from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .form import EstimationForm
from .models import EstimationInput
from ml.predict import predict_price
from django.views.generic import TemplateView

class EstimationView(LoginRequiredMixin, FormView):
    template_name = "estimations/form.html"
    form_class = EstimationForm
    success_url = "/estimations/result/"

    def form_valid(self, form):
        input_data = form.save()

        # przygotowanie danych do predykcji
        predicted = predict_price([
            input_data.naklad_szt,
            input_data.objetosc_m3,
            input_data.konstrukcja_kg,
            input_data.sklejka_m3,
            input_data.drewno_m3,
            input_data.plyta_m2,
            input_data.druk_m2,
            input_data.led_mb,
            input_data.tworzywa_m2,
            input_data.koszty_pozostale,
            input_data.stopien_skomplikowania,
            input_data.rodzaj_tworzywa,
            input_data.rodzaj_displaya,
        ])

        user_price = form.cleaned_data.get('user_price')

        self.request.session['predicted'] = float(predicted)
        self.request.session['user_price'] = float(user_price) if user_price is not None else None
        return super().form_valid(form)


class EstimationResultView(LoginRequiredMixin, TemplateView):
    template_name = "estimations/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['predicted'] = self.request.session.get('predicted')
        context['user_price'] = self.request.session.get('user_price')
        return context
