import logging
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from sensor.models import Sensor
from django.db import connections
import threading
import joblib
import random
import time
import json
import numpy as np
import pandas as pd
from sensor.models import Sensor
# Configuration du logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Configuration du broker HiveMQ
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "SmartFactoryHub_sensor/#"


class MqttService:
    def __init__(self, client_id):
        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(username="smartfactoryhub", password="smfahu0156")
        self.client.tls_set()  # Activer TLS pour une connexion sécurisée
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.enable_logger(logger)

    def connect(self):
        """Connecte le client MQTT au broker"""
        self.client.connect(BROKER, PORT)

    def on_connect(self, client, userdata, flags, rc):
        """Callback appelé lors de la connexion"""
        if rc == 0:
            logger.info("Connexion réussie au broker !")
            self.client.subscribe(TOPIC)  # S'abonner au topic de température# S'abonner au topic de pression
        else:
            logger.error(f"Échec de la connexion, code de retour : {rc}")

    def on_message(self, client, userdata, msg):
        # Cette méthode est maintenant appelée sur l'instance du consumer
        message = msg.payload.decode("utf-8")
        try:
            sensor_data = json.loads(message)
            logger.info(f"Message reçu via MQTT: {sensor_data}")
            sensor_id = sensor_data.get("sensor_id")
            if not sensor_id:
                logger.info(f"Aucun sensor_id trouvé dans le message : {sensor_data}")
                return
            required_fields = ["temperature", "humidity", "pressure", "energy", "luminosity"]
            if not all(field in sensor_data for field in required_fields):
                logger.error(f"Données manquantes dans le message : {sensor_data}")
                return
            try:
                Sensor.objects.create(
                    temperature=sensor_data.get("temperature"),
                    humidity=sensor_data.get("humidity"),
                    pressure=sensor_data.get("pressure"),
                    energy=sensor_data.get("energy"),
                    luminosity=sensor_data.get("luminosity")
                )
                logger.info("Capteur enregistré dans la base de données.")
            except Exception as e:
                logger.error(f"Erreur lors de l'enregistrement du capteur : {e}")
        except json.JSONDecodeError:
            logger.error(f"Erreur de décodage du message JSON: {message}")

    def _check_database_connection(self):
        """Vérifie si la connexion à la base de données est prête"""
        try:
            connection = connections["default"]
            connection.ensure_connection()
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données : {e}")
            return False

    def loop(self):
        """Démarre la boucle d'écoute pour recevoir des messages"""
        self.client.loop_forever()


class Command(BaseCommand):
    help = "Lance le service MQTT pour publier et s'abonner aux messages"

    def handle(self, *args, **kwargs):
        # Créer le service MQTT
        mqtt_service = MqttService(client_id="DataGenerator")

        # Connecter le client MQTT
        mqtt_service.connect()

        # Démarrer le subscriber (écoute des messages) dans un thread
        subscriber_thread = threading.Thread(target=mqtt_service.loop)
        subscriber_thread.daemon = (
            True  # Assurer que le thread se termine lorsque l'application se ferme
        )
        subscriber_thread.start()
