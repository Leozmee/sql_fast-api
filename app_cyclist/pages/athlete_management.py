import streamlit as st
from utils.api import get_athlete_info, update_athlete

def show_athlete_management():
    st.title("Gestion des athlètes")
    
    # Vérification des permissions
    if not st.session_state.is_staff:
        st.warning("Vous n'avez pas les droits d'administrateur nécessaires pour gérer les athlètes.")
        return
    
    # Recherche d'athlète par ID ou nom
    st.subheader("Rechercher un athlète")
    
    search_type = st.radio("Rechercher par", ["ID", "Nom"])
    
    if search_type == "ID":
        user_id = st.number_input("ID de l'utilisateur", min_value=1, value=1)
        search_button = st.button("Rechercher")
        
        if search_button:
            show_athlete_details(user_id)
    else:
        # Note: Dans une application réelle, vous auriez besoin d'un endpoint API pour rechercher par nom
        st.warning("La recherche par nom n'est pas encore implémentée dans l'API. Utilisez l'ID pour l'instant.")
        name = st.text_input("Nom de l'athlète")
        search_button = st.button("Rechercher")
        
        if search_button:
            st.error("Fonctionnalité non disponible. Utiliser la recherche par ID.")

def show_athlete_details(user_id):
    athlete_data = get_athlete_info(user_id)
    
    if athlete_data:
        st.success(f"Athlète trouvé: ID {user_id}")
        
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
            try:
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                response = requests.delete(f"http://127.0.0.1:8000/athletes/{user_id}", headers=headers)
                
                if response.status_code in [200, 204]:
                    st.success("Athlète supprimé avec succès!")
                else:
                    st.error(f"Erreur: {response.json().get('detail', 'Erreur inconnue')}")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
    else:
        st.error(f"Aucun athlète trouvé avec l'ID {user_id}")