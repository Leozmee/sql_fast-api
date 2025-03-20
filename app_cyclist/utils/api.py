import requests
import streamlit as st
import pandas as pd

API_URL = "http://127.0.0.1:8000"

def get_athlete_info(user_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/athletes/{user_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            st.error("Impossible de récupérer les informations de l'athlète")
            return None
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return None

def create_athlete(user_id, gender, age, weight, height):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/athletes/",
            headers=headers,
            json={
                "user_id": user_id,
                "gender": gender,
                "age": age,
                "weight": weight,
                "height": height
            }
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"Erreur de création d'athlète: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def update_athlete(user_id, gender, age, weight, height):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            f"{API_URL}/athletes/{user_id}",
            headers=headers,
            json={
                "gender": gender,
                "age": age,
                "weight": weight,
                "height": height
            }
        )
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Erreur de mise à jour: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def get_performances(user_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        
        if st.session_state.is_staff:
            response = requests.get(f"{API_URL}/performances/user/{user_id}", headers=headers)
        else:
           
            response = requests.get(f"{API_URL}/performances/my-stats", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Impossible de récupérer les performances (Status: {response.status_code})")
            return []
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return []

def get_stats():
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/performances/stats", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # S'assurer que toutes les clés attendues existent
            if not isinstance(data, dict):
                data = {}
            if "strongest_athlete" not in data:
                data["strongest_athlete"] = None
            if "highest_vo2max" not in data:
                data["highest_vo2max"] = None
            if "best_power_weight_ratio" not in data:
                data["best_power_weight_ratio"] = None
            return data
        else:
            st.error(f"Impossible de récupérer les statistiques (Status: {response.status_code})")
            return {
                "strongest_athlete": None,
                "highest_vo2max": None,
                "best_power_weight_ratio": None
            }
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return {
            "strongest_athlete": None,
            "highest_vo2max": None,
            "best_power_weight_ratio": None
        }

def get_user_name_by_id(user_id):
    try:
        # Cette fonction est une simulation car l'API n'a pas d'endpoint pour ça
        # Dans une application réelle, vous auriez besoin d'un endpoint API
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/users/me", headers=headers)
        
        if response.status_code == 200 and response.json().get("id") == user_id:
            user_data = response.json()
            return f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}"
        
        return f"Utilisateur #{user_id}"
    except Exception as e:
        return f"Utilisateur #{user_id}"

def add_performance(user_id, time, power, vo2_max, oxygen, cadence, heart_rate, respiration_frequency):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.post(
            f"{API_URL}/performances/",
            headers=headers,
            json={
                "user_id": user_id,
                "time": time,
                "power": power,
                "vo2_max": vo2_max,
                "oxygen": oxygen,
                "cadence": cadence,
                "heart_rate": heart_rate,
                "respiration_frequency": respiration_frequency
            }
        )
        
        if response.status_code in [200, 201]:
            return True
        else:
            st.error(f"Erreur d'ajout de performance: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False
    
def get_performance_by_id(performance_id):
    # Cette fonction est une simulation car l'API n'a pas d'endpoint spécifique
    # pour récupérer une performance par ID
    performances = get_performances(st.session_state.user_id)
    for perf in performances:
        if perf.get("performance_id") == performance_id:
            return perf
    return None

def update_performance(performance_id, power, vo2_max, heart_rate, respiration_frequency, cadence):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        
        # Récupérer d'abord les données actuelles de performance
        current_perf = get_performance_by_id(performance_id)
        if not current_perf:
            return False
            
        response = requests.patch(
            f"{API_URL}/performances/{performance_id}",
            headers=headers,
            json={
                "user_id": current_perf["user_id"],
                "time": current_perf["time"],
                "power": power,
                "vo2_max": vo2_max,
                "oxygen": current_perf.get("oxygen", 0),
                "cadence": cadence,
                "heart_rate": heart_rate,
                "respiration_frequency": respiration_frequency
            }
        )
        
        if response.status_code in [200, 202]:
            return True
        else:
            st.error(f"Erreur de mise à jour: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def delete_performance(performance_id):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.delete(
            f"{API_URL}/performances/{performance_id}",
            headers=headers
        )
        
        if response.status_code in [200, 202, 204]:
            return True
        else:
            st.error(f"Erreur de suppression: {response.json().get('detail', 'Erreur inconnue')}")
            return False
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False
    
def get_performances_by_username(username):
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/performances/user_name/{username}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Impossible de récupérer les performances pour {username}")
            return []
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return []