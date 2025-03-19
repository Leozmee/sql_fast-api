import streamlit as st
import pandas as pd
import sqlite3

st.write("Cyclist Data Analysis")

def get_data():
    conn = sqlite3.connect("cyclist_database.db")
    cursor = conn.cursor()

    df = pd.read_sql_query("SELECT User.id, User.first_name, User.last_name, User.email, User.password, User.is_staff,"
                               "CyclistInfo.gender, CyclistInfo.age, CyclistInfo.weight, CyclistInfo.height,"
                                "Performance.time, Performance.power, Performance.oxygen, Performance.cadence, Performance.heart_rate, Performance.respiration_frequency,"
                                "Test.test_type "
                        "FROM USER "
                        "LEFT JOIN CyclistInfo ON User.id = CyclistInfo.user_id "
                        "LEFT JOIN PERFORMANCE ON CyclistInfo.user_id = performance.user_id "
                        "LEFT JOIN TEST ON performance.test_id = test.test_id", conn)

    return df.head(1000)


st.dataframe(get_data())