import random
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from . import models
from .analyze import analyze


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "departments": models.Department.objects.filter(
                    work_orders__isnull=False
                )
                .distinct()
                .order_by("text"),
                "divisions": models.Division.objects.filter(work_orders__isnull=False)
                .distinct()
                .order_by("text"),
                "categories": models.Category.objects.filter(work_orders__isnull=False)
                .distinct()
                .order_by("text"),
            }
        )
        return context


def random_color():
    return "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])


def chart_data(request):
    dept = (
        None
        if not request.GET.get("department")
        else get_object_or_404(models.Department, code=request.GET["department"])
    )
    div = (
        None
        if not request.GET.get("division")
        else get_object_or_404(models.Division, code=request.GET["division"])
    )
    cat = (
        None
        if not request.GET.get("category")
        else get_object_or_404(models.Category, code=request.GET["category"])
    )
    limit = int(request.GET["limit"])
    domain = request.GET["domain"]
    range = request.GET["range"]
    value = request.GET["value"]

    queryset = models.WorkOrder.objects.all()
    if dept:
        queryset = queryset.filter(department=dept)
    if div:
        queryset = queryset.filter(division=div)
    if cat:
        queryset = queryset.filter(category=cat)
    data = list(
        analyze(queryset, domain=domain, range=range).order_by(f"-{range}_{value}")[
            :limit
        ]
    )
    labels = [d[domain] for d in data]
    series = [d[f"{range}_{value}"] for d in data]
    colors = []
    while len(colors) < len(series):
        new_color = random_color()
        if new_color in colors:
            continue
        colors.append(new_color)
    data = {
        "labels": labels,
        "datasets": [
            {
                "label": range.replace("_", " ").capitalize(),
                "data": series,
                "backgroundColor": colors,
            }
        ],
    }
    return JsonResponse({"chart": {"data": data}})
