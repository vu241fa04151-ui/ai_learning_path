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
    ProjectSuggestion, Feedback
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
