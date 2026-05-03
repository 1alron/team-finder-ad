from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/list", views.project_list, name="project_list"),
    path("projects/favorites", views.favorite_projects, name="favorite_projects"),
    path("projects/create-project", views.project_create, name="project_create"),
    path("projects/<int:project_id>", views.project_detail, name="project_detail"),
    path("projects/<int:project_id>/edit", views.project_edit, name="project_edit"),
    path(
        "projects/<int:project_id>/complete/",
        views.complete_project,
        name="project_complete",
    ),
    path(
        "projects/<int:project_id>/toggle-favorite/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),
    path(
        "projects/<int:project_id>/toggle-participate/",
        views.toggle_participate,
        name="toggle_participate",
    ),
    path("users/list", views.users_list, name="users_list"),
    path("users/register/", views.register_view, name="register"),
    path("users/login/", views.login_view, name="login"),
    path("users/logout/", views.logout_view, name="logout"),
    path("users/<int:user_id>/", views.user_details, name="user_details"),
    path("users/edit-profile/", views.edit_profile, name="edit_profile"),
    path("users/change-password/", views.change_password, name="change_password"),
]
