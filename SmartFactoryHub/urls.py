from django.contrib import admin
from django.urls import path, include
from sensor.routing import websocket_urlpatterns
from sensor.views import sensor_data_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "ws/", include(websocket_urlpatterns)
    ),  # Assurez-vous que cette ligne est présente

    path('sensor_data/', sensor_data_view, name='sensor_data'),

]
