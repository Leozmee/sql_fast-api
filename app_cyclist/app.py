import streamlit as st
from utils.auth import show_login_page
from utils.session import initialize_session
from components.sidebar import show_sidebar

# Configuration de la page
st.set_page_config(page_title="CycleTrack Pro", layout="wide")

# Initialisation de la session
initialize_session()

# Style sportif dynamique
sports_style = """
<style>
    /* Palette de couleurs */
    :root {
        --primary: #FF5722;
        --secondary: #2E7D32;
        --background: #F5F5F5;
        --sidebar-bg: #303030;
        --text-light: #FFFFFF;
        --text-dark: #212121;
        --accent: #FFC107;
    }
    
    /* Corps principal */
    .main {
        background-color: var(--background);
        color: var(--text-dark);
        font-family: 'Roboto', sans-serif;
    }
    
    /* Barre latérale */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        color: var(--text-light);
    }
    
    /* Titres */
    h1 {
        color: var(--primary) !important;
        font-weight: 800 !important;
        font-size: 2.2rem !important;
        text-transform: uppercase;
        border-bottom: 4px solid var(--primary);
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: var(--secondary) !important;
        font-weight: 700 !important;
    }
    
    h3 {
        color: var(--text-dark) !important;
        font-weight: 600 !important;
    }
    
    /* Boutons */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #E64A19;
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Métriques */
    [data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-weight: 800 !important;
    }
    
    /* Widgets */
    .stSelectbox {
        border-radius: 4px;
    }
    
    /* Masquer navigation dupliquée */
    [data-testid="collapsedControl"] {display: none !important;}
    nav {display: none !important;}
    header {display: none !important;}
    footer {display: none !important;}
</style>
"""

st.markdown(sports_style, unsafe_allow_html=True)

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