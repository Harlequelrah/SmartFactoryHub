import paho.mqtt.client as mqtt
import random
import time
import json

# Configuration du broker HiveMQ
BROKER = "broker.hivemq.com"
PORT = 8883
TOPIC = "sensor/sensor1"

# Créer un client MQTT
client = mqtt.Client("DataGenerator", protocol=mqtt.MQTTv311)

# Activer TLS pour des connexions sécurisées
client.tls_set()

# Connexion au broker
client.connect(BROKER, PORT)

# Démarrer la boucle MQTT dans un thread séparé
client.loop_start()

print("Connexion réussie au broker HiveMQ !")

while True:
    # Génération de données aléatoires
    sensor_id=1
    temperature = round(random.uniform(20.0, 30.0), 2)
    humidity = round(random.uniform(10.0, 30.0), 2)
    energy = round(random.uniform(20.0, 30.0), 2)
    luminosity = round(random.uniform(20.0, 30.0), 2)  # Température entre 20 et 30°C
    pression = random.randint(40, 80)  # Humidité entre 40 et 80%
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Heure actuelle

    # Créer un message JSON
    messages=[{"humidity":humidity,"sensor_id":sensor_id,"luminosity":luminosity,"energy":energy,"temperature": temperature, "timestamp": timestamp},{"presure": pression, "timestamp": timestamp}]
    # Publier le message sur le topic
    client.publish(TOPIC, json.dumps(messages[0]))
    print(f"Message publié : {messages}")

    time.sleep(5)  # Attendre 5 secondes avant d'envoyer un autre message
