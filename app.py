import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Configuração da interface do dashboard
st.set_page_config(page_title="Green Horizon - Dashboard Real", layout="wide", page_icon="🚜")

# --- FUNÇÃO DE ACESSO AOS DADOS REAIS ---
def carregar_dados_reais():
    # Conecta ao banco de dados SQL gerado na Fase 1 [cite: 30]
    conn = sqlite3.connect('etl/green_horizon.db')
    
    # Tabela com dados climáticos processados e limpos
    df_clima_limpo = pd.read_sql_query("SELECT * FROM historico_clima", conn)
    
    # Tabela com o histórico de decisões do sistema (Fase 2) [cite: 33, 34]
    df_logs = pd.read_sql_query("SELECT * FROM logs_decisao", conn)
    
    conn.close()
    return df_clima_limpo, df_logs

# --- CARREGAMENTO E TRATAMENTO DE ERROS ---
try:
    df_limpo, df_logs = carregar_dados_reais()
    # Carrega o CSV sujo (legado) para fins de auditoria [cite: 19, 20]
    df_sujo = pd.read_csv('data/historico_leituras_sujo.csv') 
    
    # TRATAMENTO DE ERRO DE DATA (NameError/ValueError):
    # Usamos errors='coerce' para ignorar textos inválidos como 'S-01' e format='mixed' para flexibilidade
    df_limpo['timestamp'] = pd.to_datetime(df_limpo['timestamp'], errors='coerce', format='mixed')
    df_sujo['timestamp'] = pd.to_datetime(df_sujo['timestamp'], errors='coerce', format='mixed')
    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'], errors='coerce', format='mixed')
    
    # Limpeza de registros inválidos que poderiam quebrar os gráficos
    df_limpo = df_limpo.dropna(subset=['timestamp'])
    df_sujo = df_sujo.dropna(subset=['timestamp'])
    df_logs = df_logs.dropna(subset=['timestamp'])
    
except Exception as e:
    st.error(f"Erro ao carregar arquivos: {e}. Verifique se as pastas 'data' e 'etl' estão no mesmo diretório que este script.")
    st.stop()

# --- INTERFACE VISUAL ---
st.title("🚜 Projeto Green Horizon - AgroTech 2.0")
st.markdown("**Unidade Experimental:** Rio de Janeiro (Cristo Redentor) [cite: 5, 25]")

# 1. MONITORAMENTO (Requisito 4.1) [cite: 48]
st.header("1. Monitoramento em Tempo Real")
ultima_leitura = df_logs.iloc[-1] # Captura o estado mais recente do sistema
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Umidade do Solo", f"{ultima_leitura['umidade_solo']}%")
with col2:
    st.metric("Previsão de Chuva", f"{ultima_leitura['previsao_chuva']}mm")
with col3:
    st.metric("Tarifa de Energia", ultima_leitura['tarifa'])

st.info(f"**Status do Sistema:** {ultima_leitura['acao']} | **Motivo:** {ultima_leitura['motivo']}")

st.divider()

# 2. AUDITORIA DE DADOS (Requisito 4.2) [cite: 49]
st.header("2. Auditoria de Qualidade (ETL)")
st.write("Comprovação da limpeza de dados: Remoção de picos de 500°C dos sensores legados[cite: 10, 32].")

fig_auditoria = px.line(title="Comparativo de Temperatura: Dados Sujos vs. Dados Sanitizados")
fig_auditoria.add_scatter(x=df_sujo['timestamp'], y=df_sujo['temp_ambiente'], name="Sensor Sujo (Erro)", line=dict(color='red'))
fig_auditoria.add_scatter(x=df_limpo['timestamp'], y=df_limpo['temp_ambiente'], name="Sensor Limpo (Corrigido)", line=dict(color='green'))
st.plotly_chart(fig_auditoria, use_container_width=True)

st.divider()

# 3. KPI DE ECONOMIA (Requisito 4.3) [cite: 50]
st.header("3. Inteligência de Negócio e Economia")
c1, c2 = st.columns([1, 2])

# Cálculo de irrigações evitadas (Chuvas futuras) ou adiadas (Horário de Ponta) [cite: 36, 37, 40]
total_economizado = df_logs[df_logs['acao'].str.contains("NÃO IRRIGAR|ADIAR", na=False)].shape[0]

with c1:
    st.metric("Ações de Economia Geradas", total_economizado)
    st.success("Impacto: Redução de custos evitando o 'Horário de Ponta' (3x mais caro)[cite: 9].")

with c2:
    df_distribuicao = df_logs['acao'].value_counts().reset_index()
    fig_kpi = px.bar(df_distribuicao, x='acao', y='count', title="Distribuição de Decisões do Algoritmo Pleno",
                     labels={'acao': 'Ação Tomada', 'count': 'Frequência'}, color='acao')
    st.plotly_chart(fig_kpi, use_container_width=True)