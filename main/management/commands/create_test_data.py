from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Project


class Command(BaseCommand):
    help = "Create test users and projects"

    def handle(self, *args, **options):
        User = get_user_model()

        users_data = [
            {"email": "user1@example.com", "name": "Иван", "surname": "Иванов"},
            {"email": "user2@example.com", "name": "Мария", "surname": "Петрова"},
            {"email": "user3@example.com", "name": "Алексей", "surname": "Сидоров"},
            {"email": "user4@example.com", "name": "Елена", "surname": "Кузнецова"},
            {"email": "user5@example.com", "name": "Дмитрий", "surname": "Васильев"},
        ]

        users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "name": user_data["name"],
                    "surname": user_data["surname"],
                    "is_active": True,
                },
            )
            if created:
                user.set_password("password123")
                user.save()
                self.stdout.write(f"Created user: {user.email}")
            else:
                self.stdout.write(f"User already exists: {user.email}")
            users.append(user)

        project_titles = [
            "Разработка веб-приложения",
            "Мобильное приложение для фитнеса",
            "ИИ для анализа данных",
            "E-commerce платформа",
            "Система управления задачами",
        ]

        for i, user in enumerate(users):
            for j in range(2):
                project_title = f"{project_titles[(i + j) % len(project_titles)]}"
                project, created = Project.objects.get_or_create(
                    name=project_title,
                    owner=user,
                    defaults={
                        "description": f"Описание проекта: {project_title}. Это тестовый проект для демонстрации функционала платформы.",
                        "status": "open" if j % 2 == 0 else "closed",
                    },
                )
                if created:
                    project.participants.add(user)
                    for k in range(1, 3):
                        other_user = users[(i + k) % len(users)]
                        project.participants.add(other_user)
                        if k == 1:
                            other_user.favorites.add(project)
                    self.stdout.write(
                        f"Created project: {project.name} for {user.email}"
                    )
                else:
                    self.stdout.write(f"Project already exists: {project.name}")

        self.stdout.write(self.style.SUCCESS("Test data creation completed!"))
