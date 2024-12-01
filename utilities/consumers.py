import json
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import logging
from django.utils.timezone import now, timedelta
from django.db import connections
import joblib
from .models import Sensor

import random
import time
import numpy as np
import pandas as pd
from .log_consumers import WebSocketHandler

# Configuration du client MQTT
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "SmartFactoryHub_sensor/#"  # Utilise un wildcard pour écouter plusieurs topics (ex: sensor1, sensor2)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # logging.FileHandler("sensor_logs.log"),
        # logging.StreamHandler(),
        # WebSocketHandler(),  # Nouveau handler pour WebSocket
    ],
)

logger = logging.getLogger(__name__)

# Fonction de callback pour la connexion MQTT
def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connecté au broker MQTT avec succès")
            client.subscribe(TOPIC)  # Abonne-toi au topic

        else:
            print(f"Échec de la connexion au broker MQTT, code : {rc}")

# Classe Consumer pour gérer les WebSockets
class SensorConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = "sensor_data"

        # Créer un groupe où tous les clients écoutent
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Démarrer l'abonnement aux données MQTT
        self.mqtt_client = mqtt.Client(client_id="SmartFactoryHubClient")
        self.mqtt_client.username_pw_set(
            username="smartfactoryhub", password="smfahu0156"
        )
        self.mqtt_client.tls_set()  # Active TLS pour des connexions sécurisées

        # Passer l'instance du consumer à la fonction on_message
        self.mqtt_client.on_connect = on_connect
        self.sensor_models = {
                "temperature": joblib.load("sensor_temperature_model.pkl"),
                "pressure": joblib.load("sensor_pressure_model.pkl"),
                "luminosity": joblib.load("sensor_luminosity_model.pkl"),
                "energy": joblib.load("sensor_energy_model.pkl"),
            }
        logger.info("Modèles chargés avec succès.")
        # Passer l'instance du consumer à la fonction on_message
        self.mqtt_client.on_message = self.on_message

        # Connexion au broker MQTT
        self.mqtt_client.connect(BROKER, PORT)
        self.mqtt_client.subscribe(TOPIC)

        # Démarrer l'écoute MQTT
        self.mqtt_client.loop_start()
    def _check_database_connection(self):
        """Vérifie si la connexion à la base de données est prête"""
        try:
            connection = connections['default']
            connection.ensure_connection()
            return True
        except Exception as e:
            logger.error(f"Erreur de connexion à la base de données : {e}")
            return False



    def on_message(self, client, userdata, msg):
        # Cette méthode est maintenant appelée sur l'instance du consumer
        message = msg.payload.decode("utf-8")
        try:
            sensor_data = json.loads(message)
            print(f"Message reçu via MQTT: {sensor_data}")
            sensor_id = sensor_data.get("sensor_id")
            if not sensor_id:
                print(f"Aucun sensor_id trouvé dans le message : {sensor_data}")
                return

            temperature=sensor_data.get("temperature")
            humidity=sensor_data.get("humidity")
            luminosity=sensor_data.get("luminosity")
            energy=sensor_data.get("energy")
            pressure=sensor_data.get("pressure")
            if self._check_database_connection() and Sensor.objects.count()<120:
                Sensor.objects.create(
                    temperature=temperature,
                    humidity=humidity,
                    luminosity=luminosity,
                    energy=energy,
                    pressure=pressure,
                )
            self.detect_anomaly_or_predict(sensor_data)

            # Utilisation de async_to_sync pour appeler la méthode asynchrone du consumer
            async_to_sync(self.send_sensor_data_to_group)(sensor_id, sensor_data)

        except json.JSONDecodeError:
            print(f"Erreur de décodage du message JSON: {message}")

    def detect_anomaly_or_predict(self):
        future_timestamp = now() + timedelta(seconds=10)
        future_timestamp_value = pd.to_datetime(future_timestamp).value
        input_data = np.array([[future_timestamp_value]]).reshape(-1, 1)

        # Prédictions pour chaque variable cible en utilisant les modèles chargés
        predicted_temperature = self.sensor_models["temperature"].predict(input_data)[0]
        predicted_pressure = self.sensor_models["pressure"].predict(input_data)[0]
        predicted_luminosity = self.sensor_models["luminosity"].predict(input_data)[0]
        predicted_energy = self.sensor_models["energy"].predict(input_data)[0]

        logger.info(
            f"Données de capteur prédites pour dans 10 secondes : "
            f"Température: {predicted_temperature}, "
            f"Pression: {predicted_pressure}, "
            f"Luminosité: {predicted_luminosity}, "
            f"Énergie: {predicted_energy}"
        )

        # Vérifier les anomalies sur chaque prédiction
        self.check_temperature(predicted_temperature)
        self.check_pressure(predicted_pressure)
        self.check_luminosity(predicted_luminosity)
        self.check_energy(predicted_energy)

    def check_pressure(self,pression):
        if pression < 0.5:  # Valeur indicative, en dessous de la pression minimale attendue
            logger.warning("Attention : Pression trop faible, pourrait indiquer une fuite ou un dysfonctionnement.")
        elif pression > 15:  # Valeur indicative, au-dessus de la pression maximale attendue
            logger.warning("Attention : Pression trop élevée, risque d'endommagement des équipements ou d'explosion.")

    def check_luminosity(self,luminosity):
        if luminosity < 100:  # Valeur indicative pour des environnements d'ateliers
            logger.warning("Attention : Luminosité trop faible, risque de sécurité ou  d'erreur de travail.")
        elif luminosity > 3000:  # Valeur indicative pour des environnements où une trop forte     luminosité peut causer des problèmes
            logger.warning("Attention : Luminosité trop élevée, risque d'éblouissement oude gaspillage d'énergie.")

    def check_energy(self,energy):
        if energy < 10:  # Valeur indicative, dépend de l'application
            logger.warning("Attention : Consommation d'énergie trop faible, pourrait indiquer une panne ou un arrêt non planifié.")
        elif energy > 150:  # Valeur indicative, à ajuster selon les besoins
            logger.warning("Attention : Consommation d'énergie trop élevée, pourrait indiquer une surcharge ou un dysfonctionnement.")

    def check_humidity(self,humidity):
        if humidity < 0.20:
            logger.warning("Attention : Humidité trop faible, risque d'électricité statique.")
        elif humidity > 0.80:
            logger.warning("Attention : Humidité trop élevée, risque de corrosion ou moisissures.")

    def check_temperature(self,temperature):
        if temperature < 10:
            log = "une panne de chauffage ou un environnement inadéquat"
        elif temperature > 60:
            log = " un risque d'équipement en surchauffe ou d'incendie"
            logger.warning(
                f"Anomalie détectée : La Température prédite dans 10s sera ({temperature}°C) qui peut indiquer {log}.)"
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        self.mqtt_client.loop_stop()

    async def receive(self, text_data):
        # Cette méthode peut être utilisée pour recevoir des messages du client WebSocket
        data = json.loads(text_data)
        sensor_data = data.get("sensor_data", {})
        print(f"Message reçu du client: {sensor_data}")

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


# class LogConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_group_name = "log_group"
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         log_message = data.get("log_message")
#         if log_message:
#             await self.send_log_message(log_message)

#     async def send_log_message(self, log_message):
#         await self.send(text_data=json.dumps({"message": log_message}))
