import sys
import os
import sqlite3
import argparse
from pathlib import Path

# Ajouter le répertoire parent au chemin pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_config_loader import TestConfig

def initialize_test_database():
    """Initialisation de la base de données de test"""
    config = TestConfig()
    db_path = config.get_test_database_url()
    
    # Créer le répertoire si nécessaire
    Path(os.path.dirname(db_path)).mkdir(parents=True, exist_ok=True)
    
    # Supprimer l'ancienne base de données si elle existe
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Créer la nouvelle base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer les tables
    cursor.executescript("""
        CREATE TABLE User(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            is_staff BOOLEAN NOT NULL DEFAULT 0
        );
        
        CREATE TABLE Athlete(
            user_id INTEGER PRIMARY KEY,
            gender TEXT CHECK(gender IN ('male', 'female')) NOT NULL,
            age INTEGER CHECK(age > 0) NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
        
        CREATE TABLE Performance(
            performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL, 
            time INTEGER NOT NULL,
            power REAL NOT NULL,
            vo2_max REAL NOT NULL,
            oxygen INTEGER NOT NULL,
            cadence REAL NOT NULL,
            heart_rate REAL NOT NULL,
            respiration_frequency REAL NOT NULL,
            FOREIGN KEY(user_id) REFERENCES User(id)
        );
    """)
    
    # Ajouter des données de test
    test_user = config.get_auth_test_user()
    test_athlete = config.get_test_athlete_data()
    test_performance = config.get_test_performance_data()
    
    # Insérer un utilisateur de test
    cursor.execute(
        "INSERT INTO User (user_name, first_name, last_name, email, password, is_staff) VALUES (?, ?, ?, ?, ?, ?)",
        (
            test_user['user_name'],
            test_user['first_name'],
            test_user['last_name'],
            test_user['email'],
            # Mot de passe haché (bcrypt) pour 'password123'
            "$2b$12$tQGxq0T8vxzrDDEJVJIlRO0J4Yfbkq9s8/zRgUV3bECUi7RXW1oPS",
            1 if test_user['is_staff'].upper() == "YES" else 0
        )
    )
    
    # Insérer un athlète de test
    cursor.execute(
        "INSERT INTO Athlete (user_id, gender, age, weight, height) VALUES (?, ?, ?, ?, ?)",
        (
            test_athlete['user_id'],
            test_athlete['gender'],
            test_athlete['age'],
            test_athlete['weight'],
            test_athlete['height']
        )
    )
    
    # Insérer quelques performances de test
    cursor.execute(
        """
        INSERT INTO Performance (
            user_id, time, power, vo2_max, oxygen, cadence, heart_rate, respiration_frequency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            test_performance['user_id'],
            test_performance['time'],
            test_performance['power'],
            test_performance['vo2_max'],
            test_performance['oxygen'],
            test_performance['cadence'],
            test_performance['heart_rate'],
            test_performance['respiration_frequency']
        )
    )
    
    # Insérer une deuxième performance avec des valeurs différentes
    cursor.execute(
        """
        INSERT INTO Performance (
            user_id, time, power, vo2_max, oxygen, cadence, heart_rate, respiration_frequency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            test_performance['user_id'],
            test_performance['time'] + 3600,  # 1 heure plus tard
            test_performance['power'] * 1.1,  # 10% plus puissant
            test_performance['vo2_max'] * 1.05,  # 5% meilleur VO2max
            test_performance['oxygen'] + 2,
            test_performance['cadence'] + 5,
            test_performance['heart_rate'] + 10,
            test_performance['respiration_frequency'] + 2
        )
    )
    
    # Valider les modifications et fermer la connexion
    conn.commit()
    conn.close()
    
    print(f"Base de données de test initialisée avec succès : {db_path}")
    return db_path

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Initialisation de la base de données de test")
    parser.add_argument("--reset", action="store_true", help="Réinitialiser la base de données de test")
    
    args = parser.parse_args()
    
    if args.reset:
        db_path = initialize_test_database()
        print(f"Base de données réinitialisée : {db_path}")
    else:
        config = TestConfig()
        db_path = config.get_test_database_url()
        
        if not os.path.exists(db_path):
            db_path = initialize_test_database()
            print(f"Base de données créée : {db_path}")
        else:
            print(f"La base de données existe déjà : {db_path}")
            print("Utilisez l'option --reset pour la réinitialiser.")

if __name__ == "__main__":
    main()