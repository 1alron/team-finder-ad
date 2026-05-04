from http import HTTPStatus

from django.contrib.auth import (authenticate, get_user_model, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from main.constants import PROJECTS_PER_PAGE, USERS_PER_PAGE
from main.forms import LoginForm, ProfileForm, ProjectForm, RegisterForm
from main.models import Project, User
from main.service import get_project_queryset, paginate_queryset


def index(request):
    return redirect("users:project_list")


def project_list(request):
    projects = get_project_queryset().all()
    projects_page = paginate_queryset(request, projects, PROJECTS_PER_PAGE)
    return render(request, "projects/project_list.html", {"projects": projects_page})


@login_required
def favorite_projects(request):
    favorites = request.user.favorites.values_list("pk", flat=True)
    projects = get_project_queryset().filter(pk__in=favorites)
    projects_page = paginate_queryset(request, projects, PROJECTS_PER_PAGE)
    return render(
        request, "projects/favorite_projects.html", {"projects": projects_page}
    )


def project_detail(request, project_id):
    project = get_object_or_404(get_project_queryset(), pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("users:project_detail", project_id=project.id)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("users:project_detail", project_id=project.id)
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse(
            {"status": "forbidden"}, status=int(HTTPStatus.FORBIDDEN)
        )
    project.status = Project.STATUS_CLOSED
    project.save()
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    is_favorite = request.user.favorites.filter(pk=project_id).exists()
    if is_favorite:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)
    return JsonResponse({"status": "ok", "favorite": not is_favorite})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    participant = project.participants.filter(pk=request.user.pk).exists()
    if participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": not participant})


def users_list(request):
    UserModel = get_user_model()
    active_filter = request.GET.get("filter")
    users = UserModel.objects.order_by("-date_joined")
    if request.user.is_authenticated and active_filter:
        filter_map = {
            "owners-of-favorite-projects": UserModel.objects.filter(
                owned_projects__in=request.user.favorites.all()
            ),
            "owners-of-participating-projects": UserModel.objects.filter(
                owned_projects__participants=request.user
            ),
            "interested-in-my-projects": UserModel.objects.filter(
                favorites__owner=request.user
            ),
            "participants-of-my-projects": UserModel.objects.filter(
                participating_projects__owner=request.user
            ),
        }
        users = filter_map.get(active_filter, users).order_by("-date_joined").distinct()
    participants = paginate_queryset(request, users, USERS_PER_PAGE)
    return render(
        request,
        "users/participants.html",
        {"participants": participants, "active_filter": active_filter},
    )


def user_details(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, "users/user-details.html", {"user": user})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("users:user_details", user_id=request.user.id)
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("users:user_details", user_id=user.id)
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("users:user_details", user_id=request.user.id)
    form = LoginForm(request.POST or None)
    if form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("users:user_details", user_id=request.user.id)
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("users:project_list")


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect("users:user_details", user_id=request.user.id)
    return render(
        request, "users/edit_profile.html", {"form": form, "user": request.user}
    )


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:user_details", user_id=request.user.id)
    return render(request, "users/change_password.html", {"form": form})
