from django.contrib import admin
from .models import EstimationInput, EstimationResult

@admin.register(EstimationInput)
class EstimationInputAdmin(admin.ModelAdmin):
    list_display = ('id', 'naklad_szt', 'objetosc_m3', 'konstrukcja_kg', 'sklejka_m3', 'drewno_m3', 'plyta_m2', 'druk_m2', 'led_mb', 'tworzywa_m2', 'koszty_pozostale', 'stopien_skomplikowania', 'rodzaj_tworzywa', 'rodzaj_displaya')
    search_fields = ('rodzaj_tworzywa', 'rodzaj_displaya')
    list_filter = ('rodzaj_tworzywa', 'rodzaj_displaya')

@admin.register(EstimationResult)
class EstimationResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'estimation_input', 'estimated_price', 'created_at')
    search_fields = ('estimation_input__rodzaj_tworzywa', 'estimation_input__rodzaj_displaya')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    def estimation_input(self, obj):
        return str(obj.input_data)
    
    def estimated_price(self, obj):
        return obj.predicted_price