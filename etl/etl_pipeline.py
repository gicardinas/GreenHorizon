import pandas as pd
import sqlite3
import requests
from datetime import datetime, timedelta
from pathlib import Path

# --- CAMINHOS ---
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / 'green_horizon.db'

LATITUDE = -22.9519
LONGITUDE = -43.2105


# --- API CLIMÁTICA ---
def consultar_clima():
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": [
            "temperature_2m",
            "precipitation",
            "wind_speed_10m"
        ],
        "timezone": "America/Sao_Paulo"
    }

    r = requests.get(url, params=params)
    dados = r.json()["current"]

    return {
        "temp_ambiente": dados["temperature_2m"],
        "chuva_mm": dados["precipitation"],
        "vento_kmh": dados["wind_speed_10m"],
        "radiacao_solar": 0.0,  # Placeholder
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# --- SALVAR HISTÓRICO CLIMÁTICO ---
def atualizar_historico_clima(umidade_solo, id_sensor=1, id_cultura=1):
    clima = consultar_clima()

    registro = {
        "timestamp": clima["timestamp"],
        "id_sensor": id_sensor,
        "id_cultura": id_cultura,
        "umidade_solo": umidade_solo,
        "temp_ambiente": clima["temp_ambiente"],
        "vento_kmh": clima["vento_kmh"],
        "radiacao_solar": clima["radiacao_solar"],
        "chuva_mm": clima["chuva_mm"]
    }

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criar tabela se não existir
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_clima (
            id_leitura INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            id_sensor INTEGER,
            id_cultura INTEGER,
            umidade_solo REAL,
            temp_ambiente REAL,
            vento_kmh REAL,
            radiacao_solar REAL,
            chuva_mm REAL
        )
    """)

    # Inserir novo registro
    cursor.execute("""
        INSERT INTO historico_clima (
            timestamp, id_sensor, id_cultura, umidade_solo,
            temp_ambiente, vento_kmh, radiacao_solar, chuva_mm
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        registro["timestamp"],
        registro["id_sensor"],
        registro["id_cultura"],
        registro["umidade_solo"],
        registro["temp_ambiente"],
        registro["vento_kmh"],
        registro["radiacao_solar"],
        registro["chuva_mm"]
    ))

    # Limpar registros antigos (mais de 3h)
    limite = (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        DELETE FROM historico_clima
        WHERE timestamp < ?
    """, (limite,))

    conn.commit()
    conn.close()

    print("🌱 Histórico climático atualizado (últimas 3h mantidas).")
