from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    badge_type = models.CharField(max_length=50)  # e.g., 'path_completion', 'streak', 'points'
    icon = models.CharField(max_length=100, default='fa-medal')  # FontAwesome icon class name

    def __str__(self):
        return self.name

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    skills = models.ManyToManyField(Skill, blank=True, related_name='students')
    interests = models.TextField(blank=True)
    career_target = models.CharField(max_length=100, blank=True)
    study_hours_per_day = models.DecimalField(max_digits=4, decimal_places=1, default=2.0)
    experience_level = models.CharField(
        max_length=50,
        choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')],
        default='Beginner'
    )
    learning_style = models.CharField(
        max_length=50,
        choices=[('Video', 'Video'), ('Reading', 'Reading'), ('Practice', 'Practice'), ('Mixed', 'Mixed')],
        default='Mixed'
    )
    streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    points = models.IntegerField(default=0)
    avatar = models.CharField(max_length=50, default='default_avatar.png')

    def __str__(self):
        return self.user.username

class StudentBadge(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'badge')

    def __str__(self):
        return f"{self.student.user.username} - {self.badge.name}"

class LearningPath(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='learning_paths')
    title = models.CharField(max_length=200)
    career_target = models.CharField(max_length=100)
    duration_weeks = models.IntegerField(default=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.student.user.username})"

    @property
    def progress_percentage(self):
        modules = self.modules.all()
        if not modules.exists():
            return 0
        
        # Check through the Progress records or individual modules status
        # Since we synchronize Progress records, we count Completed statuses in progress records
        completed_count = Progress.objects.filter(student=self.student, module__in=modules, status='Completed').count()
        return int((completed_count / modules.count()) * 100)

class Module(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='modules')
    week_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"

class Progress(models.Model):
    STATUS_CHOICES = [
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='progress_records')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress_records')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'module')
        verbose_name_plural = 'Progresses'

    def __str__(self):
        return f"{self.student.user.username} - {self.module.title} - {self.status}"

class Recommendation(models.Model):
    TYPE_CHOICES = [
        ('Video', 'Video'),
        ('Reading', 'Reading'),
        ('Practice', 'Practice'),
        ('Course', 'Course'),
        ('Blog', 'Blog'),
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='recommendations')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    url = models.URLField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"[{self.resource_type}] {self.title}"

class ProjectSuggestion(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='project_suggestions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=50)  # Beginner, Intermediate, Advanced
    milestones = models.TextField(blank=True)  # Markdown list of milestones
    technologies = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    TYPE_CHOICES = [
        ('Feedback', 'Feedback'),
        ('Doubt', 'Doubt'),
        ('Suggestion', 'Suggestion'),
    ]
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    admin_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.feedback_type} by {self.student.user.username} at {self.created_at.strftime('%Y-%m-%d')}"
