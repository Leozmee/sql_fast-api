import streamlit as st

def initialize_session():
    """Initialise les variables d'état de session"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "user_data" not in st.session_state:
        st.session_state.user_data = None
    if "is_staff" not in st.session_state:
        st.session_state.is_staff = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "login"