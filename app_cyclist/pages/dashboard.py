import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api import get_stats, get_performances, get_athlete_info, get_user_name_by_id

def show_dashboard():
    st.title("Tableau de bord des performances cyclistes")
    
    # Récupérer les stats
    stats = get_stats()
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            strongest_id = stats.get('strongest_athlete')
            strongest_name = get_user_name_by_id(strongest_id) if strongest_id else "N/A"
            st.metric("Athlète le plus fort", strongest_name)
        
        with col2:
            vo2max_id = stats.get('highest_vo2max')
            vo2max_name = get_user_name_by_id(vo2max_id) if vo2max_id else "N/A"
            st.metric("Meilleur VO2max", vo2max_name)
            
            # Récupérer infos supplémentaires
            if vo2max_id:
                athlete = get_athlete_info(vo2max_id)
                if athlete:
                    st.write(f"Âge: {athlete.get('age')} ans")
                    st.write(f"Poids: {athlete.get('weight')} kg")
        
        with col3:
            ratio_id = stats.get('best_power_weight_ratio')
            ratio_name = get_user_name_by_id(ratio_id) if ratio_id else "N/A"
            st.metric("Meilleur ratio puissance/poids", ratio_name)
            
            # Récupérer infos supplémentaires
            if ratio_id:
                athlete = get_athlete_info(ratio_id)
                if athlete:
                    st.write(f"Âge: {athlete.get('age')} ans")
                    st.write(f"Poids: {athlete.get('weight')} kg")
    
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
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(x=df['time'], y=df['heart_rate'], mode='lines+markers', name='FC'))
                    fig2.add_trace(go.Scatter(x=df['time'], y=df['vo2_max'], mode='lines+markers', name='VO2max'))
                    fig2.update_layout(title="Fréquence cardiaque et VO2max")
                    st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aucune performance enregistrée. Commencez à ajouter vos données d'entraînement.")