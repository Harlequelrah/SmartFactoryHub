import json
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

# Configuration du client MQTT
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "sensor/sensor1"  # Utilise un wildcard pour écouter plusieurs topics (ex: sensor1, sensor2)


# Fonction de callback pour MQTT
def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    try:
        sensor_data = json.loads(message)
        print(f"Message reçu via MQTT: {sensor_data}")

        # Envoi des données au groupe WebSocket (utilisation de async_to_sync pour appeler la méthode asynchrone)
        async_to_sync(client.send_sensor_data_to_group)(sensor_data)

    except json.JSONDecodeError:
        print(f"Erreur de décodage du message JSON: {message}")


# Classe Consumer pour gérer les WebSockets
class SensorConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Le client se connecte à un WebSocket
        self.room_group_name = "sensor_data"

        # Créer un groupe où tous les clients écoutent
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        # Démarrer l'abonnement aux données MQTT
        self.mqtt_client = mqtt.Client(client_id=
            "DataReceiver"
        )  # Ajout de la version API des callbacks
        self.mqtt_client.username_pw_set(
            username="smartfactoryhub", password="smfahu0156"
        )
        self.mqtt_client.tls_set()  # Active TLS pour des connexions sécurisées

        # Connexion au broker MQTT
        self.mqtt_client.connect(BROKER, PORT)

        # Attacher la fonction callback pour la réception des messages MQTT
        self.mqtt_client.on_message = on_message

        # Démarrer l'écoute MQTT
        self.mqtt_client.loop_start()

    async def disconnect(self, close_code):
        # Lorsque la connexion WebSocket est fermée
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

        # Arrêter le client MQTT lorsqu'on déconnecte
        self.mqtt_client.loop_stop()

    async def receive(self, text_data):
        # Cette méthode peut être utilisée si tu souhaites recevoir des messages depuis le WebSocket
        data = json.loads(text_data)
        sensor_data = data.get("sensor_data", {})
        print(f"Message reçu du client: {sensor_data}")

        # Traiter ou stocker les données ici si nécessaire

    # Envoi des données reçues à tous les clients via WebSocket
    async def send_sensor_data_to_group(self, sensor_data):
        # Cette méthode est appelée pour envoyer les données à tous les clients connectés
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "send_sensor_data", "sensor_data": sensor_data},
        )

    # Envoi de données à tous les clients connectés via WebSocket
    async def send_sensor_data(self, event):
        # Cette méthode sera appelée par le groupe lors de l'envoi de données
        sensor_data = event["sensor_data"]
        await self.send(text_data=json.dumps({"sensor_data": sensor_data}))
