from django.core.management.base import BaseCommand
from sensor.services.mqtt_manager import MqttService 
import threading

class Command(BaseCommand):
    help = "Lance le service MQTT pour publier et s'abonner aux messages"

    def handle(self, *args, **kwargs):
        # Créer le service MQTT
        mqtt_service = MqttService(client_id="DataGenerator")

        # Connecter le client MQTT
        mqtt_service.connect()

        # Démarrer le subscriber (écoute des messages) dans un thread
        subscriber_thread = threading.Thread(target=mqtt_service.loop)
        subscriber_thread.daemon = True  # Assurer que le thread se termine lorsque l'application se ferme
        subscriber_thread.start()

        # Démarrer le publisher (génération et envoi des données)
        mqtt_service.start_publisher()
