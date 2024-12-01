from django.core.management.base import BaseCommand
import pandas as pd
from sensor.models import Machine
from sklearn.ensemble import RandomForestRegressor  # Exemple d'algorithme
import joblib  # Pour sauvegarder le modèle

class Command(BaseCommand):
    help = 'Charge les données et entraîne un modèle intelligent'

    def handle(self, *args, **kwargs):
        # Charger les données depuis la base de données
        data = Machine.objects.all().values('temperature', 'timestamp')
        df = pd.DataFrame(data)

        # Assurer que la colonne 'timestamp' est bien au format DateTime
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Exemple de préparation des données pour l'entraînement
        # Vous pouvez ajouter ici des transformations spécifiques
        X = df['timestamp'].values.reshape(-1, 1)  # Par exemple, prédire la température à partir du temps
        y = df['temperature']

        # Entraîner un modèle d'exemple (par exemple, RandomForest)
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X, y)

        # Sauvegarder le modèle entraîné
        joblib.dump(model, 'temperature_model.pkl')

        self.stdout.write(self.style.SUCCESS('Modèle entraîné et sauvegardé avec succès !'))
