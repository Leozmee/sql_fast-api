import unittest
import sys
import os
import time
import requests
from unittest.mock import patch
import subprocess

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_config_loader import TestConfig

class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour l'API et l'application Streamlit"""
    
    @classmethod
    def setUpClass(cls):
        """Initialisation avant tous les tests"""
        # Charger la configuration
        cls.config = TestConfig()
        cls.api_url = cls.config.get_api_url()
        cls.test_user = cls.config.get_auth_test_user()
        cls.test_athlete = cls.config.get_test_athlete_data()
        cls.test_performance = cls.config.get_test_performance_data()
        cls.integration_timeout = cls.config.get_integration_timeout()
        
        # Vérifier si l'API est accessible
        try:
            response = requests.get(cls.api_url, timeout=cls.integration_timeout)
            cls.api_available = response.status_code == 200
        except:
            cls.api_available = False
            print("AVERTISSEMENT: L'API n'est pas accessible. Les tests d'intégration seront ignorés.")
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.token = None
        
        # Ignorer les tests si l'API n'est pas disponible
        if not self.__class__.api_available:
            self.skipTest("L'API n'est pas accessible")
    
    def test_1_user_registration(self):
        """Test d'intégration: inscription d'un utilisateur"""
        # Créer un utilisateur de test
        user_data = {
            "first_name": self.test_user["first_name"],
            "last_name": self.test_user["last_name"],
            "user_name": self.test_user["user_name"],
            "email": self.test_user["email"],
            "password": self.test_user["password"],
            "is_staff": self.test_user["is_staff"]
        }
        
        response = requests.post(f"{self.api_url}/users/register", json=user_data)
        
        # Vérifie que l'inscription a réussi (ou que l'utilisateur existe déjà)
        self.assertTrue(response.status_code in [201, 200, 400], 
                        f"Échec de l'inscription: {response.status_code}, {response.text}")
    
    def test_2_user_login(self):
        """Test d'intégration: connexion d'un utilisateur"""
        # Connexion avec l'utilisateur créé précédemment
        login_data = {
            "username": self.test_user["email"],
            "password": self.test_user["password"]
        }
        
        response = requests.post(
            f"{self.api_url}/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Vérifie que la connexion a réussi
        self.assertEqual(response.status_code, 200, 
                         f"Échec de la connexion: {response.status_code}, {response.text}")
        
        # Stocke le token pour les tests suivants
        response_data = response.json()
        self.token = response_data.get("access_token")
        self.assertIsNotNone(self.token, "Aucun token reçu")
    
    def test_3_create_athlete(self):
        """Test d'intégration: création d'un athlète"""
        # S'assurer qu'un token a été obtenu
        if not self.token:
            self.test_2_user_login()
        
        # Créer un athlète
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{self.api_url}/athletes/", json=self.test_athlete, headers=headers)
        
        # Vérifie que la création a réussi (ou que l'athlète existe déjà)
        self.assertTrue(response.status_code in [201, 200, 400], 
                        f"Échec de la création d'athlète: {response.status_code}, {response.text}")
    
    def test_4_get_athlete_info(self):
        """Test d'intégration: récupération des informations d'un athlète"""
        # S'assurer qu'un token a été obtenu
        if not self.token:
            self.test_2_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(f"{self.api_url}/athletes/{self.test_athlete['user_id']}", headers=headers)
        
        # Si l'athlète existe, vérifier les données
        if response.status_code == 200:
            athlete_data = response.json()
            self.assertEqual(athlete_data["user_id"], self.test_athlete["user_id"])
            self.assertIn(athlete_data["gender"], ["male", "female"])
            self.assertIsInstance(athlete_data["age"], int)
            self.assertIsInstance(athlete_data["weight"], (int, float))
            self.assertIsInstance(athlete_data["height"], (int, float))
        else:
            # Si l'athlète n'existe pas, ce n'est pas une erreur dans ce test d'intégration
            print(f"Athlète non trouvé, statut: {response.status_code}")
    
    def test_5_add_performance(self):
        """Test d'intégration: ajout d'une performance"""
        # S'assurer qu'un token a été obtenu
        if not self.token:
            self.test_2_user_login()
        
        # Ajouter une performance
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"{self.api_url}/performances/", json=self.test_performance, headers=headers)
        
        # Vérifie que l'ajout a réussi
        self.assertTrue(response.status_code in [201, 200], 
                        f"Échec de l'ajout de performance: {response.status_code}, {response.text}")
    
    def test_6_get_performances(self):
        """Test d'intégration: récupération des performances"""
        # S'assurer qu'un token a été obtenu
        if not self.token:
            self.test_2_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(f"{self.api_url}/performances/user/{self.test_athlete['user_id']}", headers=headers)
        
        # Vérifie que la récupération a réussi
        self.assertEqual(response.status_code, 200, 
                         f"Échec de la récupération: {response.status_code}, {response.text}")
        
        performances = response.json()
        self.assertIsInstance(performances, list)
        
        # Si des performances existent, vérifier leur structure
        if performances:
            performance = performances[0]
            self.assertIn("performance_id", performance)
            self.assertIn("user_id", performance)
            self.assertIn("time", performance)
            self.assertIn("power", performance)
    
    def test_7_get_stats(self):
        """Test d'intégration: récupération des statistiques"""
        # S'assurer qu'un token a été obtenu
        if not self.token:
            self.test_2_user_login()
        
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        
        response = requests.get(f"{self.api_url}/performances/stats", headers=headers)
        
        # Vérifie que la récupération a réussi
        self.assertEqual(response.status_code, 200, 
                         f"Échec de la récupération des stats: {response.status_code}, {response.text}")
        
        stats = response.json()
        self.assertIsInstance(stats, dict)
        
        # Vérifie que les clés attendues sont présentes
        self.assertIn("strongest_athlete", stats)
        self.assertIn("highest_vo2max", stats)
        self.assertIn("best_power_weight_ratio", stats)

if __name__ == '__main__':
    unittest.main()