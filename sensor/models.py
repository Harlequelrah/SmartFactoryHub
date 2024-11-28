from django.db import models

# Create your models here.
class Sensor(models.Model):
    id=models.IntegerField()
    temperature = models.IntegerField()
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    luminosity = models.IntegerField()
    energy = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
