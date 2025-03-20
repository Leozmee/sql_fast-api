import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration de l'API
API_URL = "http://127.0.0.1:8000"

# Configuration de la page Streamlit
st.set_page_config(page_title="Cyclist Performance Dashboard", layout="wide")

# Initialisation des états de session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "is_staff" not in st.session_state:
    st.session_state.is_staff = False
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# Fonctions pour interagir avec l'API
def login(email, password):
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.authenticated = True
            
            # Récupérer les informations de l'utilisateur
            user_data = get_user_info()
            if user_data:
                st.session_state.user_data = user_data
                st.session_state.user_id = user_data.get("id")
                st.session_state.is_staff = user_data.get("is_staff", False)
            
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")
        return False

def register(first_name, last_name, user_name, email, password, is_staff="NO"):
    try:
        response = requests.post(
            f"{API_URL}/users/register",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "user_name": user_name,
                "email": email,
                "password": password,
                "is_staff": is_staff
            }
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"Erreur d'enregistrement: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur d'enregistrement: {str(e)}")
        return False

def get_user_info():
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/users/me", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Impossible de récupérer les informations utilisateur")
            return None
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return None

def get_athlete_info(user_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/athletes/{user_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            st.error("Impossible de récupérer les informations de l'athlète")
            return None
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return None

def create_athlete(user_id, gender, age, weight, height):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/athletes/",
            headers=headers,
            json={
                "user_id": user_id,
                "gender": gender,
                "age": age,
                "weight": weight,
                "height": height
            }
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"Erreur de création d'athlète: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def update_athlete(user_id, gender, age, weight, height):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            f"{API_URL}/athletes/{user_id}",
            headers=headers,
            json={
                "gender": gender,
                "age": age,
                "weight": weight,
                "height": height
            }
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Erreur de mise à jour: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def get_performances(user_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        # Si l'utilisateur est admin, utiliser la route staff
        if st.session_state.is_staff:
            response = requests.get(f"{API_URL}/performances/user/{user_id}", headers=headers)
        else:
            # Sinon, utiliser la route pour voir ses propres performances
            response = requests.get(f"{API_URL}/performances/my-stats", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Impossible de récupérer les performances")
            return []
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return []

def add_performance(user_id, time, power, vo2_max, oxygen, cadence, heart_rate, respiration_frequency):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/performances/",
            headers=headers,
            json={
                "user_id": user_id,
                "time": time,
                "power": power,
                "vo2_max": vo2_max,
                "oxygen": oxygen,
                "cadence": cadence,
                "heart_rate": heart_rate,
                "respiration_frequency": respiration_frequency
            }
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"Erreur d'ajout de performance: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def update_performance(performance_id, power, vo2_max, heart_rate, respiration_frequency, cadence):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        
        # Récupérer d'abord les données actuelles de performance
        current_perf = get_performance_by_id(performance_id)
        if not current_perf:
            return False
            
        response = requests.patch(
            f"{API_URL}/performances/{performance_id}",
            headers=headers,
            json={
                "user_id": current_perf["user_id"],
                "time": current_perf["time"],
                "power": power,
                "vo2_max": vo2_max,
                "oxygen": current_perf["oxygen"],
                "cadence": cadence,
                "heart_rate": heart_rate,
                "respiration_frequency": respiration_frequency
            }
        )
        
        if response.status_code in [200, 202]:
            return True
        else:
            st.error(f"Erreur de mise à jour: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def get_performance_by_id(performance_id):
    # Cette fonction est une simulation car l'API n'a pas d'endpoint spécifique
    # pour récupérer une performance par ID
    performances = get_performances(st.session_state.user_id)
    for perf in performances:
        if perf.get("performance_id") == performance_id:
            return perf
    return None

def delete_performance(performance_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.delete(
            f"{API_URL}/performances/{performance_id}",
            headers=headers
        )
        
        if response.status_code in [200, 202, 204]:
            return True
        else:
            st.error(f"Erreur de suppression: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def get_stats():
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/performances/stats", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Impossible de récupérer les statistiques")
            return None
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return None

def logout():
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user_id = None
    st.session_state.user_data = None
    st.session_state.is_staff = False
    st.session_state.current_page = "login"

# Interface utilisateur - Page de connexion
def show_login_page():
    st.title("Cyclist Performance Management System")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Connexion")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Mot de passe", type="password", key="login_password")
        
        if st.button("Se connecter"):
            if login(email, password):
                st.success("Connexion réussie!")
                st.session_state.current_page = "dashboard"
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    
    with col2:
        st.subheader("Inscription")
        first_name = st.text_input("Prénom")
        last_name = st.text_input("Nom")
        user_name = st.text_input("Nom d'utilisateur")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Mot de passe", type="password", key="reg_password")
        is_staff = st.selectbox("Rôle", ["Utilisateur standard", "Administrateur"])
        is_staff_value = "YES" if is_staff == "Administrateur" else "NO"
        
        if st.button("S'inscrire"):
            if register(first_name, last_name, user_name, reg_email, reg_password, is_staff_value):
                st.success("Inscription réussie! Vous pouvez maintenant vous connecter.")
            else:
                st.error("Erreur lors de l'inscription")

# Interface utilisateur - Tableau de bord
def show_dashboard():
    # Barre latérale avec navigation
    with st.sidebar:
        st.subheader(f"Bonjour, {st.session_state.user_data.get('first_name', 'Utilisateur')}")
        st.write(f"Rôle: {'Administrateur' if st.session_state.is_staff else 'Utilisateur'}")
        
        # Menu adapté selon le rôle
        if st.session_state.is_staff:
            menu = st.radio(
                "Navigation",
                ["Tableau de bord", "Mon profil", "Gestion des athlètes", "Gestion des performances", "Statistiques"],
                index=0
            )
        else:
            menu = st.radio(
                "Navigation",
                ["Tableau de bord", "Mon profil", "Mes performances"],
                index=0
            )
        
        if st.button("Déconnexion"):
            logout()
            st.rerun()
    
    # Contenu principal
    if menu == "Tableau de bord":
        st.title("Tableau de bord des performances cyclistes")
        
        # Récupérer les stats (accessible à tout le monde)
        stats = get_stats()
        if stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Athlète le plus fort", f"ID: {stats.get('strongest_athlete', 'N/A')}")
            
            with col2:
                st.metric("Meilleur VO2max", f"ID: {stats.get('highest_vo2max', 'N/A')}")
                
                # Récupérer infos supplémentaires
                if stats.get('highest_vo2max'):
                    athlete = get_athlete_info(stats.get('highest_vo2max'))
                    if athlete:
                        st.write(f"Âge: {athlete.get('age')} ans")
                        st.write(f"Poids: {athlete.get('weight')} kg")
            
            with col3:
                st.metric("Meilleur ratio puissance/poids", f"ID: {stats.get('best_power_weight_ratio', 'N/A')}")
                
                # Récupérer infos supplémentaires
                if stats.get('best_power_weight_ratio'):
                    athlete = get_athlete_info(stats.get('best_power_weight_ratio'))
                    if athlete:
                        st.write(f"Âge: {athlete.get('age')} ans")
                        st.write(f"Poids: {athlete.get('weight')} kg")
        
        # Récupérer les performances de l'utilisateur
        if st.session_state.user_id:
            performances = get_performances(st.session_state.user_id)
            if performances:
                st.subheader("Vos dernières performances")
                df = pd.DataFrame(performances)
                if not df.empty:
                    st.dataframe(df)
                    
                    # Graphiques si suffisamment de données
                    if len(df) > 1:
                        st.subheader("Analyse des performances")
                        
                        # Graphique de puissance
                        fig1 = px.line(df, x='time', y='power', title="Évolution de la puissance")
                        st.plotly_chart(fig1, use_container_width=True)
                        
                        # Graphique de fréquence cardiaque et VO2max
                        fig2 = go.Figure()
                        fig2.add_trace(go.Scatter(x=df['time'], y=df['heart_rate'], mode='lines+markers', name='FC'))
                        fig2.add_trace(go.Scatter(x=df['time'], y=df['vo2_max'], mode='lines+markers', name='VO2max'))
                        fig2.update_layout(title="Fréquence cardiaque et VO2max")
                        st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Aucune performance enregistrée. Commencez à ajouter vos données d'entraînement.")
    
    elif menu == "Mon profil":
        st.title("Mon profil")
        
        # Infos utilisateur
        st.subheader("Informations utilisateur")
        if st.session_state.user_data:
            user_data = st.session_state.user_data
            st.write(f"**Nom**: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
            st.write(f"**Nom d'utilisateur**: {user_data.get('user_name', '')}")
            st.write(f"**Email**: {user_data.get('email', '')}")
            st.write(f"**Rôle**: {'Administrateur' if user_data.get('is_staff', False) else 'Utilisateur standard'}")
            
        # Infos athlète - Note: les utilisateurs standards peuvent voir leurs infos mais pas les modifier
        st.subheader("Informations athlète")
        athlete_data = None
        try:
            athlete_data = get_athlete_info(st.session_state.user_id)
        except:
            st.warning("Vous n'avez pas accès à ces informations.")
        
        if athlete_data:
            st.write(f"**Genre**: {athlete_data.get('gender', '')}")
            st.write(f"**Âge**: {athlete_data.get('age', '')} ans")
            st.write(f"**Poids**: {athlete_data.get('weight', '')} kg")
            st.write(f"**Taille**: {athlete_data.get('height', '')} cm")
            
            # Seul un admin peut modifier les données
            if st.session_state.is_staff:
                st.subheader("Modifier les informations athlète")
                with st.form("update_athlete_form"):
                    gender = st.selectbox("Genre", ["male", "female"], index=0 if athlete_data.get("gender") == "male" else 1)
                    age = st.number_input("Âge", min_value=12, max_value=100, value=athlete_data.get("age", 25))
                    weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=athlete_data.get("weight", 70.0))
                    height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=athlete_data.get("height", 175.0))
                    
                    submit = st.form_submit_button("Mettre à jour")
                    if submit:
                        if update_athlete(st.session_state.user_id, gender, age, weight, height):
                            st.success("Profil mis à jour avec succès!")
                            st.rerun()
        elif st.session_state.is_staff:
            # Seul un admin peut créer un profil athlète
            st.info("Aucun profil athlète trouvé. Créez-en un maintenant.")
            with st.form("create_athlete_form"):
                st.subheader("Créer mon profil d'athlète")
                gender = st.selectbox("Genre", ["male", "female"])
                age = st.number_input("Âge", min_value=12, max_value=100, value=25)
                weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=70.0)
                height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=175.0)
                
                submit = st.form_submit_button("Créer profil")
                if submit:
                    if create_athlete(st.session_state.user_id, gender, age, weight, height):
                        st.success("Profil créé avec succès!")
                        st.rerun()
        else:
            st.info("Aucun profil athlète trouvé. Contactez l'administrateur pour en créer un.")
    
    elif menu == "Mes performances" or menu == "Gestion des performances":
        is_admin_view = menu == "Gestion des performances"
        
        if is_admin_view:
            st.title("Gestion des performances")
        else:
            st.title("Mes performances")
            
        # Afficher les performances existantes
        performances = get_performances(st.session_state.user_id)
        
        if performances:
            st.subheader("Historique des performances")
            df = pd.DataFrame(performances)
            
            # Formater les colonnes pour une meilleure lisibilité
            if not df.empty:
                st.dataframe(df.style.format({
                    'power': '{:.1f}',
                    'vo2_max': '{:.1f}',
                    'heart_rate': '{:.0f}',
                    'cadence': '{:.0f}',
                    'respiration_frequency': '{:.0f}'
                }))
                
                # Visualisations
                if len(df) > 1:
                    st.subheader("Analyse des performances")
                    tab1, tab2, tab3 = st.tabs(["Puissance", "Fréquence cardiaque", "VO2max"])
                    
                    with tab1:
                        fig = px.line(df, x='time', y='power', title="Évolution de la puissance")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab2:
                        fig = px.line(df, x='time', y='heart_rate', title="Évolution de la fréquence cardiaque")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with tab3:
                        fig = px.line(df, x='time', y='vo2_max', title="Évolution du VO2max")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Seul un admin peut modifier/supprimer des performances
                if is_admin_view:
                    st.subheader("Modifier ou supprimer une performance")
                    
                    perf_id = st.selectbox("Sélectionner une performance", 
                                          options=df['performance_id'].tolist(),
                                          format_func=lambda x: f"ID: {x} - Temps: {df[df['performance_id']==x]['time'].values[0]}s")
                    
                    if perf_id:
                        selected_perf = df[df['performance_id'] == perf_id].iloc[0].to_dict()
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Modifier la performance")
                            with st.form("update_performance_form"):
                                power = st.number_input("Puissance (watts)", min_value=0.0, value=float(selected_perf['power']))
                                vo2_max = st.number_input("VO2max", min_value=0.0, value=float(selected_perf['vo2_max']))
                                heart_rate = st.number_input("Fréq. cardiaque (bpm)", min_value=0.0, value=float(selected_perf['heart_rate']))
                                resp_freq = st.number_input("Fréq. respiratoire", min_value=0.0, value=float(selected_perf['respiration_frequency']))
                                cadence = st.number_input("Cadence (rpm)", min_value=0.0, value=float(selected_perf['cadence']))
                                
                                submit = st.form_submit_button("Mettre à jour")
                                if submit:
                                    if update_performance(perf_id, power, vo2_max, heart_rate, resp_freq, cadence):
                                        st.success("Performance mise à jour avec succès!")
                                        st.rerun()
                        
                        with col2:
                            st.subheader("Supprimer la performance")
                            st.warning("Attention: cette action est irréversible!")
                            if st.button("Supprimer cette performance", key="delete_perf"):
                                if delete_performance(perf_id):
                                    st.success("Performance supprimée avec succès!")
                                    st.rerun()
        else:
            st.info("Aucune performance enregistrée.")
        
        # Seul un admin peut ajouter des performances
        if is_admin_view:
            st.subheader("Ajouter une nouvelle performance")
            with st.form("add_performance_form"):
                user_id = st.number_input("ID Utilisateur", min_value=1, value=st.session_state.user_id)
                time = st.number_input("Temps (secondes)", min_value=1, value=600)
                power = st.number_input("Puissance (watts)", min_value=0.0, value=200.0)
                vo2_max = st.number_input("VO2max", min_value=0.0, value=45.0)
                oxygen = st.number_input("Consommation d'oxygène (ml/kg/min)", min_value=0, value=40)
                cadence = st.number_input("Cadence (rpm)", min_value=0.0, value=90.0)
                heart_rate = st.number_input("Fréquence cardiaque (bpm)", min_value=0.0, value=150.0)
                respiration_freq = st.number_input("Fréquence respiratoire (rpm)", min_value=0.0, value=30.0)
                
                submit = st.form_submit_button("Ajouter performance")
                if submit:
                    if add_performance(user_id, time, power, vo2_max, oxygen, cadence, heart_rate, respiration_freq):
                        st.success("Performance ajoutée avec succès!")
                        st.rerun()
    
    elif menu == "Gestion des athlètes" and st.session_state.is_staff:
        st.title("Gestion des athlètes")
        
        # Cette fonctionnalité est limitée par l'API actuelle car nous n'avons pas 
        # d'endpoint pour lister tous les utilisateurs/athlètes
        # Simulons une interface simplifiée
        
        user_id = st.number_input("ID de l'utilisateur à gérer", min_value=1, value=1)
        
        if st.button("Rechercher"):
            athlete_data = get_athlete_info(user_id)
            
            if athlete_data:
                st.success(f"Athlète trouvé: ID {user_id}")
                
                st.subheader("Informations de l'athlète")
                st.write(f"**Genre**: {athlete_data.get('gender', '')}")
                st.write(f"**Âge**: {athlete_data.get('age', '')} ans")
                st.write(f"**Poids**: {athlete_data.get('weight', '')} kg")
                st.write(f"**Taille**: {athlete_data.get('height', '')} cm")
                
                st.subheader("Modifier les informations")
                with st.form("update_other_athlete_form"):
                    gender = st.selectbox("Genre", ["male", "female"], index=0 if athlete_data.get("gender") == "male" else 1)
                    age = st.number_input("Âge", min_value=12, max_value=100, value=athlete_data.get("age", 25))
                    weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=athlete_data.get("weight", 70.0))
                    height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=athlete_data.get("height", 175.0))
                    
                    submit = st.form_submit_button("Mettre à jour")
                    if submit:
                        if update_athlete(user_id, gender, age, weight, height):
                            st.success("Profil athlète mis à jour avec succès!")
                
                if st.button("Supprimer cet athlète", key="delete_athlete"):
                    try:
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        response = requests.delete(f"{API_URL}/athletes/{user_id}", headers=headers)
                        
                        if response.status_code in [200, 204]:
                            st.success("Athlète supprimé avec succès!")
                        else:
                            st.error(f"Erreur: {response.json().get('detail', 'Erreur inconnue')}")
                    except Exception as e:
                        st.error(f"Erreur: {str(e)}")
            else:
                st.error(f"Aucun athlète trouvé avec l'ID {user_id}")
                
                st.subheader("Créer un nouveau profil d'athlète")
                with st.form("create_new_athlete_form"):
                    gender = st.selectbox("Genre", ["male", "female"])
                    age = st.number_input("Âge", min_value=12, max_value=100, value=25)
                    weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=70.0)
                    height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=175.0)
                    
                    submit = st.form_submit_button("Créer profil")
                    if submit:
                        if create_athlete(user_id, gender, age, weight, height):
                            st.success(f"Profil créé avec succès pour l'utilisateur ID {user_id}!")
    
    elif menu == "Statistiques" and st.session_state.is_staff:
        st.title("Statistiques globales")
        
        stats = get_stats()
        if stats:
            st.subheader("Meilleurs athlètes")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Athlète le plus fort", f"ID: {stats.get('strongest_athlete', 'N/A')}")
                
                # Si on a l'ID, on pourrait essayer de récupérer plus d'info
                if stats.get('strongest_athlete'):
                    athlete = get_athlete_info(stats.get('strongest_athlete'))
                    if athlete:
                        st.write(f"Âge: {athlete.get('age')} ans")
                        st.write(f"Poids: {athlete.get('weight')} kg")
            
            with col2:
                st.metric("Meilleur VO2max", f"ID: {stats.get('highest_vo2max', 'N/A')}")
                
                # Récupérer infos supplémentaires
                if stats.get('highest_vo2max'):
                    athlete = get_athlete_info(stats.get('highest_vo2max'))
                    if athlete:
                        st.write(f"Âge: {athlete.get('age')} ans")
                        st.write(f"Poids: {athlete.get('weight')} kg")
            
            with col3:
                st.metric("Meilleur ratio puissance/poids", f"ID: {stats.get('best_power_weight_ratio', 'N/A')}")
                
                # Récupérer infos supplémentaires
                if stats.get('best_power_weight_ratio'):
                    athlete = get_athlete_info(stats.get('best_power_weight_ratio'))
                    if athlete:
                        st.write(f"Âge: {athlete.get('age')} ans")
                        st.write(f"Poids: {athlete.get('weight')} kg")
            
            # Afficher un graphique comparatif
            st.subheader("Comparaison des performances")
            st.info("Veuillez sélectionner des athlètes à comparer")
            
            # Simuler une interface de comparaison
            athlete_ids = st.multiselect(
                "Sélectionner des athlètes à comparer (par ID)", 
                options=list(range(1, 10))  # Simule les IDs de 1 à 9
            )
            
            if athlete_ids:
                performance_data = []
                for aid in athlete_ids:
                    perfs = get_performances(aid)
                    if perfs:
                        # Calcule la puissance moyenne pour chaque athlète
                        avg_power = sum(p.get('power', 0) for p in perfs) / len(perfs) if perfs else 0
                        performance_data.append({
                            'athlete_id': aid,
                            'avg_power': avg_power,
                            'max_power': max(p.get('power', 0) for p in perfs) if perfs else 0,
                            'avg_vo2max': sum(p.get('vo2_max', 0) for p in perfs) / len(perfs) if perfs else 0,
                            'num_performances': len(perfs)
                        })
                
                if performance_data:
                    perf_df = pd.DataFrame(performance_data)
                    
                    # Graphique de comparaison de puissance
                    fig1 = px.bar(
                        perf_df, 
                        x='athlete_id', 
                        y=['avg_power', 'max_power'],
                        barmode='group',
                        title="Comparaison de la puissance par athlète"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Graphique de comparaison de VO2max
                    fig2 = px.bar(
                        perf_df, 
                        x='athlete_id', 
                        y='avg_vo2max',
                        title="Comparaison du VO2max moyen par athlète"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("Aucune donnée de performance disponible pour les athlètes sélectionnés")
        else:
            st.warning("Aucune statistique disponible pour le moment. Ajoutez des performances pour générer des statistiques.")

# Navigation principale de l'application
def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()