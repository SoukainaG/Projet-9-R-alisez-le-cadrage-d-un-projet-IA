import pandas as pd
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px

# Configurer le titre de la page
st.set_page_config(page_title="Tableau de Bord de Scoring Client", page_icon=":bar_chart:")

# URL du fichier Excel brut hébergé sur GitHub
excel_url = 'https://raw.githubusercontent.com/SoukainaG/P7_API_d-ploiement/master/data_test.xlsx'

# Charger les données depuis l'URL
try:
    # Charger directement les données depuis l'URL, spécifiez l'engine 'openpyxl' pour le format .xlsx
    clients_df = pd.read_excel(excel_url, engine='openpyxl')
    st.success("Les données ont été chargées avec succès depuis GitHub.")
except Exception as e:
    st.error(f"Erreur lors du chargement des données : {e}")
    st.stop()

# URL de l'API déployée
API_URL = "https://p7-api-d-ploiement-6.onrender.com/"

# Fonction pour obtenir la prédiction depuis l'API
def get_prediction(features):
    if len(features) < 73:
        features = features + [0] * (73 - len(features))
    features = features[:73]
    try:
        response = requests.post(API_URL + "predict", json={"features": features})
        if response.status_code == 200:
            result = response.json()
            return result.get("prediction"), result.get("probability")
        else:
            st.error(f"Erreur dans la réponse de l'API. Code d'état : {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la communication avec l'API : {e}")
        return None, None

# Extraction des 20 caractéristiques importantes
important_features = clients_df[['EXT_SOURCES_MAX', 'HOUR_APPR_PROCESS_START', 'EXT_SOURCES_MIN', 
'BURO_AMT_CREDIT_MAX_OVERDUE_MEAN', 'CREDIT_TO_GOODS_RATIO', 
'INS_D365INS_IS_DPD_UNDER_120_MEAN', 'POS_CNT_INSTALMENT_MIN', 
'PREV_HOUR_APPR_PROCESS_START_MAX', 'INSTAL_INS_IS_DPD_UNDER_120_MEAN', 
'PREV_DAYS_TERMINATION_MAX', 'PREV_APP_CREDIT_PERC_MAX', 
'PREV_DAYS_LAST_DUE_DIFF_MEAN', 'INSTAL_LATE_PAYMENT_MEAN', 
'INS_D365DPD_DIFF_MAX', 'INCOME_TO_EMPLOYED_RATIO', 
'EXT_SOURCE_2', 'REGION_POPULATION_RELATIVE', 
'PREV_SIMPLE_INTERESTS_MEAN', 'PAYMENT_RATE', 'DAYS_EMPLOYED']]

# Dictionnaire de définitions des caractéristiques
feature_definitions = {
    'EXT_SOURCES_MAX': "Le maximum des sources externes, indiquant l'élément externe avec la valeur maximale.",
    'HOUR_APPR_PROCESS_START': "L'heure de début du processus de demande de crédit.",
    'EXT_SOURCES_MIN': "Le minimum des sources externes, indiquant l'élément externe avec la valeur minimale.",
    'BURO_AMT_CREDIT_MAX_OVERDUE_MEAN': "Montant moyen du crédit maximum en retard dans le bureau de crédit.",
    'CREDIT_TO_GOODS_RATIO': "Ratio du crédit par rapport à la valeur des biens.",
    'INS_D365INS_IS_DPD_UNDER_120_MEAN': "Indicateur de retard de paiement sous 120 jours moyen pour les assurances.",
    'POS_CNT_INSTALMENT_MIN': "Le nombre minimal de paiements par versement.",
    'PREV_HOUR_APPR_PROCESS_START_MAX': "L'heure maximale de début du processus de demande de crédit dans le passé.",
    'INSTAL_INS_IS_DPD_UNDER_120_MEAN': "Indicateur de retard de paiement sous 120 jours moyen pour les prêts à tempérament.",
    'PREV_DAYS_TERMINATION_MAX': "Nombre maximal de jours jusqu'à la fin du processus précédent.",
    'PREV_APP_CREDIT_PERC_MAX': "Pourcentage maximum de crédit accordé pour les demandes de crédit précédentes.",
    'PREV_DAYS_LAST_DUE_DIFF_MEAN': "Différence moyenne de jours depuis la dernière échéance pour les crédits antérieurs.",
    'INSTAL_LATE_PAYMENT_MEAN': "Moyenne des retards de paiement sur les installations de crédits.",
    'INS_D365DPD_DIFF_MAX': "Différence maximale de jours depuis le dernier retard de paiement sur une période de 365 jours pour les assurances.",
    'INCOME_TO_EMPLOYED_RATIO': "Rapport entre les revenus et le nombre d'années d'emploi.",
    'EXT_SOURCE_2': "Score de la source externe 2, représentant un facteur de risque.",
    'REGION_POPULATION_RELATIVE': "Population relative dans la région de résidence du client.",
    'PREV_SIMPLE_INTERESTS_MEAN': "Moyenne des intérêts simples sur les crédits précédents.",
    'PAYMENT_RATE': "Taux de paiement par rapport au montant du crédit initial.",
    'DAYS_EMPLOYED': "Nombre de jours que le client a été employé."
}

# Titre de l'application
st.title("Tableau de Bord de Scoring Client")

# Sélection du client
client_id = st.selectbox("Sélectionnez un client", options=clients_df.index)
features = important_features.iloc[client_id].tolist()

