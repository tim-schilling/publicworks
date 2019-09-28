from django.urls import path
from . import views

app_name = "project"
urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("data/", views.chart_data, name="chart_data"),
]
