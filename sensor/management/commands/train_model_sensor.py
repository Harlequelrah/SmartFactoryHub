from django.core.management.base import BaseCommand
import pandas as pd
from sensor.models import Sensor
from sklearn.ensemble import RandomForestRegressor
import joblib


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

        # Extraire des caractéristiques temporelles
        df["year"] = df["timestamp"].dt.year
        df["month"] = df["timestamp"].dt.month
        df["day"] = df["timestamp"].dt.day
        df["hour"] = df["timestamp"].dt.hour
        df["minute"] = df["timestamp"].dt.minute

        # Colonnes de base pour les features
        base_features = ["year", "month", "day", "hour", "minute"]
        futures = ["temperature", "pressure", "luminosity", "energy", "humidity"]

        for target in futures:
            # Construire X en ajoutant les autres variables comme features
            additional_features = [feature for feature in futures if feature != target]
            X = df[base_features + additional_features]
            y = df[target]

            # Vérifier et nettoyer les données manquantes
            X = X.dropna()
            y = y[X.index]

            # Entraîner le modèle
            model = RandomForestRegressor(n_estimators=100)
            model.fit(X, y)

            # Sauvegarder le modèle
            joblib.dump(model, f"sensor_{target}_model.pkl")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Modèle entraîné et sauvegardé avec succès pour la donnée {target}!"
                )
            )
