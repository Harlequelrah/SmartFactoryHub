from django.db import models

# Create your models here.
class Sensor(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    luminosity = models.FloatField()
    energy = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Machine(models.Model):
    temperature = models.FloatField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.temperature}°C at {self.timestamp}"
