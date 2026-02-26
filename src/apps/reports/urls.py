from django.urls import path

from .views import ReportChartView

urlpatterns = [
    path("", ReportChartView.as_view(), name="reports-chart"),
]
