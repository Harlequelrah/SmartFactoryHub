from django.shortcuts import render


def sensor_data_view(request):
    return render(request, "sensor_data.html")
