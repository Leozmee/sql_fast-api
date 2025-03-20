import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

def login(email, password):
    """Authentification utilisateur via l'API"""
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
    """Enregistrement d'un nouvel utilisateur"""
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
    """Récupère les informations de l'utilisateur connecté"""
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

def logout():
    """Déconnecte l'utilisateur en effaçant les données de session"""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user_id = None
    st.session_state.user_data = None
    st.session_state.is_staff = False
    st.session_state.current_page = "login"

def show_login_page():
    """Affiche la page de connexion/inscription"""
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