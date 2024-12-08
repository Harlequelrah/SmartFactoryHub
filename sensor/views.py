from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def sensor_data_view(request):
    return render(request, "sensor_data.html")


def sensor_log_view(request):
    return render(request, "sensor_log_view.html")


def sensors_data_view(request):
    return render(request, "sensors_data.html")

@login_required
def sensor_dashboard(request):
    return render(request, "sensor_dashboard.html")
