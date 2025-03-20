import streamlit as st
from utils.auth import show_login_page
from utils.session import initialize_session
from components.sidebar import show_sidebar

# Configuration de la page
st.set_page_config(page_title="Cyclist Performance Dashboard", layout="wide")

# Initialiser l'état de session
initialize_session()

# Cacher les éléments par défaut de navigation
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    .css-ztfqz8.e1ewe7hr3, .css-16idsys.e1ewe7hr3 {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Navigation principale de l'application
def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        # Afficher la barre latérale avec navigation
        selected_page = show_sidebar()
        
        # Importer et afficher la page sélectionnée
        if selected_page == "Tableau de bord":
            from pages.dashboard import show_dashboard
            show_dashboard()
        elif selected_page == "Mon profil":
            from pages.profile import show_profile
            show_profile()
        elif selected_page == "Création d'athlètes":
            from pages.athlete_creation import show_athlete_creation
            show_athlete_creation()
        elif selected_page == "Gestion des athlètes":
            from pages.athlete_management import show_athlete_management
            show_athlete_management()
        elif selected_page == "Gestion des performances":
            from pages.performances import show_performances
            show_performances()
        elif selected_page == "Statistiques":
            from pages.statistics import show_statistics
            show_statistics()

if __name__ == "__main__":
    main()