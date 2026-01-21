import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
# Pega o caminho de onde este script está
BASE_DIR = Path(__file__).resolve().parent 

# Define o caminho da pasta 'data' que está UM NÍVEL ACIMA
# .parent (sai de etl) / 'data' (entra em data)
DATA_DIR = BASE_DIR.parent / 'data'

DB_NAME = BASE_DIR / 'green_horizon.db'

def run_etl():
    print(f"[{datetime.now()}] Iniciando processo de ETL...")
    print(f"🔎 Buscando dados em: {DATA_DIR}")

    # --- 2. EXTRACT ---
    try:
        # PEGANDO CSVS
        df_culturas = pd.read_csv(DATA_DIR / 'config_culturas.csv')
        df_tarifas = pd.read_csv(DATA_DIR / 'tarifas_energia.csv')
        df_historico = pd.read_csv(DATA_DIR / 'historico_leituras_sujo.csv')

        print("✅ Arquivos CSV carregados com sucesso.")
        
        # --- 3. TRANSFORM (Limpeza) ---
        # Removendo Nulos
        df_historico = df_historico.dropna()
        
        # Removendo Temperaturas > 60°C (Ruído)
        df_historico = df_historico[df_historico['temp_ambiente'] <= 60]
        
        print(f"🧹 Dados limpos. Total de registros válidos: {len(df_historico)}")

        # --- 4. LOAD (Salvando no SQLite) ---
        conn = sqlite3.connect(DB_NAME)
        df_historico.to_sql('historico_clima', conn, if_exists='replace', index=False)
        print(f"Banco de dados criado/atualizado em: {DB_NAME}")
        conn.close()

    except Exception as e:
        print(f"❌ Erro durante o processo: {e}")

if __name__ == "__main__":
    run_etl()
        



