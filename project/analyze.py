from itertools import permutations
from django.db.models import Max, Min, Avg, StdDev, Sum, Count
from . import models
from .queryset import Median


REQUEST_DOMAINS = [
    "category__text",
    "problem__text",
    "department__text",
    "division__text",
]

ORDER_DOMAINS = [
    "category__text",
    "problem__text",
    "department__text",
    "division__text",
    "task__text",
    "cause__text",
]

DETAIL_DOMAINS = ["task__text", "resource__text", "resource__type__text"]


def analyze(queryset, domain, range):
    r = range
    annotation_dicts = [
        {
            f"{r}_avg": Avg(r),
            f"{r}_stddev": StdDev(r),
            f"{r}_sum": Sum(r),
            f"{r}_median": Median(r),
        }
    ]

    annotations = {}
    for d in annotation_dicts:
        annotations.update(d)
    return (
        queryset.filter(**{f"{domain}__isnull": False})
        .values(domain)
        .distinct()
        .annotate(**annotations)
    )


def x():
    orders = models.WorkOrder.objects.all()
    perms = permutations(ORDER_DOMAINS)
    data = [
        list(
            analyze(
                orders,
                ORDER_DOMAINS,
                ["total_cost", "labor_cost", "material_cost", "equipment_cost"],
            ).order_by("-total_cost_count")[:10]
        ),
        list(
            analyze(
                orders,
                ORDER_DOMAINS,
                ["total_cost", "labor_cost", "material_cost", "equipment_cost"],
            ).order_by("-total_cost_sum")[:10]
        ),
    ]
    return data


# Which segments cost the most
# Which segments do we spend the most time on
# Show 5(y) most expensive orders per month.
# Show most costly causes
# Show most costly problems
# Show crew productivity per month
# Allow filtering down per department, division

# Stretch, show areas with the most requests?
