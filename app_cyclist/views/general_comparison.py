import streamlit as st

def show_general_comparison():
    st.title("Comparaison générale")
    
    st.write("Ce tableau de bord présente une comparaison de la moyenne de chaque statistique de performance entre les utilisateurs.")
    
    # URL de votre tableau de bord Metabase public
    metabase_url = "http://localhost:3000/public/dashboard/520e4f4a-7483-4563-8473-9e1c8011d0db"
    
    # Intégration du tableau de bord Metabase dans un iframe
    st.components.v1.iframe(
        metabase_url,
        height=800,  # Hauteur de l'iframe en pixels
        scrolling=True
    )
    
    st.info("Note: Ce tableau de bord est alimenté par Metabase et montre les données en temps réel de la base de données.")