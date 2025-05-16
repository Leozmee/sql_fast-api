
import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from io import StringIO


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.auth import login, register, get_user_info, logout
from test_config_loader import TestConfig

class DotDict(dict):
    """Classe pour simuler un objet avec accès par attribut pour streamlit.session_state"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class TestAuth(unittest.TestCase):
    
    def setUp(self):
        
        self.config = TestConfig()
        self.test_user = self.config.get_auth_test_user()
        self.api_url = self.config.get_api_url()
        
        self.patcher = patch('streamlit.error')
        self.mock_st_error = self.patcher.start()
    
        self.session_state = DotDict({})
        self.session_state_patcher = patch('streamlit.session_state', self.session_state)
        self.mock_session_state = self.session_state_patcher.start()
    
    def tearDown(self):
        self.patcher.stop()
        self.session_state_patcher.stop()
    
    @patch('requests.post')
    def test_login_success(self, mock_post):
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "fake_token",
            "token_type": "bearer"
        }
        mock_post.return_value = mock_response
        
        with patch('utils.auth.get_user_info') as mock_get_user_info:
            mock_get_user_info.return_value = {
                "id": 1,
                "first_name": self.test_user["first_name"],
                "last_name": self.test_user["last_name"],
                "user_name": self.test_user["user_name"],
                "email": self.test_user["email"],
                "is_staff": True
            }
            
            result = login(self.test_user["email"], self.test_user["password"])
            
            self.assertTrue(result)
            mock_post.assert_called_once_with(
                f"{self.api_url}/token",
                data={"username": self.test_user["email"], "password": self.test_user["password"]},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
    
    @patch('requests.post')
    def test_login_failure(self, mock_post):
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid credentials"}
        mock_post.return_value = mock_response
        
        result = login(self.test_user["email"], "wrong_password")
        
        self.assertFalse(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_login_exception(self, mock_post):
        
        mock_post.side_effect = Exception("Connection error")
        
        result = login(self.test_user["email"], self.test_user["password"])
        
        self.assertFalse(result)
        self.mock_st_error.assert_called_once()
    
    @patch('requests.post')
    def test_register_success(self, mock_post):
        
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "User registered successfully"}
        mock_post.return_value = mock_response
        
        result = register(
            self.test_user["first_name"],
            self.test_user["last_name"],
            self.test_user["user_name"],
            self.test_user["email"],
            self.test_user["password"],
            self.test_user["is_staff"]
        )
        
        self.assertTrue(result)
        mock_post.assert_called_once_with(
            f"{self.api_url}/users/register",
            json={
                "first_name": self.test_user["first_name"],
                "last_name": self.test_user["last_name"],
                "user_name": self.test_user["user_name"],
                "email": self.test_user["email"],
                "password": self.test_user["password"],
                "is_staff": self.test_user["is_staff"]
            }
        )
    
    @patch('requests.post')
    def test_register_failure(self, mock_post):
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Email already exists"}
        mock_post.return_value = mock_response
        
        result = register(
            self.test_user["first_name"],
            self.test_user["last_name"],
            self.test_user["user_name"],
            self.test_user["email"],
            self.test_user["password"],
            self.test_user["is_staff"]
        )
        
        self.assertFalse(result)
        self.mock_st_error.assert_called_once()
    
    @patch('requests.get')
    def test_get_user_info_success(self, mock_get):
        
        import streamlit as st
        st.session_state.token = "fake_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "first_name": self.test_user["first_name"],
            "last_name": self.test_user["last_name"],
            "user_name": self.test_user["user_name"],
            "email": self.test_user["email"],
            "is_staff": True
        }
        mock_get.return_value = mock_response
        
        result = get_user_info()
        
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["email"], self.test_user["email"])
        mock_get.assert_called_once_with(
            f"{self.api_url}/users/me",
            headers={"Authorization": "Bearer fake_token"}
        )
    
    @patch('requests.get')
    def test_get_user_info_failure(self, mock_get):
        
        import streamlit as st
        st.session_state.token = "fake_token"
        
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = get_user_info()
        
        self.assertIsNone(result)
        self.mock_st_error.assert_called_once()
    
    def test_logout(self):
        
        import streamlit as st
        st.session_state.authenticated = True
        st.session_state.token = "fake_token"
        st.session_state.user_id = 1
        st.session_state.user_data = {"name": "Test"}
        st.session_state.is_staff = True
        st.session_state.current_page = "dashboard"
        
        logout()
        
        self.assertFalse(st.session_state.authenticated)
        self.assertIsNone(st.session_state.token)
        self.assertIsNone(st.session_state.user_id)
        self.assertIsNone(st.session_state.user_data)
        self.assertFalse(st.session_state.is_staff)
        self.assertEqual(st.session_state.current_page, "login")

if __name__ == '__main__':
    unittest.main()