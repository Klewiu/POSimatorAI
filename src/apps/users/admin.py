from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.estimations.models   import EstimationInput, EstimationResult
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Pola, które chcemy wyświetlać w liście użytkowników
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Pola w formularzu dodawania/edycji użytkownika
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )

@admin.register(EstimationInput)
class EstimationInputAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'naklad_szt', 'objetosc_m3', 'konstrukcja_kg',
        'sklejka_m3', 'drewno_m3', 'plyta_m2', 'druk_m2',
        'led_mb', 'tworzywa_m2', 'koszty_pozostale',
        'stopien_skomplikowania', 'rodzaj_tworzywa', 'rodzaj_displaya'
    )
    list_filter = ('rodzaj_tworzywa', 'rodzaj_displaya', 'stopien_skomplikowania')
    search_fields = ('rodzaj_tworzywa', 'rodzaj_displaya')
    ordering = ('-id',)
    readonly_fields = ('id',)

@admin.register(EstimationResult)
class EstimationResultAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'input_data', 'predicted_price', 'user_price', 'created_at'
    )
    list_filter = ('created_at',)
    search_fields = ('input_data__rodzaj_displaya', 'input_data__rodzaj_tworzywa')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')