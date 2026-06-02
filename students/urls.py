from django.urls import path
from . import views

urlpatterns = [
    # Landing & General Static Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Registration
    path('register/', views.register, name='register'),
    
    # Core Student Portal
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate/', views.generate_path, name='generate_path'),
    path('result/<int:path_id>/', views.result_detail, name='result_detail'),
    path('result/<int:path_id>/activate/', views.set_active_path, name='set_active_path'),
    
    # Features Pages
    path('resources/', views.resources_view, name='resources'),
    path('projects/', views.projects_view, name='projects'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('profile/', views.profile_view, name='profile'),
    
    # AJAX / API Endpoints
    path('api/toggle-module-progress/', views.toggle_module_progress, name='toggle_module_progress'),
    path('api/chatbot/', views.chatbot_response, name='chatbot_response'),
]
