import streamlit as st
from utils.auth import show_login_page
from utils.session import initialize_session
from components.sidebar import show_sidebar

st.set_page_config(page_title="Cyclist Performance Dashboard", layout="wide")

initialize_session()

def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        selected_page = show_sidebar()
        
        if selected_page == "Tableau de bord":
            from views.dashboard import show_dashboard
            show_dashboard()
        elif selected_page == "Mon profil":
            from views.profile import show_profile
            show_profile()
        elif selected_page == "Création d'athlètes":
            from views.athlete_creation import show_athlete_creation
            show_athlete_creation()
        elif selected_page == "Gestion des athlètes":
            from views.athlete_management import show_athlete_management
            show_athlete_management()
        elif selected_page == "Gestion des performances":
            from views.performances import show_performances
            show_performances()
        elif selected_page == "Statistiques":
            from views.statistics import show_statistics
            show_statistics()

if __name__ == "__main__":
    main()