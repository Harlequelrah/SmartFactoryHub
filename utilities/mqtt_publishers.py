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
        temperature = round(random.uniform(20.0, 30.0), 2)
        humidity = round(random.uniform(10.0, 30.0), 2)
        energy = round(random.uniform(20.0, 30.0), 2)
        luminosity = round(random.uniform(20.0, 30.0), 2)  # Température entre 20 et 30°C
        pression = random.randint(40, 80)  # Humidité entre 40 et 80%
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return [{"humidity":humidity,"sensor_id":sensor_id,"luminosity":luminosity,"energy":energy,"temperature": temperature, "timestamp": timestamp},{"presure": pression, "timestamp": timestamp}][0]

while True:
    for i in range(1,5):
        message=create_sensor(i)
        client.publish(TOPIC+str(i), json.dumps(message))
        print(f"Message publié : {message}")

    time.sleep(5)  # Attendre 5 secondes avant d'envoyer un autre message
