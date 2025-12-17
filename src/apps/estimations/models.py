from django.db import models

# słowniki
RODZAJ_TWORZYWA_CHOICES = [
    ('HIPS', 'HIPS'),
    ('PMMA', 'PMMA'),
    ('PET', 'PET'),
    ('PC', 'PC'),
    ('ABS', 'ABS'),
    ('NAKLEJKA', 'NAKLEJKA'),
    ('GUMA', 'GUMA'),
    ('TKANINA', 'TKANINA')
]

RODZAJ_DISPLAYA_CHOICES = [
    ('ekspozytor_pmma', 'Ekspozytor PMMA'),
    ('ekspozytor_tworzywowy', 'Ekspozytor tworzywowy'),
    ('maly_naladowy', 'Mały display naladowy'),
    ('potykacz', 'Potykacz'),
    ('regal_qpd', 'Regal QPD'),
    ('regal_hpd', 'Regal HPD'),
    ('regal_pd', 'Regal PD'),
    ('paleciak_qpd', 'Paleciak QPD'),
    ('paleciak_hpd', 'Paleciak HPD'),
    ('paleciak_pd', 'Paleciak PD'),
    ('owijka_pd', 'Owijka paletowa'),
    ('kaseton', 'Kaseton'),
    ('wyspa', 'Wyspa'),
    ('druciak', 'Druciak'),
    ('pozostale', 'Pozostałe'),  
]

class EstimationInput(models.Model):
    # NUMERIC
    naklad_szt = models.FloatField()
    objetosc_m3 = models.FloatField()
    konstrukcja_kg = models.FloatField()
    sklejka_m3 = models.FloatField()
    drewno_m3 = models.FloatField()
    plyta_m2 = models.FloatField()
    druk_m2 = models.FloatField()
    led_mb = models.FloatField()
    tworzywa_m2 = models.FloatField()
    koszty_pozostale = models.FloatField()
    stopien_skomplikowania = models.IntegerField()

    # CATEGORICAL z choices
    rodzaj_tworzywa = models.CharField(max_length=50, choices=RODZAJ_TWORZYWA_CHOICES)
    rodzaj_displaya = models.CharField(max_length=50, choices=RODZAJ_DISPLAYA_CHOICES)

class EstimationResult(models.Model):
    input_data = models.ForeignKey(EstimationInput, on_delete=models.CASCADE)
    predicted_price = models.FloatField()
    user_price = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
