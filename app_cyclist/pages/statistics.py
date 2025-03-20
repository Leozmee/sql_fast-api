import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api import get_stats, get_performances, get_athlete_info, get_user_name_by_id

def show_statistics():
    st.title("Statistiques globales")
    
    # Vérification des permissions
    if not st.session_state.is_staff:
        st.warning("Vous n'avez pas les droits d'administrateur nécessaires pour voir les statistiques globales.")
        return
    
    stats = get_stats()
    if stats:
        st.subheader("Meilleurs athlètes")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            strongest_id = stats.get('strongest_athlete')
            strongest_name = get_user_name_by_id(strongest_id) if strongest_id else "N/A"
            st.metric("Athlète le plus fort", strongest_name)
            
            if strongest_id:
                athlete = get_athlete_info(strongest_id)
                if athlete:
                    st.write(f"ID: {strongest_id}")
                    st.write(f"Âge: {athlete.get('age')} ans")
                    st.write(f"Poids: {athlete.get('weight')} kg")
        
        with col2:
            vo2max_id = stats.get('highest_vo2max')
            vo2max_name = get_user_name_by_id(vo2max_id) if vo2max_id else "N/A"
            st.metric("Meilleur VO2max", vo2max_name)
            
            if vo2max_id:
                athlete = get_athlete_info(vo2max_id)
                if athlete:
                    st.write(f"ID: {vo2max_id}")
                    st.write(f"Âge: {athlete.get('age')} ans")
                    st.write(f"Poids: {athlete.get('weight')} kg")
        
        with col3:
            ratio_id = stats.get('best_power_weight_ratio')
            ratio_name = get_user_name_by_id(ratio_id) if ratio_id else "N/A"
            st.metric("Meilleur ratio puissance/poids", ratio_name)
            
            if ratio_id:
                athlete = get_athlete_info(ratio_id)
                if athlete:
                    st.write(f"ID: {ratio_id}")
                    st.write(f"Âge: {athlete.get('age')} ans")
                    st.write(f"Poids: {athlete.get('weight')} kg")
        
        # Comparaison des athlètes
        st.subheader("Comparaison des performances")
        st.info("Veuillez sélectionner des athlètes à comparer")
        
        # Options pour sélectionner les athlètes
        comparison_type = st.radio("Sélectionner par", ["ID", "Nom"])
        
        if comparison_type == "ID":
            athlete_ids = st.multiselect(
                "Sélectionner des athlètes à comparer (par ID)", 
                options=list(range(1, 10))  # Simule les IDs de 1 à 9
            )
        else:
            st.warning("La sélection par nom n'est pas encore implémentée dans l'API. Utilisez l'ID pour l'instant.")
            athlete_ids = []
        
        if athlete_ids:
            performance_data = []
            for aid in athlete_ids:
                perfs = get_performances(aid)
                if perfs:
                    # Calcule la puissance moyenne pour chaque athlète
                    avg_power = sum(p.get('power', 0) for p in perfs) / len(perfs) if perfs else 0
                    performance_data.append({
                        'athlete_id': aid,
                        'athlete_name': get_user_name_by_id(aid),
                        'avg_power': avg_power,
                        'max_power': max(p.get('power', 0) for p in perfs) if perfs else 0,
                        'avg_vo2max': sum(p.get('vo2_max', 0) for p in perfs) / len(perfs) if perfs else 0,
                        'num_performances': len(perfs)
                    })
            
            if performance_data:
                perf_df = pd.DataFrame(performance_data)
                
                # Graphique de comparaison de puissance
                fig1 = px.bar(
                    perf_df, 
                    x='athlete_name', 
                    y=['avg_power', 'max_power'],
                    barmode='group',
                    title="Comparaison de la puissance par athlète"
                )
                st.plotly_chart(fig1, use_container_width=True)
                
                # Graphique de comparaison de VO2max
                fig2 = px.bar(
                    perf_df, 
                    x='athlete_name', 
                    y='avg_vo2max',
                    title="Comparaison du VO2max moyen par athlète"
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Aucune donnée de performance disponible pour les athlètes sélectionnés")
    else:
        st.warning("Aucune statistique disponible pour le moment. Ajoutez des performances pour générer des statistiques.")