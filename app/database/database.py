# src/database/database.py

import sqlite3
import os

def conectar_db():
    """Conecta a la base de datos SQLite."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'trafico_aereo.db')
    conn = sqlite3.connect(db_path)
    return conn
