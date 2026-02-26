from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.submits.models import Submission
from apps.users.views import AdminRequiredMixin


class ReportChartView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = "reports/chart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submissions = Submission.objects.select_related("user").filter(
            user_price__isnull=False
        ).order_by("created_at")

        labels = []
        user_prices = []
        predicted_prices = []
        residuals = []

        for sub in submissions:
            labels.append(f"#{sub.pk}")
            user_prices.append(round(sub.user_price, 2))
            predicted_prices.append(round(sub.predicted_price, 2))
            residuals.append(round(sub.user_price - sub.predicted_price, 2))

        context["labels"] = labels
        context["user_prices"] = user_prices
        context["predicted_prices"] = predicted_prices
        context["residuals"] = residuals
        return context
