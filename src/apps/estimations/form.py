from django import forms
from .models import EstimationInput

class EstimationForm(forms.ModelForm):
    user_price = forms.DecimalField(
        required=False,
        label="Twoja wycena",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = EstimationInput
        fields = ["width", "height", "shelves", "material_cost"]

        widgets = {
            "width": forms.NumberInput(attrs={"class": "form-control"}),
            "height": forms.NumberInput(attrs={"class": "form-control"}),
            "shelves": forms.NumberInput(attrs={"class": "form-control"}),
            "material_cost": forms.NumberInput(attrs={"class": "form-control"}),
        }
