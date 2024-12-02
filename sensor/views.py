from django.shortcuts import render


def sensor_data_view(request):
    return render(request, "sensor_data.html")


def sensor_log_view(request):
    return render(request, "sensor_log_view.html")


def sensors_data_view(request):
    return render(request, "sensors_data.html")
def sensors_dashboard_view(request):
    return render(request, "sensor_dashboard.html")
