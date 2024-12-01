from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.core.management import call_command

class SensorConfig(AppConfig):
    name = 'sensor'

    def ready(self):
       call_command('mqtt_command')
