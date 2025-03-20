import streamlit as st
from utils.auth import logout

def show_sidebar():
    with st.sidebar:
        st.subheader(f"Bonjour, {st.session_state.user_data.get('first_name', 'Utilisateur')}")
        st.write(f"Rôle: {'Coach' if st.session_state.is_staff else 'Utilisateur'}")
        
        if st.session_state.is_staff:
            menu = st.radio(
                "Navigation",
                ["Tableau de bord", "Mon profil", "Création d'athlètes", "Gestion des athlètes", "Gestion des performances", "Statistiques"],
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
            
        return menu