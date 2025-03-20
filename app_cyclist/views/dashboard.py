import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api import get_stats, get_performances, get_athlete_info, get_user_name_by_id


def show_dashboard():
    st.title("Tableau de bord des performances cyclistes")

    stats = get_stats()
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Athlète le plus fort", stats.get('strongest_athlete', "Non disponible"))
        
        with col2:
            st.metric("Meilleur VO2max", stats.get('highest_vo2max', "Non disponible"))
        
        with col3:
            st.metric("Meilleur ratio puissance/poids", stats.get('best_power_weight_ratio', "Non disponible"))
    
    # Récupérer les performances de l'utilisateur
    if st.session_state.user_id:
        performances = get_performances(st.session_state.user_id)
        if performances:
            st.subheader("Vos dernières performances")
            df = pd.DataFrame(performances)
            if not df.empty:
                st.dataframe(df)
                
                # Graphiques si suffisamment de données
                if len(df) > 1:
                    st.subheader("Analyse des performances")
                    
                    # Graphique de puissance
                    fig1 = px.line(df, x='time', y='power', title="Évolution de la puissance")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Graphique de fréquence cardiaque et VO2max
                    if 'heart_rate' in df.columns and 'vo2_max' in df.columns:
                        fig2 = go.Figure()
                        fig2.add_trace(go.Scatter(x=df['time'], y=df['heart_rate'], mode='lines+markers', name='FC'))
                        fig2.add_trace(go.Scatter(x=df['time'], y=df['vo2_max'], mode='lines+markers', name='VO2max'))
                        fig2.update_layout(title="Fréquence cardiaque et VO2max")
                        st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aucune performance enregistrée. Commencez à ajouter vos données d'entraînement.")