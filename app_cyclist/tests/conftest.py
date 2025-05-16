import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_config_loader import TestConfig
from init_test_db import initialize_test_database

# Classe pour simuler un objet avec accès par attribut pour streamlit.session_state
class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

@pytest.fixture(scope="session")
def config():
    """Fournit la configuration des tests à toutes les fonctions de test"""
    return TestConfig()

@pytest.fixture(scope="session")
def test_db():
    """Initialise la base de données de test une fois par session"""
    db_path = initialize_test_database()
    return db_path

@pytest.fixture
def api_url(config):
    """Fournit l'URL de l'API aux fonctions de test"""
    return config.get_api_url()

@pytest.fixture
def test_user(config):
    """Fournit les informations d'utilisateur de test"""
    return config.get_auth_test_user()

@pytest.fixture
def test_athlete(config):
    """Fournit les données d'un athlète de test"""
    return config.get_test_athlete_data()

@pytest.fixture
def test_performance(config):
    """Fournit les données d'une performance de test"""
    return config.get_test_performance_data()

@pytest.fixture
def auth_token(api_url, test_user):
    """Obtient un token d'authentification pour les tests"""
    import requests
    
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    
    response = requests.post(
        f"{api_url}/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

@pytest.fixture
def auth_headers(auth_token):
    """Fournit les headers d'authentification pour les requêtes API"""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}

@pytest.fixture
def mock_streamlit_session():
    """Crée un mock pour streamlit.session_state avec support d'attributs"""
    session_state = DotDict({
        'token': 'fake_token',
        'user_id': 1,
        'authenticated': True,
        'is_staff': True,
        'user_data': {
            'id': 1,
            'first_name': 'Test',
            'last_name': 'User',
            'user_name': 'testuser',
            'email': 'test@example.com',
            'is_staff': True
        },
        'current_page': 'dashboard'
    })
    
    with patch('streamlit.session_state', session_state) as mock_session:
        yield mock_session

@pytest.fixture
def mock_streamlit():
    """Crée des mocks pour les composants Streamlit"""
    import streamlit as st
    from unittest.mock import MagicMock, patch
    
    # Liste des composants Streamlit à mocker
    components = [
        'streamlit.title', 'streamlit.header', 'streamlit.subheader', 
        'streamlit.text', 'streamlit.markdown', 'streamlit.write',
        'streamlit.button', 'streamlit.checkbox', 'streamlit.radio',
        'streamlit.selectbox', 'streamlit.multiselect', 'streamlit.slider',
        'streamlit.text_input', 'streamlit.number_input', 'streamlit.text_area',
        'streamlit.date_input', 'streamlit.time_input', 'streamlit.file_uploader',
        'streamlit.color_picker', 'streamlit.success', 'streamlit.info',
        'streamlit.warning', 'streamlit.error', 'streamlit.columns',
        'streamlit.tabs', 'streamlit.sidebar', 'streamlit.form',
        'streamlit.metric', 'streamlit.rerun'
    ]
    
   
    patchers = []
    for component in components:
        patcher = patch(component, return_value=MagicMock())
        mock = patcher.start()
        patchers.append((component, patcher, mock))
    
    # Configurer session_state
    session_state = DotDict({
        'token': 'fake_token',
        'user_id': 1,
        'authenticated': True,
        'is_staff': True,
        'user_data': {
            'id': 1,
            'first_name': 'Test',
            'last_name': 'User',
            'user_name': 'testuser',
            'email': 'test@example.com',
            'is_staff': True
        },
        'current_page': 'dashboard'
    })
    session_state_patcher = patch('streamlit.session_state', session_state)
    session_state_mock = session_state_patcher.start()
    patchers.append(('streamlit.session_state', session_state_patcher, session_state_mock))
    
    yield {
        'patchers': patchers,
        'session_state': session_state
    }
    
    # Arrêter tous les patchers
    for _, patcher, _ in patchers:
        patcher.stop()

@pytest.fixture
def mock_api_functions():
    """Mock les fonctions d'API pour qu'elles retournent des résultats attendus"""
    functions_to_mock = [
        ('utils.api.get_athlete_info', lambda *args, **kwargs: {
            "user_id": 1,
            "gender": "male",
            "age": 30,
            "weight": 75.5,
            "height": 180.0
        }),
        ('utils.api.create_athlete', lambda *args, **kwargs: True),
        ('utils.api.update_athlete', lambda *args, **kwargs: True),
        ('utils.api.get_performances', lambda *args, **kwargs: [
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
        ]),
        ('utils.api.get_stats', lambda *args, **kwargs: {
            "strongest_athlete": "athlete1",
            "highest_vo2max": "athlete2",
            "best_power_weight_ratio": "athlete3"
        }),
        ('utils.api.add_performance', lambda *args, **kwargs: True),
        ('utils.api.update_performance', lambda *args, **kwargs: True),
        ('utils.api.delete_performance', lambda *args, **kwargs: True),
        ('utils.api.get_performances_by_username', lambda *args, **kwargs: [
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
        ]),
        ('utils.api.get_user_name_by_id', lambda *args, **kwargs: "John Doe")
    ]
    
    patchers = []
    for func_path, return_value in functions_to_mock:
        patcher = patch(func_path, return_value)
        mock = patcher.start()
        patchers.append((func_path, patcher, mock))
    
    yield {
        'patchers': patchers
    }
    
    # Arrêter tous les patchers
    for _, patcher, _ in patchers:
        patcher.stop()

@pytest.fixture
def mock_auth_functions():
    """Mock les fonctions d'authentification pour qu'elles retournent des résultats attendus"""
    functions_to_mock = [
        ('utils.auth.login', lambda *args, **kwargs: True),
        ('utils.auth.register', lambda *args, **kwargs: True),
        ('utils.auth.get_user_info', lambda *args, **kwargs: {
            "id": 1,
            "first_name": "Test",
            "last_name": "User",
            "user_name": "testuser",
            "email": "test@example.com",
            "is_staff": True
        })
    ]
    
    patchers = []
    for func_path, return_value in functions_to_mock:
        patcher = patch(func_path, return_value)
        mock = patcher.start()
        patchers.append((func_path, patcher, mock))
    
    yield {
        'patchers': patchers
    }
    
    # Arrêter tous les patchers
    for _, patcher, _ in patchers:
        patcher.stop()