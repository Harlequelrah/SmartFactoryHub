from django.urls import re_path
# from .consumers import  LogConsumer
from .consumers import SensorConsumer


websocket_urlpatterns = [
    re_path(r"^ws/sensor_data/$", SensorConsumer.as_asgi()),
    # re_path(r"ws/logs/$", LogConsumer.as_asgi()),
]
