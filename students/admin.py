from django.contrib import admin
from .models import (
    Skill, Badge, StudentProfile, StudentBadge, 
    LearningPath, Module, Progress, Recommendation, 
    ProjectSuggestion, Feedback
)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'description', 'icon')
    list_filter = ('badge_type',)
    search_fields = ('name',)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'career_target', 'streak', 'points', 'last_active_date')
    list_filter = ('experience_level', 'learning_style', 'career_target')
    search_fields = ('user__username', 'full_name', 'career_target')

@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ('student', 'badge', 'earned_at')
    list_filter = ('badge',)
    search_fields = ('student__user__username', 'badge__name')

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'career_target', 'duration_weeks', 'is_active', 'created_at')
    list_filter = ('career_target', 'is_active', 'duration_weeks')
    search_fields = ('student__user__username', 'title')
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('learning_path', 'week_number', 'title', 'order')
    list_filter = ('learning_path__career_target', 'week_number')
    search_fields = ('title', 'description', 'learning_path__title')

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'module', 'status', 'updated_at')
    list_filter = ('status', 'updated_at')
    search_fields = ('student__user__username', 'module__title')

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('module', 'title', 'resource_type', 'url')
    list_filter = ('resource_type',)
    search_fields = ('title', 'description', 'module__title')

@admin.register(ProjectSuggestion)
class ProjectSuggestionAdmin(admin.ModelAdmin):
    list_display = ('learning_path', 'title', 'difficulty', 'technologies')
    list_filter = ('difficulty', 'learning_path__career_target')
    search_fields = ('title', 'description', 'technologies')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'feedback_type', 'created_at', 'has_response')
    list_filter = ('feedback_type', 'created_at')
    search_fields = ('student__user__username', 'message', 'admin_response')
    readonly_fields = ('created_at',)
    
    def has_response(self, obj):
        return bool(obj.admin_response)
    has_response.boolean = True
    has_response.short_description = 'Replied?'
