import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path
from clima_API import consultar_clima

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_TARIFAS = BASE_DIR / 'data' / 'tarifas_energia.csv'
PATH_DB = BASE_DIR / 'database' / 'agro.db'

def verificar_tarifa_atual():
    try:
        df_tarifas = pd.read_csv(PATH_TARIFAS, sep=None, engine='python')
        hora_atual = datetime.now().hour
        tarifa_info = df_tarifas[df_tarifas['hora'] == hora_atual].iloc[0]
        return tarifa_info['tipo'] 
    except Exception as e:
        return "Normal"

def salvar_log_decisao(decisao):
    try:
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs_decisao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                umidade_solo REAL,
                temp_media REAL,
                volume_chuva REAL,
                tarifa TEXT,
                acao TEXT,
                motivo TEXT
            )
        ''')
        cursor.execute('''
            INSERT INTO logs_decisao (timestamp, umidade_solo, temp_media, volume_chuva, tarifa, acao, motivo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            decisao['timestamp'], decisao['umidade_solo'], 
            decisao['temp_media'], decisao['volume_chuva'],
            decisao['tarifa'], decisao['acao'], decisao['motivo']
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao salvar banco: {e}")

def processar_decisao(umidade_solo_atual):
    clima_preditivo = consultar_clima()
    tarifa = verificar_tarifa_atual()
    
    
    LIMITE_UMIDADE = 30
    
    decisao = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "umidade_solo": umidade_solo_atual,
        "temp_media": clima_preditivo['temperatura_media'],
        "volume_chuva": clima_preditivo['volume_chuva_total'],
        "tarifa": tarifa,
        "acao": "DESLIGADO",
        "motivo": ""
    }

    # Lógica PARA PREVISÃO
    if umidade_solo_atual < LIMITE_UMIDADE:
        if clima_preditivo['vai_chover']:
            decisao["acao"] = "AGUARDAR"
            decisao["motivo"] = f"Previsão de {decisao['volume_chuva']}mm de chuva. Economizando água."
        elif tarifa == "Pico":
            decisao["acao"] = "AGUARDAR"
            decisao["motivo"] = "Horário de tarifa cara. Postergando irrigação."
        else:
            decisao["acao"] = "LIGAR"
            decisao["motivo"] = "Solo seco e condições climáticas favoráveis."
    else:
        decisao["motivo"] = "Umidade do solo dentro dos parâmetros ideais."

    # --- TERMINAL LOG
    print("\n" + "═"*50)
    print("🟢 GREEN HORIZON - RELATÓRIO PREDITIVO")
    print("═"*50)
    print(f"📅 Data/Hora:       {decisao['timestamp']}")
    print(f"🌱 Umidade Solo:    {decisao['umidade_solo']}%")
    print(f"🌡️ Temp. Média (3h): {decisao['temp_media']}°C")
    print(f"🌧️ Chuva Prevista:  {decisao['volume_chuva']} mm")
    print(f"⚡ Tarifa Atual:    {decisao['tarifa']}")
    print("─"*50)
    print(f"🤖 DECISÃO:        >>> {decisao['acao']} <<<")
    print(f"💡 MOTIVO:         {decisao['motivo']}")
    print("═"*50 + "\n")

    salvar_log_decisao(decisao)

if __name__ == "__main__":
 
    processar_decisao(20)