import json

from django.contrib.auth import (authenticate, get_user_model, login, logout,
                                 update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfileForm, ProjectForm, RegisterForm
from .models import Project, User


def index(request):
    return redirect("/projects/list")


def project_list(request):
    projects = Project.objects.select_related("owner").all()
    paginator = Paginator(projects, 12)
    page = request.GET.get("page")
    projects_page = paginator.get_page(page)
    return render(request, "projects/project_list.html", {"projects": projects_page})


@login_required
def favorite_projects(request):
    projects = request.user.favorites.select_related("owner").all()
    paginator = Paginator(projects, 12)
    page = request.GET.get("page")
    projects_page = paginator.get_page(page)
    return render(
        request, "projects/favorite_projects.html", {"projects": projects_page}
    )


def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_create(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect(f"/projects/{project.id}")
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": False}
    )


@login_required
def project_edit(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return HttpResponseForbidden()
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"/projects/{project.id}")
    return render(
        request, "projects/create-project.html", {"form": form, "is_edit": True}
    )


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user and not request.user.is_staff:
        return JsonResponse({"status": "forbidden"}, status=403)
    project.status = Project.STATUS_CLOSED
    project.save()
    return JsonResponse({"status": "ok"})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user.favorites.filter(pk=project_id).exists():
        request.user.favorites.remove(project)
        is_favorite = False
    else:
        request.user.favorites.add(project)
        is_favorite = True
    return JsonResponse({"status": "ok", "favorite": is_favorite})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})


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
    paginator = Paginator(users, 12)
    page = request.GET.get("page")
    participants = paginator.get_page(page)
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
        return redirect(f"/users/{request.user.id}")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(f"/users/{user.id}")
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect(f"/users/{request.user.id}")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect(f"/users/{request.user.id}")
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("/projects/list")


@login_required
def edit_profile(request):
    form = ProfileForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect(f"/users/{request.user.id}")
    return render(
        request, "users/edit_profile.html", {"form": form, "user": request.user}
    )


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect(f"/users/{request.user.id}")
    return render(request, "users/change_password.html", {"form": form})
