import yaml
import os
import sys

class TestConfig:
    """Gestionnaire de configuration pour les tests"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Implémentation du modèle Singleton"""
        if cls._instance is None:
            cls._instance = super(TestConfig, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Charger la configuration depuis le fichier YAML"""
        # Chemin du fichier de configuration
        config_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "test_config.yaml"
        )
        
        try:
            with open(config_file, 'r') as file:
                self._config = yaml.safe_load(file)
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            self._config = {}
    
    def get_api_url(self):
        """Obtenir l'URL de l'API"""
        return self._config.get('app', {}).get('api_url', "http://127.0.0.1:8000")
    
    def get_streamlit_url(self):
        """Obtenir l'URL de l'application Streamlit"""
        return self._config.get('app', {}).get('streamlit_url', "http://localhost:8501")
    
    def get_test_database_url(self):
        """Obtenir l'URL de la base de données de test"""
        # Par défaut, place la base de données dans le dossier tests
        default_db_url = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "test_database.sqlite"
        )
        return self._config.get('unit_tests', {}).get('database_url', default_db_url)
    
    def get_auth_test_user(self):
        """Obtenir les informations de l'utilisateur de test pour l'authentification"""
        return self._config.get('auth_tests', {}).get('test_user', {
            'email': "test@example.com",
            'password': "password123",
            'first_name': "Test",
            'last_name': "User",
            'user_name': "testuser",
            'is_staff': "YES"
        })
    
    def get_test_athlete_data(self):
        """Obtenir les données de test pour un athlète"""
        return self._config.get('api_tests', {}).get('test_athlete', {
            'user_id': 1,
            'gender': "male",
            'age': 30,
            'weight': 75.5,
            'height': 180.0
        })
    
    def get_test_performance_data(self):
        """Obtenir les données de test pour une performance"""
        return self._config.get('api_tests', {}).get('test_performance', {
            'user_id': 1,
            'time': 3600,
            'power': 250.0,
            'vo2_max': 55.0,
            'oxygen': 40,
            'cadence': 90.0,
            'heart_rate': 160.0,
            'respiration_frequency': 30.0
        })
    
    def get_integration_endpoints(self):
        """Obtenir la liste des endpoints à tester pour les tests d'intégration"""
        return self._config.get('integration_tests', {}).get('endpoints', [])
    
    def get_integration_timeout(self):
        """Obtenir le timeout pour les tests d'intégration"""
        return self._config.get('integration_tests', {}).get('timeout', 5)
    
    def get_load_test_config(self):
        """Obtenir la configuration pour les tests de charge"""
        return self._config.get('load_tests', {})
    
    def get_load_tests(self):
        """Obtenir la liste des tests de charge à exécuter"""
        return self._config.get('load_tests', {}).get('tests', [])

# Exemple d'utilisation
if __name__ == "__main__":
    config = TestConfig()
    print(f"API URL: {config.get_api_url()}")
    print(f"Test user: {config.get_auth_test_user()}")
    print(f"Test endpoints: {config.get_integration_endpoints()}")