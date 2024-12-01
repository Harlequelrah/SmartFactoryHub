from django.contrib import admin
from django.urls import path, include
from sensor.routing import websocket_urlpatterns
from sensor.views import sensor_data_view,sensors_data_view
from auth_app import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "ws/", include(websocket_urlpatterns)
    ),  # Assurez-vous que cette ligne est présente
    path("sensor_data/", sensor_data_view, name="sensor_data"),
    path("sensors_data/", sensors_data_view, name="sensors_data"),
    path("", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("accueil/", views.accueil, name="accueil"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
]
