import sqlite3
import pandas as pd
import json
import os

DB_PATH = "telemetria.db"

def inicializar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de Partidas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidas (
            id_partida TEXT PRIMARY KEY,
            agente_0 TEXT,
            agente_1 TEXT,
            ganador TEXT,
            turnos INTEGER,
            motivo_fin TEXT
        )
    """)
    
    # Tabla de Decisiones (Features para ML)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_partida TEXT,
            turno INTEGER,
            agente_id INTEGER,
            agente_nombre TEXT,
            estado_json TEXT,
            nodos_expandidos INTEGER,
            tiempo_ms REAL,
            accion_elegida TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def guardar_partida(id_partida, agente_0, agente_1, ganador, turnos, motivo_fin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO partidas (id_partida, agente_0, agente_1, ganador, turnos, motivo_fin)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id_partida, agente_0, agente_1, ganador, turnos, motivo_fin))
    conn.commit()
    conn.close()

def guardar_decision(id_partida, turno, agente_id, agente_nombre, estado, nodos, tiempo_ms, accion):
    # Guardamos el estado mínimo necesario para luego extraer features (ML)
    estado_serializado = json.dumps({
        "pos": estado["mi_pos"],
        "bombas": [b["pos"] for b in estado["bombas"]],
        "rivales": [r["pos"] for r in estado["rivales"]]
    })
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO decisiones (id_partida, turno, agente_id, agente_nombre, estado_json, nodos_expandidos, tiempo_ms, accion_elegida)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_partida, turno, agente_id, agente_nombre, estado_serializado, nodos, tiempo_ms, accion))
    conn.commit()
    conn.close()

def obtener_dataframe_decisiones():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM decisiones", conn)
    conn.close()
    return df

def obtener_dataframe_partidas():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM partidas", conn)
    conn.close()
    return df
