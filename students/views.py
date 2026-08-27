import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q

from .models import (
    StudentProfile, Skill, Badge, StudentBadge, 
    LearningPath, Module, Progress, Recommendation, 
    ProjectSuggestion, Feedback, EduAgentReview
)
from .forms import (
    UserRegisterForm, StudentProfileForm, 
    GeneratePathForm, FeedbackForm
)
from .utils import generate_roadmap, award_badge_by_type

# --- STATIC & LANDING PAGES ---

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'students/home.html')

def about(request):
    return render(request, 'students/about.html')

def contact(request):
    if request.method == 'POST':
        messages.success(request, "Thank you for contacting us! We'll get back to you within 24 hours.")
        return redirect('contact')
    return render(request, 'students/contact.html')

# --- AUTHENTICATION ---

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a corresponding StudentProfile
            profile = StudentProfile.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}"
            )
            # Log the user in directly
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}.")
            return redirect('generate_path')
    else:
        form = UserRegisterForm()
    return render(request, 'students/register.html', {'form': form})

def calculate_learning_insights(profile, active_path, reviews):
    insights = []
    if not active_path or not reviews.exists():
        return insights
        
    latest = reviews[0]
    
    # 1. Progress Trend & 2. Consistency
    if reviews.count() >= 2:
        previous = reviews[1]
        
        # Trend
        latest_pct = int((latest.completed_tasks / latest.total_tasks) * 100) if latest.total_tasks else 0
        prev_pct = int((previous.completed_tasks / previous.total_tasks) * 100) if previous.total_tasks else 0
        if latest_pct > prev_pct:
            insights.append({
                'type': 'trend',
                'title': 'Progress Trend',
                'text': 'Your completion progress has improved since your previous review.'
            })
            
        # Consistency
        diff = latest.completed_tasks - previous.completed_tasks
        if diff > 0:
            insights.append({
                'type': 'consistency',
                'title': 'Consistency',
                'text': f"You completed {diff} task{'s' if diff > 1 else ''} since the last review."
            })
            
    # 3. Current Focus
    first_incomplete = active_path.modules.exclude(
        progress_records__student=profile, progress_records__status='Completed'
    ).order_by('week_number').first()
    if first_incomplete:
        clean_title = first_incomplete.title.replace('[ADAPTED: FOCUS] ', '').replace('[ADAPTED: ADVANCED CHALLENGE] ', '').replace('[CONFIRMED] ', '')
        insights.append({
            'type': 'focus',
            'title': 'Current Focus',
            'text': f"You are currently working on {clean_title}."
        })
        
    # 4. Learning Pace
    if "Extended remaining modules" in latest.path_adjustment or "Behind" in latest.performance_analysis or "Behind" in latest.decision:
        insights.append({
            'type': 'pace',
            'title': 'Learning Pace',
            'text': "Your current pace suggests that the remaining roadmap may need more time."
        })
        
    return insights

# --- STUDENT PORTAL / DASHBOARD ---

