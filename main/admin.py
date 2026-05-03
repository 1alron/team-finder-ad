from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

from .models import Project, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональные данные",
            {
                "fields": (
                    "name",
                    "surname",
                    "avatar",
                    "about",
                    "phone",
                    "github_url",
                    "favorites",
                )
            },
        ),
        (
            "Права",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("date_joined",)}),
    )
    list_display = ("avatar_thumbnail", "email", "name", "surname", "is_staff")
    search_fields = ("email", "name", "surname")
    ordering = ("email",)

    def avatar_thumbnail(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />',
                obj.avatar.url,
            )
        return "-"

    avatar_thumbnail.short_description = "Аватар"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "created_at", "participants_list")
    list_filter = ("status",)
    search_fields = ("name", "description", "owner__email")

    def participants_list(self, obj):
        participants = obj.participants.all()
        if not participants:
            return "-"

        participants_names = [str(user) for user in participants[:5]]
        remaining = participants.count() - len(participants_names)
        if remaining > 0:
            participants_names.append(f"+{remaining} more")
        return ", ".join(participants_names)

    participants_list.short_description = "Участники"
