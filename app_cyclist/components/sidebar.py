import streamlit as st
from utils.auth import logout

def show_sidebar():
    with st.sidebar:
        st.subheader(f"Bonjour, {st.session_state.user_data.get('first_name', 'Utilisateur')}")
        st.write(f"Rôle: {'Administrateur' if st.session_state.is_staff else 'Utilisateur'}")
        
        # Menu adapté selon le rôle
        options = ["Tableau de bord", "Mon profil"]
        
        if st.session_state.is_staff:
            options.extend(["Création d'athlètes", "Gestion des athlètes", "Gestion des performances", "Statistiques"])
        else:
            options.append("Mes performances")
            
        # Ajouter l'option Comparaison générale pour tous les utilisateurs
        options.append("Comparaison générale")
        
        menu = st.radio("Navigation", options)
        
        if st.button("Déconnexion"):
            logout()
            st.rerun()
            
        return menu