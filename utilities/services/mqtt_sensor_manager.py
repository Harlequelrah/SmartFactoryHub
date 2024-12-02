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
        self.client.tls_set()  # Activer TLS pour une connexion sécurisée
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Charger le modèle une fois lors de l'initialisation du service
        self.model = joblib.load("sensor_model.pkl")
        logger.info("Modèle chargé avec succès.")

    def connect(self):
        """Connecte le client MQTT au broker"""
        self.client.connect(BROKER, PORT)

    def create_sensor(sensor_id):
        temperature = round(random.uniform(20.0, 30.0), 2)
        humidity = round(random.uniform(10.0, 30.0), 2)
        energy = round(random.uniform(20.0, 30.0), 2)
        luminosity = round(
            random.uniform(20.0, 30.0), 2
        )  # Température entre 20 et 30°C
        pression = random.randint(40, 80)  # Humidité entre 40 et 80%
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return [
            {
                "humidity": humidity,
                "sensor_id": sensor_id,
                "luminosity": luminosity,
                "energy": energy,
                "temperature": temperature,
                "timestamp": timestamp,
            },
            {"presure": pression, "timestamp": timestamp},
        ][0]

    def on_connect(self, client, userdata, flags, rc):
        """Callback appelé lors de la connexion"""
        if rc == 0:
            logger.info("Connexion réussie au broker !")
            self.client.subscribe(TOPIC1)  # S'abonner au topic de température
            self.client.subscribe(TOPIC2)  # S'abonner au topic de pression
        else:
            logger.error(f"Échec de la connexion, code de retour : {rc}")

    def on_message(self, client, userdata, msg):
        """Callback appelé lors de la réception de messages"""
        try:
            message = json.loads(msg.payload.decode("utf-8"))
            logger.info(f"Message reçu : {message}")
            temperature = message.get("temperature")
            if temperature is not None:
                # Vérifie que la base de données est prête avant d'interagir avec elle
                if self._check_database_connection():
                    # Enregistrer la température dans la base de données
                    Machine.objects.create(temperature=temperature, timestamp=now())
                    logger.info(
                        f"Message enregistré dans la base de données : {message}"
                    )

                    # Prédire la température ou détecter une anomalie
                    self.detect_anomaly_or_predict(temperature)

                else:
                    logger.error("Connexion à la base de données échouée.")
            else:
                logger.error("Message reçu sans 'temperature'.")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON : {e}")


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