# Calcul de la prédiction lorsque le client est sélectionné
if 'prediction' not in st.session_state or st.session_state.get("client_id") != client_id:
 prediction, probability = get_prediction(features)
 st.session_state["prediction"] = prediction
 st.session_state["probability"] = 1 - probability
 st.session_state["client_id"] = client_id

# Affichage du résultat de la prédiction
if st.session_state.get("prediction") is not None:
    seuil = 0.24
    decision = "Crédit Accordé" if st.session_state["probability"] >= seuil else "Crédit Refusé"

    # Description et affichage de la jauge pour le score
    st.write("Graphique de jauge montrant le score de probabilité du client sélectionné.")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=st.session_state["probability"],
        title={'text': "Score de Probabilité"},
        gauge={'axis': {'range': [0, 1]},
               'bar': {'color': "darkblue"},
               'steps': [{'range': [0, seuil], 'color': "red"},
                         {'range': [seuil, 1], 'color': "green"}]},
        delta={'reference': seuil, 'increasing': {'color': "green"}}
    ))
    st.plotly_chart(fig_gauge, key="gauge_chart")

    # Affichage des résultats de la prédiction
    st.write(f"Prédiction : {'Crédit Refusé' if st.session_state['prediction'] == 1 else 'Crédit Accordé'}")
    st.write(f"Probabilité de paiement : {st.session_state['probability']:.2f}")

    # Graphique de l'importance locale des caractéristiques
    st.subheader("Importance Locale des Caractéristiques")
    local_importance = pd.Series(features, index=important_features.columns)
    fig_local = px.bar(local_importance, x=local_importance.values, y=local_importance.index, orientation='h')
    st.plotly_chart(fig_local, key="local_importance_chart")

    # Sélection des caractéristiques pour l'analyse univariée
    st.subheader("Analyse Univariée des Caractéristiques")
    feature1 = st.selectbox("Sélectionnez la première caractéristique", important_features.columns)
    feature2 = st.selectbox("Sélectionnez la deuxième caractéristique", important_features.columns)

    # Affichage de la définition de la caractéristique sélectionnée
    st.write("### Définition de la caractéristique sélectionnée")
    st.write(f"**{feature1}:** {feature_definitions.get(feature1, 'Définition non disponible.')}")
    st.write(f"**{feature2}:** {feature_definitions.get(feature2, 'Définition non disponible.')}")

    # Graphique de distribution pour feature1
    fig_feature1 = px.histogram(clients_df, x=feature1, color="TARGET",
                                marginal="box", nbins=30, title=f"Distribution de {feature1}")
    fig_feature1.add_vline(x=features[important_features.columns.get_loc(feature1)], line_width=3, line_dash="dash", line_color="black")
    st.plotly_chart(fig_feature1, key="feature1_distribution_chart")

    # Graphique de distribution pour feature2
    fig_feature2 = px.histogram(clients_df, x=feature2, color="TARGET",
                                marginal="box", nbins=30, title=f"Distribution de {feature2}")
    fig_feature2.add_vline(x=features[important_features.columns.get_loc(feature2)], line_width=3, line_dash="dash", line_color="black")
    st.plotly_chart(fig_feature2, key="feature2_distribution_chart")

    # Analyse bi-variée entre les deux caractéristiques sélectionnées
st.subheader("Analyse Bi-Variée des Caractéristiques")
# Calcul du score temporaire en fonction du seuil
scores_temp = (clients_df['TARGET'].apply(lambda x: 1 if x >= seuil else 0))

# Créer le graphique de dispersion avec les deux caractéristiques sélectionnées
fig_bivar = px.scatter(clients_df, x=feature1, y=feature2, color=scores_temp,
                       color_continuous_scale="Viridis",
                       title=f"Relation entre {feature1} et {feature2}")
# Ajouter un point pour le client sélectionné
fig_bivar.add_scatter(
    x=[features[important_features.columns.get_loc(feature1)]],
    y=[features[important_features.columns.get_loc(feature2)]],
    mode="markers",
    marker=dict(color="red", size=15),
    name="Client Sélectionné"
)

# Afficher le graphique de l'analyse bi-variée
st.plotly_chart(fig_bivar, key="bivariate_analysis_chart")

# Graphique de l'importance globale des caractéristiques
st.subheader("Importance Globale des Caractéristiques")

# Calcul de l'importance globale des caractéristiques en prenant la moyenne sur l'ensemble des clients
global_importance = clients_df[important_features.columns].mean()

# Trier les caractéristiques par ordre d'importance (du plus grand au plus petit)
global_importance_sorted = global_importance.sort_values(ascending=False)

# Création du graphique de l'importance globale avec les 20 caractéristiques les plus importantes
fig_global = px.bar(global_importance_sorted, x=global_importance_sorted.values, y=global_importance_sorted.index,
                    orientation='h', title="Top 20 des Caractéristiques les Plus Importantes")
# Modifier la taille de la figure pour qu'elle soit plus grande et affiche mieux les noms des caractéristiques
fig_global.update_layout(
    yaxis_title="Caractéristiques",
    xaxis_title="Importance Moyenne",
    height=800,  # Augmenter la hauteur de la figure
    margin=dict(l=150, r=20, t=50, b=100)  # Ajuster les marges pour mieux afficher les labels
)

# Afficher le graphique dans Streamlit
st.plotly_chart(fig_global, key="global_importance_chart")
