from flask import Flask, request, jsonify, send_from_directory
import joblib
import numpy as np
import os

# Chargement du modèle avec joblib
model = joblib.load("lightgbm_model.pkl")

app = Flask(__name__)

# Route pour l'URL racine ("/")
@app.route('/')
def home():
    return "Bienvenue sur l'API de Prédiction!"

# Route pour le favicon.ico
@app.route('/favicon.ico')
def favicon():
    # Assurez-vous que le fichier favicon.ico est dans le dossier "static"
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Récupération des données JSON
        data = request.get_json(force=True)
        
        # Vérifier si 'features' est présent dans les données
        if 'features' not in data:
            return jsonify({"error": "Missing 'features' key in request data"}), 400
        
        # Récupérer les caractéristiques
        features = data['features']
        
        # S'assurer que le nombre de caractéristiques est correct
        if len(features) != 73:  # Supposons que votre modèle nécessite 76 caractéristiques
            # Remplir les valeurs manquantes avec des zéros
            features = features + [0] * (73 - len(features))  # Compléter jusqu'à 73
            features = features[:73]  # S'assurer que nous avons exactement 73 caractéristiques

        # Faire la prédiction
        prediction = model.predict([features])
        probability = model.predict_proba([features])[0, 1]
        
        # Conversion en types JSON-serialisables
        return jsonify({
            "prediction": int(prediction[0]), 
            "probability": float(probability)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Utiliser le port fourni par Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
