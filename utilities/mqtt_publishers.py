import paho.mqtt.client as mqtt
import random
from datetime import datetime, timedelta
import time
import json

# Configuration du broker HiveMQ
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "SmartFactoryHub_sensor/sensor"

# Créer un client MQTT
client = mqtt.Client(client_id="DataGenerator")

# Activer TLS pour des connexions sécurisées
client.tls_set()

# Connexion au broker
client.connect(BROKER, PORT)

# Démarrer la boucle MQTT dans un thread séparé
client.loop_start()


print("Connexion réussie au broker HiveMQ !")


def create_sensor(sensor_id):
    temperature = round(random.uniform(0.0, 100.0), 2)
    humidity = round(
        random.uniform(0.0, 1.0 - (temperature - 10) / 100), 2
    )  # Humidité diminue avec la température
    current_time = datetime.now() + timedelta(seconds=random.randint(0, 10))
    sensor_data = {
        "sensor_id": sensor_id,
        "temperature": temperature,
        "humidity": humidity,
        "energy": round(random.uniform(0.0, 200.0), 2),
        "luminosity": round(random.uniform(0.0, 3500.0), 2),
        "pressure": round(random.uniform(0.0, 30.0), 2),
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return sensor_data


# while True:
#         message = create_sensor(random.randint(1,8))
#         client.publish(TOPIC + str(1), json.dumps(message))
#         print(f"Message publié : {message}")
#         time.sleep(3)  # Attendre 5 secondes avant d'envoyer un autre message

while True:
    for i in range(1, 8):
        message = create_sensor(i)
        client.publish(TOPIC + str(i), json.dumps(message))
        print(f"Message publié : {message}")
        # time.sleep(3)

#     time.sleep(5)  # Attendre 5 secondes avant d'envoyer un autre message
