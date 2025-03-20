import streamlit as st
import pandas as pd
import plotly.express as px
from utils.api import get_performances, add_performance, update_performance, delete_performance

def show_performances():
    # Détermine si c'est une vue admin ou utilisateur
    is_admin_view = st.session_state.is_staff
    
    if is_admin_view:
        st.title("Gestion des performances")
    else:
        st.title("Mes performances")
        
    # Afficher les performances existantes
    performances = get_performances(st.session_state.user_id)
    
    if performances:
        st.subheader("Historique des performances")
        df = pd.DataFrame(performances)
        
        # Formater les colonnes pour une meilleure lisibilité
        if not df.empty:
            st.dataframe(df.style.format({
                'power': '{:.1f}',
                'vo2_max': '{:.1f}',
                'heart_rate': '{:.0f}',
                'cadence': '{:.0f}',
                'respiration_frequency': '{:.0f}'
            }))
            
            # Visualisations
            if len(df) > 1:
                st.subheader("Analyse des performances")
                tab1, tab2, tab3 = st.tabs(["Puissance", "Fréquence cardiaque", "VO2max"])
                
                with tab1:
                    fig = px.line(df, x='time', y='power', title="Évolution de la puissance")
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    fig = px.line(df, x='time', y='heart_rate', title="Évolution de la fréquence cardiaque")
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    fig = px.line(df, x='time', y='vo2_max', title="Évolution du VO2max")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Seul un admin peut modifier/supprimer des performances
            if is_admin_view:
                st.subheader("Modifier ou supprimer une performance")
                
                perf_id = st.selectbox("Sélectionner une performance", 
                                      options=df['performance_id'].tolist(),
                                      format_func=lambda x: f"ID: {x} - Temps: {df[df['performance_id']==x]['time'].values[0]}s")
                
                if perf_id:
                    selected_perf = df[df['performance_id'] == perf_id].iloc[0].to_dict()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Modifier la performance")
                        with st.form("update_performance_form"):
                            power = st.number_input("Puissance (watts)", min_value=0.0, value=float(selected_perf['power']))
                            vo2_max = st.number_input("VO2max", min_value=0.0, value=float(selected_perf['vo2_max']))
                            heart_rate = st.number_input("Fréq. cardiaque (bpm)", min_value=0.0, value=float(selected_perf['heart_rate']))
                            resp_freq = st.number_input("Fréq. respiratoire", min_value=0.0, value=float(selected_perf['respiration_frequency']))
                            cadence = st.number_input("Cadence (rpm)", min_value=0.0, value=float(selected_perf['cadence']))
                            
                            submit = st.form_submit_button("Mettre à jour")
                            if submit:
                                if update_performance(perf_id, power, vo2_max, heart_rate, resp_freq, cadence):
                                    st.success("Performance mise à jour avec succès!")
                                    st.rerun()
                    
                    with col2:
                        st.subheader("Supprimer la performance")
                        st.warning("Attention: cette action est irréversible!")
                        if st.button("Supprimer cette performance", key="delete_perf"):
                            if delete_performance(perf_id):
                                st.success("Performance supprimée avec succès!")
                                st.rerun()
    else:
        st.info("Aucune performance enregistrée.")
    
    # Seul un admin peut ajouter des performances
    if is_admin_view:
        st.subheader("Ajouter une nouvelle performance")
        with st.form("add_performance_form"):
            user_id = st.number_input("ID Utilisateur", min_value=1, value=st.session_state.user_id)
            time = st.number_input("Temps (secondes)", min_value=1, value=600)
            power = st.number_input("Puissance (watts)", min_value=0.0, value=200.0)
            vo2_max = st.number_input("VO2max", min_value=0.0, value=45.0)
            oxygen = st.number_input("Consommation d'oxygène (ml/kg/min)", min_value=0, value=40)
            cadence = st.number_input("Cadence (rpm)", min_value=0.0, value=90.0)
            heart_rate = st.number_input("Fréquence cardiaque (bpm)", min_value=0.0, value=150.0)
            respiration_freq = st.number_input("Fréquence respiratoire (rpm)", min_value=0.0, value=30.0)
            
            submit = st.form_submit_button("Ajouter performance")
            if submit:
                if add_performance(user_id, time, power, vo2_max, oxygen, cadence, heart_rate, respiration_freq):
                    st.success("Performance ajoutée avec succès!")
                    st.rerun()