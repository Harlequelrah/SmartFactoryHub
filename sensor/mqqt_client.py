import paho.mqtt.client as mqtt
import json
from channels.layers import get_channel_layer

BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "sensor/#"


# Fonction callback pour gérer la connexion
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connexion réussie au broker HiveMQ !")
        client.subscribe(TOPIC)
    else:
        print(f"Échec de la connexion, code de retour : {rc}")


# Fonction callback pour gérer les messages reçus
def on_message(client, userdata, msg):
    print(f"Message reçu : {msg.payload.decode('utf-8')}")
    try:
        message = json.loads(msg.payload.decode("utf-8"))
        print(f"Message JSON: {message}")

        # Utiliser le channel_layer pour envoyer les données à WebSocket
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            "sensor_data",  # Nom du groupe de WebSocket
            {
                "type": "send_sensor_data",  # Méthode dans le Consumer
                "sensor_data": message,  # Données du capteur
            },
        )
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON: {e}")


# Créer un client MQTT
client = mqtt.Client("SensorReceiver")
client.username_pw_set(username="smartfactoryhub", password="smfahu0156")
client.tls_set()  # Active TLS pour des connexions sécurisées

# Attacher les callbacks
client.on_connect = on_connect
client.on_message = on_message

# Tentative de connexion au broker
print("Tentative de connexion au broker...")
client.connect(BROKER, PORT)

# Démarrer la boucle d'écoute dans un thread séparé
client.loop_start()
import time

time.sleep(5)

if not client.is_connected():
    print("Le client n'a pas réussi à se connecter au broker.")

print("En attente de messages...")
time.sleep(60)
client.loop_stop()
