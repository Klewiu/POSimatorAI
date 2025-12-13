from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('estimations/', include('apps.estimations.urls')),
    path('', RedirectView.as_view(url='/estimations/')),  # <-- teraz w liście
]