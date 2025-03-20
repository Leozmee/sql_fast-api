from decimal import ROUND_HALF_EVEN
import streamlit as st
import pandas as pd
import sqlite3
import json 
from datetime import datetime
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Cyclist Performance", layout="wide")



# Initialize session state
if "role" not in st.session_state:
    st.session_state.role = None


def hash_password(password):
    password = password.encode("utf-8")
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    return password

def check_credentials():
    conn = sqlite3.connect("cyclist_database.db")
    cursor = conn.cursor()
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign up") or st.button("Log in"):
        cursor.execute(f"SELECT * FROM User WHERE email = '{email}' AND password = '{password}'")
        selected = cursor.fetchone()

        if selected[-1] == 1:
            st.session_state.role = "Admin"
            st.rerun()
        elif selected[-1] == 0:
            st.session_state.role = "User"
            st.rerun()
        else:
            st.error("Invalid credentials")

# Define sign up function
def signup():
    st.header("Sign up")
    conn = sqlite3.connect("cyclist_database.db")
    cursor = conn.cursor()
    first_name = st.text_input("First name")
    last_name = st.text_input("Last name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    # password = hash_password(password)

    if st.button("Sign up"):

        cursor.execute(f"INSERT INTO User (first_name, last_name, email, password) VALUES ('{first_name}', '{last_name}', '{email}', '{password}')")
        conn.commit()
        st.session_state.role = "User"
        st.rerun()

# Define login function
def login():
    st.header("Log in")
    st.text_input("Email")
    st.text_input("Password", type="password")
    st.button
    if st.button("Log in"):
        st.session_state.role = ROUND_HALF_EVEN
        st.rerun()


# Define pages
login_page = st.Page(login, title="Log in", icon=":material/login:")
signup_page = st.Page(check_credentials, title="Sign up", icon=":material/person:")
dashboard = st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
profile = st.Page("pages/profile.py", title="Your profile", icon=":material/person:")

# Set up navigation based on authentication
if st.session_state.role:
    pg = st.navigation({
        "Account": [st.Page(lambda: st.button("Log out", on_click=lambda: setattr(st.session_state, "role", None) or st.rerun()), title="Log out")],
        "App": [dashboard, profile]
    })
else:
    pg = st.navigation([login_page])

pg.run()