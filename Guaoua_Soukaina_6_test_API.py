import unittest
from app import app

class APITestCase(unittest.TestCase):
    def setUp(self):
        # Création d'un client pour tester l'API
        self.app = app.test_client()
        self.app.testing = True

    def test_prediction(self):
        # Liste de 73 caractéristiques (valeurs fictives pour cet exemple)
        features = [0] * 73  # Remplacez par des valeurs valides si nécessaire

        # Envoi de la requête POST avec les données JSON
        response = self.app.post("/predict", json={"features": features})
        
        # Vérification du statut
        print(f"Response status code: {response.status_code}")  # Ajout pour voir le code de statut
        print(f"Response data: {response.data}")  # Affichage du contenu de la réponse
        
        # Vérification de la réponse
        self.assertEqual(response.status_code, 200)  # Le code de statut doit être 200 pour succès
        self.assertIn("probability", response.json)   # La réponse doit contenir "probability"
        self.assertIn("prediction", response.json)    # La réponse doit contenir "prediction"

if __name__ == "__main__":
    unittest.main()
