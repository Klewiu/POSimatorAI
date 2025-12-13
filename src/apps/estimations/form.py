from django import forms
from .models import EstimationInput

class EstimationForm(forms.ModelForm):
    user_price = forms.FloatField(required=False, label="Twoja wycena")

    class Meta:
        model = EstimationInput
        fields = ['width', 'height', 'shelves', 'material_cost']