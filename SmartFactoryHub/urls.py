from django.contrib import admin
from django.urls import path, include
from sensor.routing import websocket_urlpatterns
from sensor.views import sensor_data_view, sensor_dashboard,sensors_data_view,sensor_log_view
from auth_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "ws/", include(websocket_urlpatterns)
    ),  # Assurez-vous que cette ligne est présente
    path('sensor/', include('sensor.urls')),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("accueil/", views.accueil, name="accueil"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
]
