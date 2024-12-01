from django.urls import re_path
from .consumers import SensorConsumer,LogConsumer


websocket_urlpatterns = [
    re_path(r"^ws/sensor_data/$", SensorConsumer.as_asgi()),
    re_path(r"ws/logs/$", LogConsumer.as_asgi()),
]