@login_required
def dashboard(request):
    # Get student profile
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # 1. Handle daily streak tracker
    today = timezone.localdate()
    if profile.last_active_date:
        delta = today - profile.last_active_date
        if delta.days == 1:
            profile.streak += 1
            # Check for streak badges
            if profile.streak >= 5:
                badge = award_badge_by_type(profile, 'streak_5')
                if badge:
                    messages.info(request, f"🔥 Badge Earned: {badge.name}!")
        elif delta.days > 1:
            profile.streak = 1
    else:
        profile.streak = 1
        
    profile.last_active_date = today
    profile.save()

    # 2. Get active learning path
    active_path = LearningPath.objects.filter(student=profile, is_active=True).first()
    
    modules = []
    progress_percentage = 0
    completed_modules_count = 0
    total_modules_count = 0
    upcoming_modules = []
    completed_modules = []
    
    if active_path:
        modules_query = active_path.modules.all().order_by('week_number')
        total_modules_count = modules_query.count()
        
        # Build modules with their status
        for m in modules_query:
            prog, _ = Progress.objects.get_or_create(student=profile, module=m)
            m_data = {
                'id': m.id,
                'week_number': m.week_number,
                'title': m.title,
                'description': m.description,
                'status': prog.status,
                'recommendations': m.recommendations.all()
            }
            modules.append(m_data)
            
            if prog.status == 'Completed':
                completed_modules.append(m_data)
                completed_modules_count += 1
            else:
                upcoming_modules.append(m_data)
                
        if total_modules_count > 0:
            progress_percentage = int((completed_modules_count / total_modules_count) * 100)
            
            # Check for path completion badge
            if progress_percentage == 100:
                badge = award_badge_by_type(profile, 'path_completion')
                if badge:
                    messages.success(request, f"🎓 Congratulations! You completed your pathway and earned the '{badge.name}' badge!")
    
    # Check for points badges
    if profile.points >= 500:
        badge = award_badge_by_type(profile, 'points_500')
        if badge:
            messages.info(request, f"🏆 Points milestone badge earned: {badge.name}!")

    # 3. Leaderboard data (top 5 students by points)
    leaderboard = StudentProfile.objects.exclude(user__is_superuser=True).order_by('-points')[:5]

    # 4. Badges earned
    earned_badges = StudentBadge.objects.filter(student=profile).select_related('badge')

    # 5. EduAgent review
    latest_review = None
    past_reviews = []
    insights = []
    if active_path:
        reviews = EduAgentReview.objects.filter(student=profile, learning_path=active_path).order_by('-created_at')
        latest_review = reviews.first()
        past_reviews = reviews[1:]
        insights = calculate_learning_insights(profile, active_path, reviews)

    context = {
        'profile': profile,
        'active_path': active_path,
        'modules': modules,
        'progress_percentage': progress_percentage,
        'completed_modules_count': completed_modules_count,
        'total_modules_count': total_modules_count,
        'upcoming_modules': upcoming_modules[:3],  # limit to next 3
        'leaderboard': leaderboard,
        'earned_badges': earned_badges,
        'latest_review': latest_review,
        'past_reviews': past_reviews,
        'insights': insights,
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def toggle_module_progress(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        module_id = data.get('module_id')
        new_status = data.get('status') # 'Not Started', 'In Progress', 'Completed'
        
        profile = get_object_or_404(StudentProfile, user=request.user)
        module = get_object_or_404(Module, id=module_id)
        
        progress, created = Progress.objects.get_or_create(student=profile, module=module)
        old_status = progress.status
        progress.status = new_status
        progress.save()
        
        # Adjust experience points
        points_message = ""
        badge_earned = ""
        
        if old_status != 'Completed' and new_status == 'Completed':
            profile.points += 50
            points_message = "+50 XP"
            # Award first module completion badge
            badge = award_badge_by_type(profile, 'completion_1')
            if badge:
                badge_earned = badge.name
        elif old_status == 'Completed' and new_status != 'Completed':
            profile.points = max(0, profile.points - 50)
            points_message = "-50 XP"
            
        profile.save()
        
        # Calculate new pathway completion percentage
        path = module.learning_path
        total_modules = path.modules.count()
        completed_modules = Progress.objects.filter(student=profile, module__learning_path=path, status='Completed').count()
        progress_percentage = int((completed_modules / total_modules) * 100) if total_modules > 0 else 0
        
        return JsonResponse({
            'success': True,
            'new_status': new_status,
            'points': profile.points,
            'progress_percentage': progress_percentage,
            'points_message': points_message,
            'badge_earned': badge_earned
        })
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

# --- LEARNING PATH GENERATOR ---

@login_required
def generate_path(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = GeneratePathForm(request.POST)
        if form.is_valid():
            path = generate_roadmap(profile, form.cleaned_data)
            messages.success(request, "🎉 Your personalized AI Learning Path has been generated successfully!")
            return redirect('result_detail', path_id=path.id)
    else:
        # Prepopulate with profile data if available
        initial_data = {
            'full_name': profile.full_name or f"{request.user.first_name} {request.user.last_name}",
            'education_level': profile.education_level,
            'interests': profile.interests,
            'career_target': profile.career_target or 'Full Stack Developer',
            'study_hours_per_day': profile.study_hours_per_day,
            'experience_level': profile.experience_level,
            'preferred_learning_mode': profile.learning_style,
            'current_skills': profile.skills.all()
        }
        form = GeneratePathForm(initial=initial_data)
        
    return render(request, 'students/generate_path.html', {'form': form, 'profile': profile})

@login_required
def result_detail(request, path_id):
    profile = get_object_or_404(StudentProfile, user=request.user)
    path = get_object_or_404(LearningPath, id=path_id, student=profile)
    modules = path.modules.all().order_by('week_number')
    
    # Prepare recommendations and projects
    modules_data = []
    for m in modules:
        prog, _ = Progress.objects.get_or_create(student=profile, module=m)
        modules_data.append({
            'module': m,
            'status': prog.status,
            'recommendations': m.recommendations.all()
        })
        
    projects = path.project_suggestions.all()
    
    return render(request, 'students/result.html', {
        'path': path,
        'modules_data': modules_data,
        'projects': projects,
        'profile': profile
    })

@login_required
def set_active_path(request, path_id):
    profile = get_object_or_404(StudentProfile, user=request.user)
    path = get_object_or_404(LearningPath, id=path_id, student=profile)
    
    # Deactivate all other paths
    LearningPath.objects.filter(student=profile, is_active=True).update(is_active=False)
    
    # Set this one as active
    path.is_active = True
    path.save()
    
    messages.success(request, f"'{path.title}' is now your active study plan!")
    return redirect('dashboard')

# --- OTHER SECTIONS ---

@login_required
def resources_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    active_path = LearningPath.objects.filter(student=profile, is_active=True).first()
    
    # Base query for recommendations based on student's career target or active path
    target = active_path.career_target if active_path else profile.career_target
    
    # Find recommendations linked to modules matching the career target
    recommendations = Recommendation.objects.filter(
        module__learning_path__student=profile,
        module__learning_path__is_active=True
    ).distinct()
    
    # Search and Filter
    query = request.GET.get('q', '')
    res_type = request.GET.get('type', '')
    
    if query:
        recommendations = recommendations.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if res_type:
        recommendations = recommendations.filter(resource_type=res_type)
        
    return render(request, 'students/resources.html', {
        'recommendations': recommendations,
        'query': query,
        'res_type': res_type,
        'career_target': target
    })

@login_required
def projects_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    active_path = LearningPath.objects.filter(student=profile, is_active=True).first()
    
    projects = []
    if active_path:
        projects = active_path.project_suggestions.all()
        
    return render(request, 'students/projects.html', {
        'active_path': active_path,
        'projects': projects
    })

@login_required
def feedback_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    feedbacks = Feedback.objects.filter(student=profile).order_by('-created_at')
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = profile
            feedback.save()
            messages.success(request, "Your query/feedback has been submitted successfully! An administrator will review it.")
            return redirect('feedback')
    else:
        form = FeedbackForm()
        
    return render(request, 'students/feedback.html', {
        'form': form,
        'feedbacks': feedbacks
    })

@login_required
def profile_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        form = StudentProfileForm(instance=profile)
        
    earned_badges = StudentBadge.objects.filter(student=profile).select_related('badge')
    all_badges_count = Badge.objects.count()
    
    return render(request, 'students/profile.html', {
        'form': form,
        'profile': profile,
        'earned_badges': earned_badges,
        'all_badges_count': all_badges_count
    })

# --- MOCK AI CHATBOT ---

@login_required
def chatbot_response(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '').strip().lower()
        
        profile = get_object_or_404(StudentProfile, user=request.user)
        active_path = LearningPath.objects.filter(student=profile, is_active=True).first()
        
        # Rule-based NLP assistant
        response_text = ""
        
        if "python" in user_message:
            response_text = "Python is a powerful high-level programming language used in web development, data science, and automation. If you're building websites, I recommend starting with basic syntax, then diving straight into **Django** views and templates!"
        elif "django" in user_message:
            response_text = "Django is a high-level Python web framework that follows the MVT (Model-View-Template) pattern. It has a built-in admin panel, ORM for databases, and authentication out of the box, making backend building incredibly fast!"
        elif "javascript" in user_message or "js" in user_message:
            response_text = "JavaScript is the programming language of the web. It runs client-side to add clicks, animations, and async data calls (fetch). Make sure to practice DOM manipulation and Promises before moving to **React**."
        elif "react" in user_message:
            response_text = "React is a component-based frontend UI library created by Facebook. It uses a virtual DOM to update views dynamically. Mastering state (`useState`), hooks, and props is crucial for building frontend applications."
        elif "job" in user_message or "career" in user_message or "interview" in user_message:
            response_text = "To ace your interviews, compile your mini projects into a professional portfolio. Host them on GitHub, write thorough README files, and practice coding challenges on websites like freeCodeCamp and Codewars."
        elif "stuck" in user_message or "help" in user_message or "doubt" in user_message:
            response_text = "If you're stuck on a module or have technical doubts, you can submit an official query on our **Feedback** page. Our mentors and administrators will reply to you directly!"
        elif "path" in user_message or "roadmap" in user_message:
            if active_path:
                response_text = f"You are currently working on **{active_path.title}**. It spans {active_path.duration_weeks} weeks, and you have completed {active_path.progress_percentage}% of it. Stay consistent to earn your graduation badge!"
            else:
                response_text = "You don't have an active learning path yet! Head over to the **Generate Path** page to generate a custom roadmap based on your education level and career goals."
        elif "hello" in user_message or "hi" in user_message or "hey" in user_message:
            response_text = f"Hello {profile.full_name or profile.user.username}! I am your AI Counselor. How can I help you with your learning path or coding studies today?"
        else:
            response_text = "That is a great question! For specific technical issues, I recommend checking official documentation links listed in your **Resources** tab, or posting a doubt on our **Feedback** page so our admins can assist you."
            
        return JsonResponse({
            'success': True,
            'reply': response_text
        })
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
def eduagent_review(request):
    if request.method == 'POST':
        profile = get_object_or_404(StudentProfile, user=request.user)
        active_path = LearningPath.objects.filter(student=profile, is_active=True).first()
        
        if not active_path:
            return JsonResponse({'success': False, 'error': 'Generate a learning roadmap first so EduAgent can review your progress.'}, status=400)
            
        modules = active_path.modules.all()
        total_tasks = modules.count()
        
        if total_tasks == 0:
            return JsonResponse({'success': False, 'error': 'Generate a learning roadmap first so EduAgent can review your progress.'}, status=400)
            
        # Count statuses
        completed_tasks = Progress.objects.filter(student=profile, module__in=modules, status='Completed').count()
        in_progress_tasks = Progress.objects.filter(student=profile, module__in=modules, status='In Progress').count()
        remaining_tasks = total_tasks - completed_tasks - in_progress_tasks
        
        # Determine current learning pace
        elapsed_days = (timezone.now() - active_path.created_at).days
        expected_completed = min(total_tasks, max(1, elapsed_days // 7))
        
        # Get previous review BEFORE creating a new one
        prev_review = EduAgentReview.objects.filter(student=profile, learning_path=active_path).order_by('-created_at').first()
        
        logs = []
        logs.append(f"🔍 Observe: Read current roadmap and progress: {completed_tasks} / {total_tasks} modules completed.")
        logs.append(f"🧠 Analyze: Compare current progress with available study time ({profile.study_hours_per_day} hours/day): {in_progress_tasks} in progress, {remaining_tasks} remaining.")
        
        # Determine pace and add evaluate log
        pace = "On Track"
        if completed_tasks == total_tasks:
            pace = "Completed"
            logs.append("⚖️ Evaluate: Evaluate learning pace: Pathway fully completed!")
        elif completed_tasks == 0 and in_progress_tasks == 0:
            pace = "Not Started"
            logs.append("⚖️ Evaluate: Evaluate learning pace: Learning path not yet initiated.")
        else:
            if elapsed_days == 0:
                if completed_tasks >= 1:
                    pace = "Ahead of Schedule"
                    logs.append("⚖️ Evaluate: Evaluate learning pace: Accelerated progress on Day 1.")
                else:
                    pace = "On Track"
                    logs.append("⚖️ Evaluate: Evaluate learning pace: Learning pace is normal for Day 1.")
            else:
                if completed_tasks > expected_completed:
                    pace = "Ahead of Schedule"
                    logs.append(f"⚖️ Evaluate: Evaluate learning pace: Student is moving faster than expected ({completed_tasks} completed vs {expected_completed} expected).")
                elif completed_tasks < expected_completed:
                    pace = "Behind Schedule"
                    logs.append(f"⚖️ Evaluate: Evaluate learning pace: Student is falling behind ({completed_tasks} completed vs {expected_completed} expected).")
                else:
                    pace = "On Track"
                    logs.append(f"⚖️ Evaluate: Evaluate learning pace: Progress matches expected timeline of {expected_completed} weeks.")

        # Remember log entry
        if prev_review:
            diff = completed_tasks - prev_review.completed_tasks
            if diff > 0:
                logs.append(f"💾 Remember: Compare with previous review on {prev_review.created_at.strftime('%Y-%m-%d')}. Student completed {diff} additional modules.")
            else:
                logs.append(f"💾 Remember: Compare with previous review on {prev_review.created_at.strftime('%Y-%m-%d')}. Completed tasks remain unchanged.")
        else:
            logs.append("💾 Remember: No previous reviews found. Stored initial review in memory.")

        # Find next incomplete module
        first_incomplete = active_path.modules.exclude(
            progress_records__student=profile, progress_records__status='Completed'
        ).order_by('week_number').first()
        
        next_step_title = first_incomplete.title if first_incomplete else "All modules complete"
        
        # Decide log entry
        logs.append(f"📋 Decide: Determine the appropriate next learning action: Adapt learning recommendations for '{pace}' pace.")
        logs.append(f"🚀 Recommend: Recommend the next task: Focus on '{next_step_title}'.")

        # Memory commentary variables
        memory_perf_comment = ""
        memory_rec_comment = ""
        if prev_review:
            diff = completed_tasks - prev_review.completed_tasks
            if diff > 0:
                memory_perf_comment = f" Since your last review on {prev_review.created_at.strftime('%b %d')}, you successfully completed {diff} additional module{'s' if diff > 1 else ''}. This is an excellent trend of improvement!"
                memory_rec_comment = " Keep pushing on this positive momentum."
            else:
                memory_perf_comment = f" We noticed your progress has remained flat at {completed_tasks} completed modules since your last review on {prev_review.created_at.strftime('%b %d')}. Consistency is key; try splitting large tasks into smaller daily goals."
                memory_rec_comment = " Consider spending just 15 minutes today to read the first resource of the current week to restart your progress momentum."

        # Performance analysis and adaptation
        performance_analysis = ""
        path_adjustment = ""
        recommendation = ""

        if pace == "Completed":
            performance_analysis = (
                f"Outstanding work! You have fully completed all {total_tasks} modules of your '{active_path.career_target}' roadmap. "
                "You have demonstrated extreme consistency."
            )
            path_adjustment = (
                "No adjustments needed. You have completed the curriculum!"
            )
            recommendation = (
                "Recommend applying your skills by building advanced portfolio projects, contributing to open source, "
                "or generating a new roadmap in a different technical domain."
            )
        elif pace == "Not Started":
            performance_analysis = (
                f"You have not started your study path yet. Setting up a learning habit is key."
            )
            if prev_review:
                performance_analysis += memory_perf_comment
            path_adjustment = (
                f"Let's focus on setting up a manageable study routine of {profile.study_hours_per_day} hours/day."
            )
            recommendation = (
                f"Start with Week 1 module: '{next_step_title}'. Read the first recommended resource and check it off today."
            )
            if prev_review:
                recommendation += memory_rec_comment
        elif pace == "Ahead of Schedule":
            performance_analysis = (
                f"Superb pace! You have completed {completed_tasks} modules, which is ahead of the expected {expected_completed} weeks. "
                f"You are mastering the material quickly."
            )
            if prev_review:
                performance_analysis += memory_perf_comment
            
            # Suggest advanced project or challenge
            suggested_proj = active_path.project_suggestions.order_by('-difficulty').first()
            proj_text = f"'{suggested_proj.title}'" if suggested_proj else "an advanced full-stack application"
            
            path_adjustment = (
                f"Continue with the scheduled timeline, but consider taking on the advanced project challenge: {proj_text}."
            )
            recommendation = (
                f"Move onto the next module: '{next_step_title}'. Try researching additional advanced subtopics to deepen your understanding."
            )
            if prev_review:
                recommendation += memory_rec_comment
        elif pace == "Behind Schedule":
            performance_analysis = (
                f"You have completed {completed_tasks} out of {total_tasks} modules. Based on the {elapsed_days} days elapsed since path creation, "
                f"you are slightly behind your initial timeline."
            )
            if prev_review:
                performance_analysis += memory_perf_comment
            path_adjustment = (
                f"We suggest adjusting your daily schedule. Consider spacing out modules or dedicating an extra 30 minutes "
                f"of practice per day to catch up. Focus strictly on core concepts first."
            )
            recommendation = (
                f"Focus on finishing the current incomplete module: '{next_step_title}'. "
                "Review the practical exercises and reading resources before moving forward."
            )
            if prev_review:
                recommendation += memory_rec_comment
        else: # On Track
            performance_analysis = (
                f"Great job! You are progressing exactly on track, matching the {expected_completed} weeks timeline. "
                f"Consistency is the most important factor in technical training."
            )
            if prev_review:
                performance_analysis += memory_perf_comment
            path_adjustment = (
                f"Continue the roadmap exactly as planned. Your current commitment of {profile.study_hours_per_day} hours/day is working perfectly."
            )
            recommendation = (
                f"Proceed to the next module: '{next_step_title}'. Ensure you code along with any practice/video exercises."
            )
            if prev_review:
                recommendation += memory_rec_comment

        # Save review to database
        review = EduAgentReview.objects.create(
            student=profile,
            learning_path=active_path,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            total_tasks=total_tasks,
            observed_logs=json.dumps(logs),
            performance_analysis=performance_analysis,
            path_adjustment=path_adjustment,
            decision=path_adjustment,
            recommendation=recommendation
        )
        
        # Calculate updated insights and history to return in JSON
        reviews = EduAgentReview.objects.filter(student=profile, learning_path=active_path).order_by('-created_at')
        past_reviews_list = []
        for r in reviews[1:]:
            past_reviews_list.append({
                'created_at': r.created_at.strftime('%b %d, %Y at %H:%M'),
                'completed_tasks': r.completed_tasks,
                'total_tasks': r.total_tasks,
                'decision': r.decision,
                'recommendation': r.recommendation
            })
            
        insights_list = calculate_learning_insights(profile, active_path, reviews)
        
        return JsonResponse({
            'success': True,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks,
            'performance_analysis': performance_analysis,
            'decision': path_adjustment,
            'path_adjustment': path_adjustment,
            'recommendation': recommendation,
            'logs': logs,
            'past_reviews': past_reviews_list,
            'insights': insights_list
        })
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@login_required
def eduagent_adapt(request):
    if request.method == 'POST':
        import json
        profile = get_object_or_404(StudentProfile, user=request.user)
        active_path = LearningPath.objects.filter(student=profile, is_active=True).first()
        
        if not active_path:
            return JsonResponse({'success': False, 'error': 'Generate a learning roadmap first so EduAgent can review your progress.'}, status=400)
            
        latest_review = EduAgentReview.objects.filter(student=profile, learning_path=active_path).order_by('-created_at').first()
        if not latest_review:
            return JsonResponse({'success': False, 'error': 'Please ask EduAgent to review your progress first so it has the analysis data needed to adapt your path.'}, status=400)
            
        # Get modules
        all_modules = active_path.modules.all().order_by('week_number')
        completed_modules_ids = Progress.objects.filter(
            student=profile, module__in=all_modules, status='Completed'
        ).values_list('module_id', flat=True)
        
        remaining_modules = all_modules.exclude(id__in=completed_modules_ids)
        
        if not remaining_modules.exists():
            return JsonResponse({
                'success': True,
                'what_changed': "No changes made.",
                'why': "You have already completed all modules in this roadmap!",
                'next_step': "All modules complete. Consider generating a new roadmap!"
            })
            
        completed_count = len(completed_modules_ids)
        total_count = all_modules.count()
        elapsed_days = (timezone.now() - active_path.created_at).days
        expected_completed = min(total_count, max(1, elapsed_days // 7))
        
        # Decide adaptation category
        pace = "On Track"
        if completed_count == total_count:
            pace = "Completed"
        elif completed_count == 0:
            # Check if user has items in progress
            in_progress_count = Progress.objects.filter(student=profile, module__in=all_modules, status='In Progress').count()
            if in_progress_count == 0:
                pace = "Not Started"
            else:
                pace = "Behind Schedule"
        else:
            if elapsed_days > 0:
                if completed_count > expected_completed:
                    pace = "Ahead of Schedule"
                elif completed_count < expected_completed:
                    pace = "Behind Schedule"
                    
        what_changed = ""
        why = ""
        next_step_title = ""
        
        if pace == "Behind Schedule":
            # Action: Reduce weekly load, focus on fundamentals, space out modules
            why = f"You are currently running behind schedule ({completed_count} completed vs {expected_completed} expected in {elapsed_days} days). EduAgent has adjusted remaining work to prevent burnout."
            
            start_week = remaining_modules.first().week_number
            updated_weeks = []
            
            for idx, m in enumerate(remaining_modules):
                new_week = start_week + idx * 2 # Space them every 2 weeks
                m.week_number = new_week
                m.order = new_week
                
                # Adapt title/desc
                clean_title = m.title.replace('[ADAPTED: ADVANCED CHALLENGE] ', '').replace('[ADAPTED: FOCUS] ', '').replace('[CONFIRMED] ', '')
                m.title = f"[ADAPTED: FOCUS] {clean_title}"
                
                clean_desc = m.description.replace('Essential Core Only: Focus on main tools and syntax. Skip heavy theoretical details. ', '').replace('Advanced Deep-Dive: Apply architectural design, performance tuning, and build custom projects. ', '')
                m.description = f"Essential Core Only: Focus on main tools and syntax. Skip heavy theoretical details. {clean_desc}"
                m.save()
                updated_weeks.append(new_week)
                
            max_week = max(updated_weeks) if updated_weeks else active_path.duration_weeks
            active_path.duration_weeks = max_week
            active_path.save()
            
            what_changed = f"Extended remaining modules to space out every 2 weeks (Week {', '.join(map(str, updated_weeks))}). Refocused curriculum titles and descriptions to emphasize core fundamentals only."
            next_step_title = remaining_modules.first().title
            
        elif pace == "Ahead of Schedule":
            # Action: Compress remaining timeline, add advanced tasks
            why = f"You are progressing ahead of schedule ({completed_count} completed vs {expected_completed} expected). EduAgent has compressed remaining timeline and added advanced tasks."
            
            start_week = remaining_modules.first().week_number
            updated_weeks = []
            
            for idx, m in enumerate(remaining_modules):
                new_week = start_week + idx
                m.week_number = new_week
                m.order = new_week
                
                clean_title = m.title.replace('[ADAPTED: FOCUS] ', '').replace('[ADAPTED: ADVANCED CHALLENGE] ', '').replace('[CONFIRMED] ', '')
                m.title = f"[ADAPTED: ADVANCED CHALLENGE] {clean_title}"
                
                clean_desc = m.description.replace('Essential Core Only: Focus on main tools and syntax. Skip heavy theoretical details. ', '').replace('Advanced Deep-Dive: Apply architectural design, performance tuning, and build custom projects. ', '')
                m.description = f"Advanced Deep-Dive: Apply architectural design, performance tuning, and build custom projects. {clean_desc}"
                m.save()
                updated_weeks.append(new_week)
                
            max_week = max(updated_weeks) if updated_weeks else active_path.duration_weeks
            active_path.duration_weeks = max_week
            active_path.save()
            
            what_changed = "Merged and compressed remaining module timelines. Injected '[ADAPTED: ADVANCED CHALLENGE]' deep-dive guidelines and custom project benchmarks into descriptions."
            next_step_title = remaining_modules.first().title
            
        else: # On Track or Not Started
            why = "You are currently proceeding on track with your roadmap. EduAgent validated your timeline."
            
            for m in remaining_modules:
                clean_title = m.title.replace('[ADAPTED: FOCUS] ', '').replace('[ADAPTED: ADVANCED CHALLENGE] ', '').replace('[CONFIRMED] ', '')
                m.title = f"[CONFIRMED] {clean_title}"
                m.save()
            
            what_changed = "Validated existing roadmap timeline and verified sequence order. Prefixed future modules with '[CONFIRMED]' to reinforce your current curriculum pace."
            next_step_title = remaining_modules.first().title

        # Update the latest review to reflect the adaptation action taken
        try:
            logs = json.loads(latest_review.observed_logs)
        except Exception:
            logs = []
        logs.append(f"🔄 Adapted pathway: {what_changed}")
        latest_review.observed_logs = json.dumps(logs)
        latest_review.path_adjustment = f"Adapted path: {what_changed}"
        latest_review.save()
        
        return JsonResponse({
            'success': True,
            'what_changed': what_changed,
            'why': why,
            'next_step': next_step_title
        })
        
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


