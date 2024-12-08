from django.contrib import admin
from django.urls import path, include
from sensor.routing import websocket_urlpatterns
from sensor.views import sensor_data_view, sensor_dashboard,sensors_data_view,sensor_log_view
from auth_app import views

app_name = 'sensor'


urlpatterns=[
path("sensor_data/", sensor_data_view, name="sensor_data"),
    # path("sensor_log/", sensor_log_view, name="sensor_log"),
path("sensor_dashboard/", sensor_dashboard, name="sensor_dashboard"),
path("sensors_data/", sensors_data_view, name="sensors_data"),]