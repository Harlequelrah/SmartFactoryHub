from datetime import datetime


class Sensor:
    def __init__(
        self, id, temperature, humidity, pressure, luminosity, energy, timestamp=None
    ):
        self.id = id
        self.temperature = temperature
        self.humidity = humidity
        self.pressure = pressure
        self.luminosity = luminosity
        self.energy = energy
        self.timestamp = timestamp if timestamp else datetime.now()

    def __repr__(self):
        return (
            f"<Sensor(id={self.id}, temperature={self.temperature}, humidity={self.humidity}, "
            f"pressure={self.pressure}, luminosity={self.luminosity}, energy={self.energy}, "
            f"timestamp={self.timestamp})>"
        )

    def as_dict(self):
        """Méthode pour convertir l'objet en dictionnaire."""
        return {
            "id": self.id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "pressure": self.pressure,
            "luminosity": self.luminosity,
            "energy": self.energy,
            "timestamp": self.timestamp,
        }
