import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path
from clima_API import consultar_clima

# --- 1. CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_TARIFAS = BASE_DIR / 'data' / 'tarifas_energia.csv'
PATH_CSV = BASE_DIR / 'data' / 'historico_leituras_sujo.csv'

PATH_DB = BASE_DIR / 'etl' / 'green_horizon.db'

def buscar_ultima_leitura_real():
    """Conecta no banco e recupera o registro mais recente para evitar dados fake."""
    try:
        conn = sqlite3.connect(PATH_DB)
       
        query = "SELECT * FROM historico_clima ORDER BY timestamp DESC LIMIT 1"
        df_ultima = pd.read_sql(query, conn)
        conn.close()
        
        if not df_ultima.empty:
            return df_ultima.iloc[0].to_dict()
        return None
    except Exception as e:
        print(f"⚠️ Erro ao buscar leitura no banco: {e}")
        return None

def verificar_tarifa_atual():
    """Identifica se o custo da energia está em horário de 'Pico' ou 'Fora Ponta'."""
    try:
        df_tarifas = pd.read_csv(PATH_TARIFAS, sep=None, engine='python')
        hora_atual = datetime.now().hour
        tarifa_info = df_tarifas[df_tarifas['hora'] == hora_atual].iloc[0]
        return tarifa_info['tipo'] 
    except:
        return "Normal"

def salvar_tudo_sincronizado(decisao, dados_reais):
    """Realiza a persistência dos dados: Logs, Histórico e CSV com ID incremental."""
    try:
        conn = sqlite3.connect(PATH_DB)
        cursor = conn.cursor()

        # 1. Lógica de ID Incremental
        cursor.execute("SELECT MAX(id_leitura) FROM historico_clima")
        resultado = cursor.fetchone()[0]
        proximo_id = (int(resultado) + 1) if resultado is not None else 1

        # 2. Criar tabela de logs se não existir
        cursor.execute('''CREATE TABLE IF NOT EXISTS logs_decisao (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            timestamp TEXT, 
            umidade_solo REAL, 
            previsao_chuva REAL, 
            tarifa TEXT, 
            acao TEXT, 
            motivo TEXT)''')

        # 3. INSERE NA TABELA DE LOGS
        cursor.execute('''INSERT INTO logs_decisao (timestamp, umidade_solo, previsao_chuva, tarifa, acao, motivo)
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (decisao['timestamp'], decisao['umidade_solo'], decisao['volume_chuva'], 
                        decisao['tarifa'], decisao['acao'], decisao['motivo']))

        # 4. Inserir na tabela de HISTÓRICO
        cursor.execute('''INSERT INTO historico_clima (id_leitura, timestamp, id_sensor, id_cultura, umidade_solo, 
                                                      temp_ambiente, vento_kmh, radiacao_solar, chuva_mm)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                       (proximo_id, decisao['timestamp'], dados_reais['id_sensor'], dados_reais['id_cultura'],
                        decisao['umidade_solo'], dados_reais['temp_ambiente'], 
                        dados_reais['vento_kmh'], dados_reais['radiacao_solar'], decisao['volume_chuva']))

        conn.commit()
        conn.close()

      
        nova_linha_csv = [
            proximo_id, decisao['timestamp'], dados_reais['id_sensor'], 
            dados_reais['id_cultura'], decisao['umidade_solo'], 
            dados_reais['temp_ambiente'], dados_reais['vento_kmh'], 
            dados_reais['radiacao_solar'], decisao['volume_chuva']
        ]
        
        df_nova = pd.DataFrame([nova_linha_csv])
        df_nova.to_csv(PATH_CSV, mode='a', header=False, index=False)
        
        print(f"✅ Sincronização concluída! ID Gerado: {proximo_id}")

    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")

def processar_decisao():
    """Cérebro do Green Horizon: une dados reais, clima e economia."""
    
    dados_reais = buscar_ultima_leitura_real()
    
    if not dados_reais:
        print("❌ Banco vazio! Rode o ETL primeiro para carregar o histórico.")
        return


    clima = consultar_clima()
    tarifa = verificar_tarifa_atual()
    umidade_atual = dados_reais['umidade_solo']

 
    decisao = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "umidade_solo": umidade_atual,
        "volume_chuva": clima['volume_chuva_total'],
        "tarifa": tarifa,
        "acao": "AGUARDAR",
        "motivo": ""
    }

    
    if umidade_atual < 30:
        if clima['vai_chover']:
            decisao["motivo"] = f"PREDITIVO: Chuva de {decisao['volume_chuva']}mm em breve."
        elif tarifa == "Pico":
            decisao["motivo"] = "ECONOMIA: Horário de energia cara. Postergando."
        else:
            decisao["acao"] = "LIGAR"
            decisao["motivo"] = "EXECUÇÃO: Solo seco e custo de energia favorável."
    else:
        decisao["motivo"] = "MANUTENÇÃO: Umidade dentro do padrão ideal."

    print(f"\n🤖 DECISÃO GREEN HORIZON: {decisao['acao']}")
    print(f"💡 MOTIVO: {decisao['motivo']}")



    salvar_tudo_sincronizado(decisao, dados_reais)

if __name__ == "__main__":
    processar_decisao()