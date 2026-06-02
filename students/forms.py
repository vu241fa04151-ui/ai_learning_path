from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import StudentProfile, Skill, Feedback

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

class StudentProfileForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = StudentProfile
        fields = [
            'full_name', 'education_level', 'skills', 'interests', 
            'career_target', 'study_hours_per_day', 'experience_level', 
            'learning_style', 'avatar'
        ]
        widgets = {
            'interests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g. Web Dev, Machine Learning, UI/UX'}),
            'avatar': forms.Select(choices=[
                ('avatar_1.png', 'Tech Pioneer'),
                ('avatar_2.png', 'Data Specialist'),
                ('avatar_3.png', 'Creative Designer'),
                ('avatar_4.png', 'Code Warrior'),
                ('avatar_5.png', 'Curious Learner')
            ])
        }

class GeneratePathForm(forms.Form):
    CAREER_CHOICES = [
        ('Full Stack Developer', 'Full Stack Developer'),
        ('Frontend Developer', 'Frontend Developer'),
        ('Backend Developer', 'Backend Developer'),
        ('Data Scientist', 'Data Scientist'),
        ('Machine Learning Engineer', 'Machine Learning Engineer'),
        ('Mobile App Developer', 'Mobile Developer'),
        ('DevOps Engineer', 'DevOps Engineer'),
        ('Cybersecurity Specialist', 'Cybersecurity Specialist'),
    ]
    
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]
    
    MODE_CHOICES = [
        ('Video', 'Video Tutorials'),
        ('Reading', 'Documentation & Blogs'),
        ('Practice', 'Hands-on Coding Projects'),
        ('Mixed', 'Balanced Mix of All'),
    ]

    full_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter your full name'}))
    education_level = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'e.g. Bachelor\'s in CS, High School, Self-taught'}))
    current_skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select skills you already know to bypass basic weeks."
    )
    new_skills_text = forms.CharField(
        max_length=255, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Or type other skills separated by commas'}),
        help_text="If your skills are not in the list, type them here."
    )
    interests = forms.CharField(widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g. Artificial Intelligence, Cryptography, Mobile Gaming'}), required=False)
    career_target = forms.ChoiceField(choices=CAREER_CHOICES, required=True)
    study_hours_per_day = forms.DecimalField(max_digits=4, decimal_places=1, initial=2.0, widget=forms.NumberInput(attrs={'min': 0.5, 'max': 24.0, 'step': 0.5}))
    experience_level = forms.ChoiceField(choices=LEVEL_CHOICES, initial='Beginner')
    preferred_learning_mode = forms.ChoiceField(choices=MODE_CHOICES, initial='Mixed')

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_type', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your feedback, doubt, or suggestion here...'})
        }
