from django.urls import path
from .views import EstimationView, EstimationResultView

urlpatterns = [
    path('', EstimationView.as_view(), name='estimation-form'),
    path('result/', EstimationResultView.as_view(), name='estimation-result'),
]