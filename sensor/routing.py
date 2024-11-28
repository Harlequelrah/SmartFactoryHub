from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/sensor/(?P<sensor_id>\w+)/$", consumers.SensorConsumer.as_asgi()),
]
