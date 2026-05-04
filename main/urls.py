from django.urls import include, path

from . import views

app_name = "users"

projects_urls = [
    path("list", views.project_list, name="project_list"),
    path("favorites", views.favorite_projects, name="favorite_projects"),
    path("create-project", views.project_create, name="project_create"),
    path("<int:project_id>", views.project_detail, name="project_detail"),
    path("<int:project_id>/edit", views.project_edit, name="project_edit"),
    path(
        "<int:project_id>/complete/",
        views.complete_project,
        name="project_complete",
    ),
    path(
        "<int:project_id>/toggle-favorite/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),
    path(
        "<int:project_id>/toggle-participate/",
        views.toggle_participate,
        name="toggle_participate",
    ),
]

users_urls = [
    path("list", views.users_list, name="users_list"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("<int:user_id>/", views.user_details, name="user_details"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("change-password/", views.change_password, name="change_password"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("projects/", include(projects_urls)),
    path("users/", include(users_urls)),
]
