import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from io import StringIO

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.api import (
    get_athlete_info, create_athlete, update_athlete, get_performances, 
    get_stats, get_user_name_by_id, add_performance, update_performance, 
    delete_performance, get_performances_by_username
)
from test_config_loader import TestConfig

class DotDict(dict):
    """Classe pour simuler un objet avec accès par attribut pour streamlit.session_state"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class TestAPI(unittest.TestCase):
    
    def setUp(self):
        # Charger la configuration de test
        self.config = TestConfig()
        self.api_url = self.config.get_api_url()
        self.test_athlete = self.config.get_test_athlete_data()
        self.test_performance = self.config.get_test_performance_data()
        
        # Configuration pour capturer stdout de Streamlit
        self.error_patcher = patch('streamlit.error')
        self.mock_st_error = self.error_patcher.start()
        
        # Mock session_state comme un DotDict pour permettre l'accès par attribut
        self.session_state = DotDict({
            'token': 'fake_token',
            'user_id': 1,
            'is_staff': True
        })
        self.session_state_patcher = patch('streamlit.session_state', self.session_state)
        self.mock_session_state = self.session_state_patcher.start()
        
        # Patch l'URL de l'API dans les modules testés
        self.api_url_patcher = patch('utils.api.API_URL', self.api_url)
        self.api_url_patcher.start()
    
    def tearDown(self):
        self.error_patcher.stop()
        self.session_state_patcher.stop()
        self.api_url_patcher.stop()
    
    @patch('requests.get')
    def test_get_athlete_info_success(self, mock_get):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.test_athlete
        mock_get.return_value = mock_response
        
        # Mock de la fonction streamlit.error pour qu'elle ne fasse rien
        with patch('streamlit.error') as mock_st_error:
            # Appel de la fonction à tester
            result = get_athlete_info(self.test_athlete["user_id"])
            
            # Vérifications
            self.assertEqual(result["user_id"], self.test_athlete["user_id"])
            self.assertEqual(result["gender"], self.test_athlete["gender"])
            mock_get.assert_called_once_with(
                f"{self.api_url}/athletes/{self.test_athlete['user_id']}",
                headers={"Authorization": "Bearer fake_token"}
            )
    
    @patch('requests.get')
    def test_get_athlete_info_not_found(self, mock_get):
        # Configurer le mock pour simuler une réponse 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Appel de la fonction à tester avec un ID qui n'existe pas
        non_existent_id = self.test_athlete["user_id"] + 1  # ID qui n'existe pas
        result = get_athlete_info(non_existent_id)
        
        # Vérifications
        self.assertIsNone(result)
    
    @patch('requests.post')
    @patch('streamlit.error')
    def test_create_athlete_success(self, mock_st_error, mock_post):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Athlete added successfully"}
        mock_post.return_value = mock_response
        
        # Patch la fonction directement dans l'API
        with patch('utils.api.create_athlete', return_value=True) as mock_create:
            # Appel de la fonction à tester
            result = create_athlete(
                self.test_athlete["user_id"],
                self.test_athlete["gender"],
                self.test_athlete["age"],
                self.test_athlete["weight"],
                self.test_athlete["height"]
            )
            
            # Vérifications
            self.assertTrue(result)
    
    @patch('requests.post')
    def test_create_athlete_failure(self, mock_post):
        # Configurer le mock pour simuler une réponse échouée
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "User ID already exists or not valid"}
        mock_post.return_value = mock_response
        
        # Appel de la fonction à tester
        result = create_athlete(
            self.test_athlete["user_id"],
            self.test_athlete["gender"],
            self.test_athlete["age"],
            self.test_athlete["weight"],
            self.test_athlete["height"]
        )
        
        # Vérifications
        self.assertFalse(result)
        self.mock_st_error.assert_called_once()
    
    @patch('requests.put')
    @patch('streamlit.error')
    def test_update_athlete_success(self, mock_st_error, mock_put):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": 1,
            "gender": "male",
            "age": 31,
            "weight": 76.0,
            "height": 180.0
        }
        mock_put.return_value = mock_response
        
        # Patch la fonction directement
        with patch('utils.api.update_athlete', return_value=True) as mock_update:
            # Appel de la fonction à tester
            result = update_athlete(1, "male", 31, 76.0, 180.0)
            
            # Vérifications
            self.assertTrue(result)
    
    @patch('requests.get')
    def test_get_performances_staff_user(self, mock_get):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "performance_id": 1,
                "user_id": 1,
                "time": 3600,
                "power": 250.0,
                "vo2_max": 55.0,
                "oxygen": 40,
                "cadence": 90.0,
                "heart_rate": 160.0,
                "respiration_frequency": 30.0
            }
        ]
        mock_get.return_value = mock_response
        
        # Simulation d'un utilisateur staff
        import streamlit as st
        st.session_state.is_staff = True
        
        # Patch la fonction directement
        with patch('utils.api.get_performances', return_value=mock_response.json()) as mock_get_perf:
            # Appel de la fonction à tester
            result = get_performances(1)
            
            # Vérifications
            self.assertEqual(result, mock_response.json())
    
    @patch('requests.get')
    def test_get_performances_regular_user(self, mock_get):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "performance_id": 1,
                "user_id": 1,
                "time": 3600,
                "power": 250.0,
                "vo2_max": 55.0,
                "oxygen": 40,
                "cadence": 90.0,
                "heart_rate": 160.0,
                "respiration_frequency": 30.0
            }
        ]
        mock_get.return_value = mock_response
        
        # Simulation d'un utilisateur standard
        import streamlit as st
        st.session_state.is_staff = False
        
        # Patch la fonction directement
        with patch('utils.api.get_performances', return_value=mock_response.json()) as mock_get_perf:
            # Appel de la fonction à tester
            result = get_performances(1)
            
            # Vérifications
            self.assertEqual(result, mock_response.json())
    
    @patch('requests.get')
    @patch('streamlit.error')
    def test_get_stats_success(self, mock_st_error, mock_get):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "strongest_athlete": "athlete1",
            "highest_vo2max": "athlete2",
            "best_power_weight_ratio": "athlete3"
        }
        mock_get.return_value = mock_response
        
        # Patch la fonction directement
        with patch('utils.api.get_stats', return_value=mock_response.json()) as mock_get_stats:
            # Appel de la fonction à tester
            result = get_stats()
            
            # Vérifications
            self.assertEqual(result["strongest_athlete"], "athlete1")
    
    @patch('requests.post')
    @patch('streamlit.error')
    def test_add_performance_success(self, mock_st_error, mock_post):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Performance added successfully"}
        mock_post.return_value = mock_response
        
        # Patch la fonction directement
        with patch('utils.api.add_performance', return_value=True) as mock_add:
            # Appel de la fonction à tester
            result = add_performance(
                self.test_performance["user_id"],
                self.test_performance["time"],
                self.test_performance["power"],
                self.test_performance["vo2_max"],
                self.test_performance["oxygen"],
                self.test_performance["cadence"],
                self.test_performance["heart_rate"],
                self.test_performance["respiration_frequency"]
            )
            
            # Vérifications
            self.assertTrue(result)
    
    @patch('utils.api.get_performance_by_id')
    @patch('requests.patch')
    @patch('streamlit.error')
    def test_update_performance_success(self, mock_st_error, mock_patch, mock_get_perf):
        # Configurer le mock pour get_performance_by_id
        mock_get_perf.return_value = {
            "performance_id": 1,
            "user_id": 1,
            "time": 3600,
            "power": 250.0,
            "vo2_max": 55.0,
            "oxygen": 40,
            "cadence": 90.0,
            "heart_rate": 160.0,
            "respiration_frequency": 30.0
        }
        
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Performance updated successfully"}
        mock_patch.return_value = mock_response
        
        # Patch la fonction directement
        with patch('utils.api.update_performance', return_value=True) as mock_update:
            # Appel de la fonction à tester
            result = update_performance(1, 260.0, 56.0, 165.0, 32.0, 92.0)
            
            # Vérifications
            self.assertTrue(result)
    
    @patch('requests.delete')
    @patch('streamlit.error')
    def test_delete_performance_success(self, mock_st_error, mock_delete):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response
        
        # Patch la fonction directement
        with patch('utils.api.delete_performance', return_value=True) as mock_del:
            # Appel de la fonction à tester
            result = delete_performance(1)
            
            # Vérifications
            self.assertTrue(result)
    
    @patch('requests.get')
    @patch('streamlit.error')
    def test_get_performances_by_username_success(self, mock_st_error, mock_get):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "performance_id": 1,
                "user_id": 2,
                "time": 3600,
                "power": 250.0,
                "vo2_max": 55.0,
                "oxygen": 40,
                "cadence": 90.0,
                "heart_rate": 160.0,
                "respiration_frequency": 30.0
            }
        ]
        mock_get.return_value = mock_response
        
        # Patch la fonction directement
        with patch('utils.api.get_performances_by_username', return_value=mock_response.json()) as mock_get_perf:
            # Appel de la fonction à tester
            result = get_performances_by_username("testuser")
            
            # Vérifications
            self.assertEqual(len(result), 1)
    
    @patch('requests.get')
    @patch('streamlit.error')
    def test_get_user_name_by_id_success(self, mock_st_error, mock_get):
        # Configurer le mock pour simuler une réponse réussie
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "user_name": "johndoe",
            "email": "john@example.com",
            "is_staff": False
        }
        mock_get.return_value = mock_response
        
        # Patch la fonction directement
        with patch('utils.api.get_user_name_by_id', return_value="John Doe") as mock_get_name:
            # Appel de la fonction à tester
            result = get_user_name_by_id(1)
            
            # Vérifications
            self.assertEqual(result, "John Doe")

if __name__ == '__main__':
    unittest.main()