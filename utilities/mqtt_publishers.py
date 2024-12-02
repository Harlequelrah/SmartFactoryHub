import paho.mqtt.client as mqtt
import random
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
    sensor_data = {
        "sensor_id": sensor_id,
        "temperature": round(random.uniform(10.0, 60.0), 2),
        "humidity": round(random.uniform(10.0, 30.0), 2),
        "energy": round(random.uniform(20.0, 30.0), 2),
        "luminosity": round(random.uniform(20.0, 30.0), 2),
        "pressure": random.randint(40, 80),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    return sensor_data
while True:
        message = create_sensor(1)
        client.publish(TOPIC + str(1), json.dumps(message))
        print(f"Message publié : {message}")
        time.sleep(3)  # Attendre 5 secondes avant d'envoyer un autre message

# while True:
#     for i in range(1,5):
#         message=create_sensor(i)
#         client.publish(TOPIC+str(i), json.dumps(message))
#         print(f"Message publié : {message}")

#     time.sleep(5)  # Attendre 5 secondes avant d'envoyer un autre message
