from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging
import json


class WebSocketHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        channel_layer = get_channel_layer()

        # Envoie le log au groupe WebSocket
        async_to_sync(channel_layer.group_send)(
            "log_group",  # Le groupe WebSocket utilisé pour les logs
            {
                "type": "send_log",  # Type d'événement WebSocket
                "message": log_entry,
            },
        )
