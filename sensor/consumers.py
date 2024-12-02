import json
from django.db import connections
import paho.mqtt.client as mqtt
from django.utils.timezone import now, timedelta
import numpy as np
import joblib
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import logging
from .log_consumers import WebSocketHandler

# from sensor.models import Sensor
# from sensor.models import Machine
# Configuration du client MQTT
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "SmartFactoryHub_sensor/#"  # Utilise un wildcard pour écouter plusieurs topics (ex: sensor1, sensor2)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("sensor_logs.log"),
        logging.StreamHandler(),
        WebSocketHandler(),  # Nouveau handler pour WebSocket
    ],
)

logger = logging.getLogger(__name__)


# Fonction de callback pour la connexion MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connecté au broker MQTT avec succès")
        client.subscribe(TOPIC)  # Abonne-toi au topic
    else:
        logger.info(f"Échec de la connexion au broker MQTT, code : {rc}")


# Classe Consumer pour gérer les WebSockets
class SensorConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = "sensor_data"

        # Créer un groupe où tous les clients écoutent
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Démarrer l'abonnement aux données MQTT
        self.mqtt_client = mqtt.Client(client_id="DataReceiver")
        self.mqtt_client.username_pw_set(
            username="smartfactoryhub", password="smfahu0156"
        )
        self.mqtt_client.tls_set()  # Active TLS pour des connexions sécurisées

        # Passer l'instance du consumer à la fonction on_message
        self.mqtt_client.on_connect = on_connect
        # Passer l'instance du consumer à la fonction on_message
        self.mqtt_client.on_message = self.on_message

        # Connexion au broker MQTT
        self.mqtt_client.connect(BROKER, PORT)
        self.model = joblib.load("sensor_temperature_model.pkl")
        self.mqtt_client.subscribe(TOPIC)

        # Démarrer l'écoute MQTT
        self.mqtt_client.loop_start()

    def on_message(self, client, userdata, msg):
        # Cette méthode est maintenant appelée sur l'instance du consumer
        message = msg.payload.decode("utf-8")
        try:
            sensor_data = json.loads(message)
            # logger.info(f"Message reçu via MQTT: {sensor_data}")
            sensor_id = sensor_data.get("sensor_id")
            if not sensor_id:
                logger.info(f"Aucun sensor_id trouvé dans le message : {sensor_data}")
                return
            self.detect_anomaly_or_predict(sensor_data.get("temperature"),sensor_data.get('pressure'),sensor_data.get('luminosity'),sensor_data.get('energy'),sensor_data.get('humidity'))

            # Utilisation de async_to_sync pour appeler la méthode asynchrone du consumer
            async_to_sync(self.send_sensor_data_to_group)(sensor_id, sensor_data)

        except json.JSONDecodeError:
            logger.error(f"Erreur de décodage du message JSON: {message}")

    def detect_anomaly_or_predict(self, temperature, pressure, luminosity, energy, humidity):
        """Effectue une prédiction avec le modèle ou détecte une anomalie"""
        from datetime import datetime, timedelta

        # Préparer l'entrée pour le modèle (timestamp dans 10 secondes)
        future_timestamp = datetime.now() + timedelta(seconds=10)

        # Construire le DataFrame d'entrée avec les futures
        df = pd.DataFrame(
            [
                {
                    "timestamp": future_timestamp,
                    "year": future_timestamp.year,
                    "month": future_timestamp.month,
                    "day": future_timestamp.day,
                    "hour": future_timestamp.hour,
                    "minute": future_timestamp.minute,
                    "pressure": pressure,
                    "luminosity": luminosity,
                    "energy": energy,
                    "humidity": humidity,
                }
            ]
        )

        # Définir les colonnes utilisées pour la prédiction
        X = df[
            [
                "year",
            "month",
                "day",
            "hour",
                "minute",
                "pressure",
                "luminosity",
                "energy",
                "humidity",
            ]
        ]

        # Faire une prédiction pour dans 10 secondes
        predicted_temperature = self.model.predict(X)[0]

        # Logger la prédiction
        logger.info(
            f"Température prédite pour dans 10 secondes ({future_timestamp}):     {predicted_temperature:.2f}°C"
        )

        # Vérifier si la température prédite est anormale
        self.check_temperature(predicted_temperature)

        return predicted_temperature

    def check_temperature(self, temperature):
        if temperature < 10:
            log = "une panne de chauffage ou un environnement inadéquat"
        elif temperature > 60:
            log = " un risque d'équipement en surchauffe ou d'incendie"
            logger.warning(
                    f"Anomalie détectée : La Température prédite dans 10s sera ({temperature}°C) qui peut indiquer {log}.)"
                )

    def check_pressure(self, pression):
        if (
            pression < 0.5
        ):  # Valeur indicative, en dessous de la pression minimale attendue
            logger.warning(
                "Attention : Pression trop faible, pourrait indiquer une fuite ou un dysfonctionnement."
            )
        elif (
            pression > 15
        ):  # Valeur indicative, au-dessus de la pression maximale attendue
            logger.warning(
                "Attention : Pression trop élevée, risque d'endommagement des équipements ou d'explosion."
            )

    def check_luminosity(self, luminosity):
        if luminosity < 100:  # Valeur indicative pour des environnements d'ateliers
            logger.warning(
                "Attention : Luminosité trop faible, risque de sécurité ou  d'erreur de travail."
            )
        elif (
            luminosity > 3000
        ):  # Valeur indicative pour des environnements où une trop forte     luminosité peut causer des problèmes
            logger.warning(
                "Attention : Luminosité trop élevée, risque d'éblouissement oude gaspillage d'énergie."
            )

    def check_energy(self, energy):
        if energy < 10:  # Valeur indicative, dépend de l'application
            logger.warning(
                "Attention : Consommation d'énergie trop faible, pourrait indiquer une panne ou un arrêt non planifié."
            )
        elif energy > 150:  # Valeur indicative, à ajuster selon les besoins
            logger.warning(
                "Attention : Consommation d'énergie trop élevée, pourrait indiquer une surcharge ou un dysfonctionnement."
            )

    def check_humidity(self, humidity):
        if humidity < 0.20:
            logger.warning(
                "Attention : Humidité trop faible, risque d'électricité statique."
            )
        elif humidity > 0.80:
            logger.warning(
                "Attention : Humidité trop élevée, risque de corrosion ou moisissures."
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        self.mqtt_client.loop_stop()

    async def receive(self, text_data):
        # Cette méthode peut être utilisée pour recevoir des messages du client WebSocket
        data = json.loads(text_data)
        sensor_data = data.get("sensor_data", {})
        logger.info(f"Message reçu du client: {sensor_data}")

    async def send_sensor_data_to_group(self, sensor_id, sensor_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_sensor_data",
                "sensor_id": sensor_id,
                "sensor_data": sensor_data,
            },
        )

    async def send_sensor_data(self, event):
        sensor_data = event["sensor_data"]
        sensor_id = event["sensor_id"]
        await self.send(
            text_data=json.dumps({"sensor_id": sensor_id, "sensor_data": sensor_data})
        )


class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "log_group"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        log_message = data.get("log_message")
        if log_message:
            await self.send_log_message(log_message)

    async def send_log_message(self, log_message):
        await self.send(text_data=json.dumps({"message": log_message}))
