import json
import paho.mqtt.client as mqtt
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import logging
from .log_consumers import WebSocketHandler
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
        logging.info("Connecté au broker MQTT avec succès")
        client.subscribe(TOPIC)  # Abonne-toi au topic
    else:
        logging.info(f"Échec de la connexion au broker MQTT, code : {rc}")


# Classe Consumer pour gérer les WebSockets
class SensorConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = "sensor_data"

        # Créer un groupe où tous les clients écoutent
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Démarrer l'abonnement aux données MQTT
        self.mqtt_client = mqtt.Client(client_id="DataReceiver")
        self.mqtt_client.username_pw_set(username="smartfactoryhub", password="smfahu0156")
        self.mqtt_client.tls_set()  # Active TLS pour des connexions sécurisées

        # Passer l'instance du consumer à la fonction on_message
        self.mqtt_client.on_connect = on_connect
        # Passer l'instance du consumer à la fonction on_message
        self.mqtt_client.on_message = self.on_message

        # Connexion au broker MQTT
        self.mqtt_client.connect(BROKER, PORT)
        self.mqtt_client.subscribe(TOPIC)

        # Démarrer l'écoute MQTT
        self.mqtt_client.loop_start()

    def on_message(self, client, userdata, msg):
        # Cette méthode est maintenant appelée sur l'instance du consumer
        message = msg.payload.decode("utf-8")
        try:
            sensor_data = json.loads(message)
            logging.info(f"Message reçu via MQTT: {sensor_data}")
            sensor_id = sensor_data.get("sensor_id")
            if not sensor_id:
                logging.info(f"Aucun sensor_id trouvé dans le message : {sensor_data}")
                return

            # Utilisation de async_to_sync pour appeler la méthode asynchrone du consumer
            async_to_sync(self.send_sensor_data_to_group)(sensor_id,sensor_data)

        except json.JSONDecodeError:
            logging.error(f"Erreur de décodage du message JSON: {message}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        self.mqtt_client.loop_stop()

    async def receive(self, text_data):
        # Cette méthode peut être utilisée pour recevoir des messages du client WebSocket
        data = json.loads(text_data)
        sensor_data = data.get("sensor_data", {})
        logging.info(f"Message reçu du client: {sensor_data}")

    async def send_sensor_data_to_group(self, sensor_id,sensor_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "send_sensor_data","sensor_id":sensor_id, "sensor_data": sensor_data},
        )

    async def send_sensor_data(self, event):
        sensor_data = event["sensor_data"]
        sensor_id=event["sensor_id"]
        await self.send(text_data=json.dumps({"sensor_id":sensor_id,"sensor_data": sensor_data}))


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
