import paho.mqtt.client as mqtt
import json
import logging

# Configuration du logger
logging.basicConfig(level=logging.DEBUG)  # Active les logs de niveau DEBUG
logger = logging.getLogger()

# Configuration du broker HiveMQ
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "capteur/temperature"


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
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON: {e}")


# Créer un client MQTT
client = mqtt.Client("DataReceiver")
client.username_pw_set(username="Harlequin", password="Harlequin0179")
client.tls_set()  # Active TLS pour des connexions sécurisées


# Attacher les callbacks

client.on_connect = on_connect
client.on_message = on_message

# Activer les logs pour Paho MQTT
client.enable_logger(logger)

# Tentative de connexion au broker
print("Tentative de connexion au broker...")
try:
    client.connect(BROKER, PORT)
except Exception as e:
    print(f"Erreur lors de la connexion : {e}")

# Démarrer la boucle d'écoute dans un thread séparé
client.loop_start()

# Attendre que la connexion soit établie et que des messages arrivent
import time

time.sleep(5)

if not client.is_connected():
    print("Le client n'a pas réussi à se connecter au broker.")

print("En attente de messages...")
time.sleep(60)
client.loop_stop()
