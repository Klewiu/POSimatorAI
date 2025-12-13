from django.db import models

class EstimationInput(models.Model):
    width = models.FloatField()
    height = models.FloatField()
    shelves = models.IntegerField()
    material_cost = models.FloatField()

class EstimationResult(models.Model):
    input_data = models.ForeignKey(EstimationInput, on_delete=models.CASCADE)
    predicted_price = models.FloatField()
    user_price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)