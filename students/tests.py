from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import StudentProfile, Skill, Badge, LearningPath, Module, Progress, StudentBadge
from .utils import generate_roadmap, award_badge_by_type

class StudentPortalTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='teststudent',
            password='testpassword',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create StudentProfile (usually created automatically in view, let's create here for tests)
        self.profile = StudentProfile.objects.create(
            user=self.user,
            full_name="Test User"
        )
        
        # Create preset skills
        self.python_skill = Skill.objects.create(name='Python', description='Python Language')
        self.django_skill = Skill.objects.create(name='Django', description='Django Framework')
        
        # Create badge
        self.badge = Badge.objects.create(
            name='The Journey Begins',
            description='Created your first path.',
            badge_type='path_creation',
            icon='fa-compass'
        )
        
        self.client = Client()

    def test_profile_creation(self):
        """Test profile fields link correctly."""
        self.assertEqual(self.profile.user.username, 'teststudent')
        self.assertEqual(self.profile.points, 0)
        self.assertEqual(self.profile.streak, 0)

    def test_dynamic_roadmap_generation_duration(self):
        """Test that study hours per day correctly dynamically adjust path duration weeks."""
        # 1. Budget < 2 hours should yield 8 weeks
        data_8_weeks = {
            'full_name': 'Test User',
            'education_level': 'CS Graduate',
            'career_target': 'Full Stack Developer',
            'experience_level': 'Beginner',
            'preferred_learning_mode': 'Mixed',
            'study_hours_per_day': 1.0,
            'current_skills': [self.python_skill.id]
        }
        path_8 = generate_roadmap(self.profile, data_8_weeks)
        self.assertEqual(path_8.duration_weeks, 8)
        self.assertEqual(path_8.modules.count(), 8)

        # 2. Budget >= 2 and < 4 hours should yield 6 weeks
        data_6_weeks = {
            'full_name': 'Test User',
            'education_level': 'CS Graduate',
            'career_target': 'Full Stack Developer',
            'experience_level': 'Intermediate',
            'preferred_learning_mode': 'Video',
            'study_hours_per_day': 3.0,
            'current_skills': []
        }
        path_6 = generate_roadmap(self.profile, data_6_weeks)
        self.assertEqual(path_6.duration_weeks, 6)
        self.assertEqual(path_6.modules.count(), 6)

        # 3. Budget >= 4 hours should yield 4 weeks
        data_4_weeks = {
            'full_name': 'Test User',
            'education_level': 'CS Graduate',
            'career_target': 'Full Stack Developer',
            'experience_level': 'Advanced',
            'preferred_learning_mode': 'Practice',
            'study_hours_per_day': 5.0,
            'current_skills': []
        }
        path_4 = generate_roadmap(self.profile, data_4_weeks)
        self.assertEqual(path_4.duration_weeks, 4)
        self.assertEqual(path_4.modules.count(), 4)

    def test_badge_awarded(self):
        """Test logic for awarding badges to students."""
        badge = award_badge_by_type(self.profile, 'path_creation')
        self.assertIsNotNone(badge)
        self.assertEqual(badge.name, 'The Journey Begins')
        self.assertTrue(StudentBadge.objects.filter(student=self.profile, badge=badge).exists())
        self.assertEqual(self.profile.points, 50) # Award points on badge unlock

    def test_views_require_login(self):
        """Test auth protection on dashboard."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_dashboard_authenticated(self):
        """Test dashboard access after authenticating."""
        self.client.login(username='teststudent', password='testpassword')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome, Test User!")
