import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_learning_path.settings')
django.setup()

from django.contrib.auth.models import User
from students.models import Skill, Badge

# 1. Create Default Skills
skills = [
    'Python', 'HTML', 'CSS', 'JavaScript', 'Django', 'React', 'SQL', 
    'Git', 'Docker', 'Pandas', 'Machine Learning', 'Linux', 'Cryptography', 'Flutter'
]

print("Seeding Skills...")
for s_name in skills:
    skill, created = Skill.objects.get_or_create(name=s_name, defaults={'description': f'Essential skill: {s_name}'})
    if created:
        print(f"Created skill: {s_name}")

# 2. Create Default Badges
badges_data = [
    {
        'name': 'The Journey Begins',
        'description': 'Created your first personalized learning roadmap.',
        'badge_type': 'path_creation',
        'icon': 'fa-solid fa-compass'
    },
    {
        'name': 'Consistency Champ',
        'description': 'Achieved a daily streak of 5 days.',
        'badge_type': 'streak_5',
        'icon': 'fa-solid fa-fire'
    },
    {
        'name': 'First Milestone',
        'description': 'Completed your first weekly learning module.',
        'badge_type': 'completion_1',
        'icon': 'fa-solid fa-circle-check'
    },
    {
        'name': 'Career Architect',
        'description': 'Successfully completed 100% of an active learning path.',
        'badge_type': 'path_completion',
        'icon': 'fa-solid fa-graduation-cap'
    },
    {
        'name': 'Knowledge Collector',
        'description': 'Earned a total of 500 experience points.',
        'badge_type': 'points_500',
        'icon': 'fa-solid fa-trophy'
    }
]

print("\nSeeding Badges...")
for b in badges_data:
    badge, created = Badge.objects.get_or_create(
        name=b['name'],
        defaults={'description': b['description'], 'badge_type': b['badge_type'], 'icon': b['icon']}
    )
    if created:
        print(f"Created badge: {b['name']}")

# 3. Create Superuser
print("\nCreating default superuser...")
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created successfully: username='admin', password='admin123'")
else:
    print("Superuser 'admin' already exists.")

print("\nSeeding process completed!")
