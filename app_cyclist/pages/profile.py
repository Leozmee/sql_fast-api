import streamlit as st
from utils.api import get_athlete_info, get_user_name_by_id

def show_profile():
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
        st.warning("Impossible de récupérer les informations d'athlète.")
    
    if athlete_data:
        st.write(f"**Genre**: {athlete_data.get('gender', '')}")
        st.write(f"**Âge**: {athlete_data.get('age', '')} ans")
        st.write(f"**Poids**: {athlete_data.get('weight', '')} kg")
        st.write(f"**Taille**: {athlete_data.get('height', '')} cm")
    else:
        st.info("Aucun profil athlète trouvé. Si vous êtes un athlète, contactez l'administrateur pour créer votre profil.")