import json
import time
import random
import logging
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from sensor.models import Machine
from django.db import connections
import threading
import joblib
import numpy as np
import pandas as pd

# Configuration du logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configuration du broker HiveMQ
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC1 = "capteur1/temperature"
TOPIC2 = "capteur1/pression"

class MqttService:
    def __init__(self, client_id):
        self.client = mqtt.Client(client_id, protocol=mqtt.MQTTv311)
        self.client.tls_set()  # Activer TLS pour une connexion sécurisée
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Charger le modèle une fois lors de l'initialisation du service
        self.model = joblib.load('temperature_model.pkl')
        logger.info("Modèle chargé avec succès.")

    def connect(self):
        """Connecte le client MQTT au broker"""
        self.client.connect(BROKER, PORT)

    def publish(self, temperature, pression, timestamp):
        """Publie les données sur les topics MQTT"""
        messages = [
            {"temperature": temperature, "timestamp": timestamp},
            {"pression": pression, "timestamp": timestamp},
        ]
        self.client.publish(TOPIC1, json.dumps(messages[0]))
        self.client.publish(TOPIC2, json.dumps(messages[1]))
        logger.info(f"Message publié : {messages}")

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
                    Machine.objects.create(
                        temperature=temperature,
                        timestamp=now()
                    )
                    logger.info(f"Message enregistré dans la base de données : {message}")

                    # Prédire la température ou détecter une anomalie
                    self.detect_anomaly_or_predict(temperature)

                else:
                    logger.error("Connexion à la base de données échouée.")
            else:
                logger.error("Message reçu sans 'temperature'.")
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON : {e}")

    def detect_anomaly_or_predict(self, temperature):
        """Effectue une prédiction avec le modèle ou détecte une anomalie"""
        # Préparer l'entrée pour le modèle (on transforme le timestamp ou toute autre donnée pertinente)
        timestamp_value = pd.to_datetime(now()).value  # Utilisation du timestamp actuel
        input_data = np.array([[timestamp_value]]).reshape(-1, 1)

        # Faire une prédiction
        predicted_temperature = self.model.predict(input_data)[0]
        logger.info(f"Température prédite pour le timestamp {now()}: {predicted_temperature:.2f}°C")

        # Anomalie détectée si la température réelle s'écarte trop de la prédiction
        threshold = 7.0  # Exemple : seuil de 5°C d'écart
        if abs(temperature - predicted_temperature) > threshold:
            logger.warning(f"Anomalie détectée : Température réelle ({temperature}°C) éloignée de la prédiction ({predicted_temperature:.2f}°C)")

    def _check_database_connection(self):
        """Vérifie si la connexion à la base de données est prête"""
        try:
            connection = connections['default']
            connection.ensure_connection()
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données : {e}")
            return False

    def loop(self):
        """Démarre la boucle d'écoute pour recevoir des messages"""
        self.client.loop_forever()

    def start_publisher(self):
        """Démarre le publisher MQTT dans un thread séparé"""
        while True:
            # Génération de données aléatoires
            temperature = round(random.uniform(10.0, 40.0), 2)
            pression = random.randint(40, 80)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # Publier les données
            self.publish(temperature, pression, timestamp)

            time.sleep(5)  # Attendre 5 secondes avant d'envoyer un autre message

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
