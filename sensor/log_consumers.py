from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
import json


class WebSocketHandler(logging.Handler):
    def emit(self, record):
        try:
            log_entry = self.format(record)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "log_group",
                {
                    "type": "send_log",
                    "message": log_entry,
                },
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi WebSocket : {e}")
