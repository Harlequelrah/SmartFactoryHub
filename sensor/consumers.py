import json
from channels.generic.websocket import AsyncWebsocketConsumer


class SensorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Récupérer l'id du capteur à partir de l'URL
        self.sensor_id = self.scope["url_route"]["kwargs"]["sensor_id"]
        self.room_group_name = f"sensor_{self.sensor_id}"

        # Rejoindre un groupe spécifique à ce capteur
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe lors de la déconnexion
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        # Gérer la réception des messages
        data = json.loads(text_data)
        message = data.get("message", "")

        # Envoyer un message à tous les membres du groupe
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "sensor_message", "message": message}
        )

    async def sensor_message(self, event):
        # Envoyer un message au WebSocket
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
