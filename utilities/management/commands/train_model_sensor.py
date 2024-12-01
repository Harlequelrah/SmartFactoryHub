from django.core.management.base import BaseCommand
import pandas as pd
from sensor.models import Sensor
from sklearn.ensemble import RandomForestRegressor  # Exemple d'algorithme
import joblib  # Pour sauvegarder le modèle


class Command(BaseCommand):
    help = "Charge les données et entraîne un modèle intelligent"

    def handle(self, *args, **kwargs):
        # Charger les données depuis la base de données
        data = Sensor.objects.all().values(
            "temperature", "pressure", "luminosity", "energy", "humidity", "timestamp"
        )
        df = pd.DataFrame(data)

        # Assurer que la colonne 'timestamp' est bien au format DateTime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Extraire des caractéristiques temporelles utiles pour l'entraînement
        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.month
        df["day"] = df["timestamp"].dt.day
        df["hour"] = df["timestamp"].dt.hour
        df["minute"] = df["timestamp"].dt.minute

        # Utiliser ces nouvelles colonnes comme features
        X = df[
            [
                "year",
                "month",
                "day",
                "hour",
                "minute",
                "temperature",
                "pressure",
                "luminosity",
            ]
        ]

        # Entraîner et sauvegarder un modèle pour chaque variable cible
        for i in ["temperature", "pressure", "luminosity", "energy", "humidity"]:
            y = df[i]

            # Entraîner le modèle
            model = RandomForestRegressor(n_estimators=100)
            model.fit(X, y)

            # Sauvegarder le modèle
            joblib.dump(model, f"sensor_{i}_model.pkl")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Modèle entraîné et sauvegardé avec succès pour la donnée {i}!"
                )
            )
