import streamlit as st
from utils.api import create_athlete

def show_athlete_creation():
    st.title("Création d'un athlète")
    
    # Vérification des permissions
    if not st.session_state.is_staff:
        st.warning("Vous n'avez pas les droits d'administrateur nécessaires pour créer des athlètes.")
        st.info("Veuillez contacter un administrateur si vous avez besoin de créer un profil d'athlète.")
        return
    
    st.subheader("Créer un nouvel athlète")
    with st.form("create_athlete_form"):
        user_id = st.number_input("ID de l'utilisateur", min_value=1, value=1)
        gender = st.selectbox("Genre", ["male", "female"])
        age = st.number_input("Âge", min_value=12, max_value=100, value=25)
        weight = st.number_input("Poids (kg)", min_value=30.0, max_value=200.0, value=70.0)
        height = st.number_input("Taille (cm)", min_value=100.0, max_value=250.0, value=175.0)
        
        submit = st.form_submit_button("Créer l'athlète")
        if submit:
            if create_athlete(user_id, gender, age, weight, height):
                st.success(f"Profil d'athlète créé avec succès pour l'utilisateur ID {user_id}!")