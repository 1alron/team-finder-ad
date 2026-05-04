from django.core.paginator import Paginator

from main.models import Project


def paginate_queryset(request, queryset, per_page, page_param="page"):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get(page_param)
    return paginator.get_page(page)


def get_project_queryset():
    return Project.objects.select_related("owner").prefetch_related("participants")
