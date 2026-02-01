import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURAÇÃO GERAL DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Green Horizon | Intelligence", 
    layout="wide"
)

# ==============================================================================
# 2. ESTILIZAÇÃO CSS AVANÇADA (UI/UX)
# ==============================================================================
st.markdown("""
    <style>
    /* Importação de tipografia corporativa */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

    /* --- SIDEBAR: IDENTIDADE VISUAL --- */
    section[data-testid="stSidebar"] {
        background-color: #143d29; /* Fundo Verde Floresta Sólido */
        border-right: 5px solid #4CAF50; /* Linha de demarcação visual */
    }
    
    /* Padronização de cor (Branco) para elementos textuais da Sidebar */
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }

    /* --- CORREÇÃO DO CALENDÁRIO (TEXTO CENTRALIZADO) --- */
    /* Garante que o texto dentro do input branco seja escuro e CENTRALIZADO */
    section[data-testid="stSidebar"] input {
        color: #31333F !important;
        font-weight: 600;
        text-align: center !important; /* <--- ALINHAMENTO CENTRALIZADO */
    }
    section[data-testid="stSidebar"] [data-testid="stDateInput"] svg {
        fill: #31333F !important;
    }
    
    /* --- COMPONENTES PERSONALIZADOS (CARDS) --- */
    /* Container translúcido com efeito Glassmorphism */
    .sidebar-card {
        background-color: rgba(255, 255, 255, 0.08);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
    }
    .sidebar-card h5 {
        margin-top: 0;
        font-size: 13px;
        color: #66BB6A !important; 
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .sidebar-card p {
        font-size: 13px;
        margin-bottom: 4px;
        color: #E0E0E0 !important;
    }
    .sidebar-card b {
        color: #FFFFFF !important;
    }
    
    /* --- RODAPÉ TÉCNICO --- */
    .sidebar-footer {
        font-size: 11px;
        color: rgba(255, 255, 255, 0.4) !important;
        text-align: center;
        margin-top: 30px;
    }

    /* --- LAYOUT PRINCIPAL --- */
    .stApp { background-color: #F0F2F6; color: #31333F; }
    
    /* KPI CARDS (Métricas de Negócio) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #2E7D32; /* Indicador de Status Verde */
        min-height: 160px; 
    }
    div[data-testid="stMetricValue"] {
        font-size: 26px; /* <--- AUMENTADO DE 22px PARA 26px PARA MAIOR DESTAQUE */
        color: #1E1E1E; 
        font-weight: 800;
        white-space: normal !important; word-wrap: break-word !important;
        line-height: 1.3; overflow: visible !important;
    }
    div[data-testid="stMetricLabel"] { font-size: 15px; color: #616161; font-weight: 600; }

    /* CABEÇALHO DA PÁGINA (BRANDING) */
    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 60px !important; font-weight: 900 !important;
        background: -webkit-linear-gradient(45deg, #143d29, #4CAF50);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: -20px; margin-bottom: -5px;
        letter-spacing: -2px; text-transform: uppercase;
    }
    .subtitle {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 20px; color: #555555; font-weight: 400;
        margin-bottom: 30px; border-left: 4px solid #4CAF50; padding-left: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. CAMADA DE DADOS (ETL & INTEGRAÇÃO)
# ==============================================================================
@st.cache_data
def carregar_dados_reais():
    """
    Realiza a conexão com o Data Warehouse (SQLite) e carrega os datasets necessários.
    Executa o pré-processamento de timestamps e joins relacionais.
    """
    try:
        # Conexão com Banco de Dados Analítico
        conn = sqlite3.connect('etl/green_horizon.db')
        
        # Ingestão de Tabelas Fato e Dimensão
        df_clima_limpo = pd.read_sql_query("SELECT * FROM historico_clima", conn)
        df_logs_raw = pd.read_sql_query("SELECT * FROM logs_decisao", conn)
        conn.close()
        
        # Carregamento de Dados Brutos (Raw) para Auditoria
        df_sujo = pd.read_csv('data/historico_leituras_sujo.csv')
        
        # Normalização de Timestamps (ISO 8601)
        for df in [df_clima_limpo, df_sujo, df_logs_raw]:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', format='mixed')
            df.dropna(subset=['timestamp'], inplace=True)
        
        # Enriquecimento de Dados: Join de Decisões com Dados Climáticos
        # Left Join garante que toda decisão tenha o contexto climático associado
        df_logs = pd.merge(df_logs_raw, df_clima_limpo[['timestamp', 'temp_ambiente']], on='timestamp', how='left')
        
        return df_clima_limpo, df_logs, df_sujo
    except Exception as e:
        st.error(f"Falha crítica na conexão com o banco de dados: {e}")
        return None, None, None

# Execução do Pipeline de Dados
df_limpo, df_logs, df_sujo = carregar_dados_reais()

if df_limpo is not None:
    # ==============================================================================
    # 4. BARRA LATERAL (CONTROLE OPERACIONAL)
    # ==============================================================================
    
    # CABEÇALHO UNIFICADO (LOGO VERTICAL - AJUSTADO PARA NÃO QUEBRAR LINHA)
    st.sidebar.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 25px;">
        <img src="https://img.icons8.com/fluency/96/natural-food.png" width="80" style="margin-bottom: 10px;">
        <div>
            <h1 style="color: white; font-family: 'Montserrat', sans-serif; font-size: 18px; font-weight: 900; margin: 0; line-height: 1.1; white-space: nowrap;">CENTRAL DE COMANDO</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Painel de Informações da Unidade (Metadados do Projeto)
    st.sidebar.markdown("""
    <div class="sidebar-card">
        <h5>📍 Detalhes da Unidade</h5>
        <p><b>Cliente:</b> Smart Farm Solutions</p>
        <p><b>Unidade:</b> Experimental - RJ</p>
        <p><b>Local:</b> Prox. Cristo Redentor</p>
    </div>
    """, unsafe_allow_html=True)

    # Filtro Temporal (Date Range Picker)
    st.sidebar.markdown("<h4 style='color: white; margin-bottom: 5px;'>📅 Período de Análise</h4>", unsafe_allow_html=True)
    min_date = df_limpo['timestamp'].min().date()
    max_date = df_limpo['timestamp'].max().date()
    
    # Input de Data (Formato BR)
    data_sel = st.sidebar.date_input(
        "Selecione o Intervalo", 
        [min_date, max_date], 
        label_visibility="collapsed",
        format="DD/MM/YYYY"
    )

    # --- LÓGICA DE FILTRAGEM ---
    if len(data_sel) == 2:
        start_date, end_date = data_sel
        # Filtra os dados com base na seleção do usuário
        df_limpo = df_limpo[(df_limpo['timestamp'].dt.date >= start_date) & (df_limpo['timestamp'].dt.date <= end_date)]
        df_logs  = df_logs[(df_logs['timestamp'].dt.date >= start_date) & (df_logs['timestamp'].dt.date <= end_date)]
        df_sujo  = df_sujo[(df_sujo['timestamp'].dt.date >= start_date) & (df_sujo['timestamp'].dt.date <= end_date)]

    # Monitoramento de Saúde do Sistema (Health Check)
    st.sidebar.markdown("""
    <div class="sidebar-card" style="margin-top: 25px;">
        <h5>📶 Status do Sistema</h5>
        <p>🟢 Conexão: <b>Estável</b></p>
        <p>📡 Sensores: <b>Ativos</b></p>
        <p>🔄 Última Sinc.: <b>Tempo Real</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Versionamento
    st.sidebar.markdown('<p class="sidebar-footer">v2.4.1 | Green Horizon System</p>', unsafe_allow_html=True)

    # ==============================================================================
    # 5. DASHBOARD PRINCIPAL (VIEW)
    # ==============================================================================
    st.markdown('<h1 class="main-title">Green Horizon</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AgroTech 2.0 | Monitoramento de Precisão & Inteligência de Dados</p>', unsafe_allow_html=True)
    
    # Verifica se há dados após o filtro para evitar erros
    if not df_logs.empty:
        # --- KPIs em Tempo Real ---
        ultima_leitura = df_logs.iloc[-1]
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Umidade do Solo", f"{ultima_leitura['umidade_solo']}%")
        with m2:
            st.metric("Previsão de Chuva", f"{ultima_leitura['previsao_chuva']}mm")
        with m3:
            st.metric("Tarifa Energética", ultima_leitura['tarifa'])
        with m4:
            # Cálculo de ROI (Ciclos economizados pela IA)
            acoes_inteligentes = df_logs[df_logs['acao'].str.contains("AGUARDAR|ADIAR", na=False, case=False)].shape[0]
            eficiencia = (acoes_inteligentes / len(df_logs)) * 100 if len(df_logs) > 0 else 0
            st.metric("Economia de Ciclos (%)", f"{eficiencia:.1f}%")

        # Log de Auditoria da Decisão Mais Recente
        st.info(f"**⚙️ Decisão Operacional:** {ultima_leitura['acao']} — **Justificativa Técnica:** {ultima_leitura['motivo']}")

        # ==============================================================================
        # 6. VISUALIZAÇÃO DE DADOS (ANALYTICS)
        # ==============================================================================
        tab1, tab2, tab3 = st.tabs(["📊 Auditoria de Sensores", "📈 Correlação Hídrica", "💰 Impacto de Negócio"])

        # Gráfico 1: Qualidade de Dados (Data Quality Assurance)
        with tab1:
            st.subheader("Sanitização de Dados em Tempo Real")
            fig_auditoria = go.Figure()
            
            # Série de Dados Sujos (Outliers Detectados)
            fig_auditoria.add_trace(go.Scatter(
                x=df_sujo['timestamp'], 
                y=df_sujo['temp_ambiente'], 
                name="Sensor Sujo (Erro)", 
                line=dict(color='#E53935', width=1, dash='dot')
            ))
            
            # Série de Dados Limpos (Pós-ETL)
            fig_auditoria.add_trace(go.Scatter(
                x=df_limpo['timestamp'], 
                y=df_limpo['temp_ambiente'], 
                name="Sensor Limpo (IA)", 
                line=dict(color='#1E88E5', width=2)
            ))
            
            fig_auditoria.update_layout(template="plotly_white", paper_bgcolor='white', plot_bgcolor='white', hovermode="x unified")
            st.plotly_chart(fig_auditoria, use_container_width=True)

        # Gráfico 2: Matriz de Decisão (Scatter Plot)
        with tab2:
            st.subheader("Análise Multivariada: Solo vs. Clima")
            fig_scatter = px.scatter(
                df_logs, 
                x="temp_ambiente", 
                y="umidade_solo", 
                color="acao",
                title="Matriz de Decisão Operacional: Solo vs. Clima", 
                labels={
                    "temp_ambiente": "Temperatura Ambiente (°C)", 
                    "umidade_solo": "Umidade do Solo (%)", 
                    "acao": "Ação do Sistema"
                },
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_scatter.update_layout(template="plotly_white", paper_bgcolor='white', plot_bgcolor='white')
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Gráfico 3: Impacto Financeiro (Financial Insights)
        with tab3:
            c1, c2 = st.columns([1, 2])
            
            # Resumo Executivo
            with c1:
                total_economizado = df_logs[df_logs['acao'].str.contains("AGUARDAR|ADIAR", na=False, case=False)].shape[0]
                st.markdown(f"""
                <div style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
                    <h3 style="color: #2E7D32;">Economia Gerada</h3>
                    <p style="font-size: 18px;">O algoritmo evitou <b>{total_economizado}</b> ciclos de irrigação desnecessários.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Distribuição de Ações (Donut Chart)
            with c2:
                df_dist = df_logs['acao'].value_counts().reset_index()
                fig_pie = px.pie(
                    df_dist, 
                    values='count', 
                    names='acao', 
                    hole=.4,
                    title="Mix de Operações da Fazenda"
                )
                fig_pie.update_layout(template="plotly_white", paper_bgcolor='white')
                st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum dado encontrado para o período selecionado. Tente ajustar o intervalo de datas na barra lateral.")
else:
    st.error("Erro crítico: Não foi possível carregar o banco de dados local.")