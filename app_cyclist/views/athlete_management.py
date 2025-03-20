import streamlit as st
from utils.api import get_athlete_info, update_athlete
import requests

def show_athlete_management():
    st.title("Gestion des athlètes")
    
    if not st.session_state.is_staff:
        st.warning("Vous n'avez pas les droits d'administrateur nécessaires pour gérer les athlètes.")
        return
    
    st.subheader("Rechercher un athlète")
    
    search_type = st.radio("Rechercher par", ["ID", "Nom"])
    
    if search_type == "ID":
        user_id = st.number_input("ID de l'utilisateur", min_value=1, value=1)
        search_button = st.button("Rechercher")
        
        if search_button:
            show_athlete_details_by_id(user_id)
    else:
        username = st.text_input("Nom d'utilisateur de l'athlète")
        search_button = st.button("Rechercher")
        
        if search_button and username:
            show_athlete_details_by_username(username)

def show_athlete_details_by_id(user_id):

    athlete_data = get_athlete_info(user_id)
    if athlete_data:
        display_athlete_info(user_id, athlete_data)
    else:
        st.error(f"Aucun athlète trouvé avec l'ID {user_id}")

def show_athlete_details_by_username(username):

    API_URL = "http://127.0.0.1:8000"
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    try:
        # Récupérer d'abord l'ID utilisateur à partir du nom
        response = requests.get(f"{API_URL}/performances/all_users", headers=headers)
        
        if response.status_code == 200:
            all_users = response.json()
            user_found = None
            
            for user in all_users:
                if user.get('user_name', '').lower() == username.lower():
                    user_found = user
                    break
            
            if user_found:
                user_id = user_found.get('id')
                athlete_data = get_athlete_info(user_id)
                if athlete_data:
                    display_athlete_info(user_id, athlete_data)
                else:
                    st.error(f"Aucun profil athlète trouvé pour {username}")
            else:
                st.error(f"Aucun utilisateur trouvé avec le nom {username}")
        else:
            st.error("Impossible de récupérer la liste des utilisateurs")
    except Exception as e:
        st.error(f"Erreur: {str(e)}")

def display_athlete_info(user_id, athlete_data):
 
    st.success(f"Athlète trouvé avec ID: {user_id}")
    
    st.subheader("Informations de l'athlète")
    st.write(f"**Genre**: {athlete_data.get('gender', '')}")
    st.write(f"**Âge**: {athlete_data.get('age', '')} ans")
    st.write(f"**Poids**: {athlete_data.get('weight', '')} kg")
    st.write(f"**Taille**: {athlete_data.get('height', '')} cm")
    
    st.subheader("Modifier les informations")
    with st.form("update_athlete_form"):
        gender = st.selectbox("Genre", ["male", "female"], index=0 if athlete_data.get("gender") == "male" else 1)
        age = st.number_input("Âge", min_value=12, max_value=100, value=athlete_data.get("age", 25))
        weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=athlete_data.get("weight", 70.0))
        height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=athlete_data.get("height", 175.0))
        
        submit = st.form_submit_button("Mettre à jour")
        if submit:
            if update_athlete(user_id, gender, age, weight, height):
                st.success("Profil athlète mis à jour avec succès!")
    
    if st.button("Supprimer cet athlète", key="delete_athlete"):
        API_URL = "http://127.0.0.1:8000"
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        try:
            response = requests.delete(f"{API_URL}/athletes/{user_id}", headers=headers)
            
            if response.status_code in [200, 204]:
                st.success("Athlète supprimé avec succès!")
            else:
                st.error("Erreur lors de la suppression de l'athlète")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")