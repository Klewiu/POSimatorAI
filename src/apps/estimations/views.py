from django.views.generic.edit import FormView
from .form import EstimationForm
from .models import EstimationInput, EstimationResult
from ml.predict import predict_price
from django.views.generic import TemplateView

class EstimationView(FormView):
    template_name = "estimations/form.html"
    form_class = EstimationForm
    success_url = "/estimations/result/"

    def form_valid(self, form):
        input_data = form.save()
        predicted = predict_price([
            input_data.width,
            input_data.height,
            input_data.shelves,
            input_data.material_cost
        ])
        EstimationResult.objects.create(
            input_data=input_data,
            predicted_price=predicted,
            user_price=form.cleaned_data.get('user_price')
        )
        self.request.session['predicted'] = predicted
        self.request.session['user_price'] = form.cleaned_data.get('user_price')
        return super().form_valid(form)



class EstimationResultView(TemplateView):
    template_name = "estimations/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['predicted'] = self.request.session.get('predicted')
        context['user_price'] = self.request.session.get('user_price')
        return context