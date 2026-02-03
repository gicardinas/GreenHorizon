import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURAÇÕES GERAIS E SISTEMA DE DESIGN
# ==============================================================================
st.set_page_config(
    page_title="Green Horizon | Intelligence", 
    layout="wide"
)

# Design System: Constantes de Cor e Estilo
CHART_TEXT_COLOR = '#31333F'  # Alto contraste para leitura
CHART_GRID_STRONG = '#B0B0B0' # Grade estrutural
CHART_GRID_SOFT = '#E5E5E5'   # Grade suavizada

# Paleta de Cores (Identidade Visual Azul - Consistente em todos os gráficos)
THEME_COLOR_PALETTE = ['#1E88E5', '#42A5F5', '#64B5F6', '#90CAF9', '#BBDEFB']

# Template base do Plotly (Dicionário robusto para compatibilidade Cross-Server)
layout_padrao_charts = {
    "template": "plotly_white",
    "paper_bgcolor": "rgba(0,0,0,0)", 
    "plot_bgcolor": "rgba(0,0,0,0)",  
    "font": {"color": CHART_TEXT_COLOR},
    "xaxis": {
        "tickfont": {"color": CHART_TEXT_COLOR},
        "titlefont": {"color": CHART_TEXT_COLOR},
        "gridcolor": CHART_GRID_STRONG, 
        "gridwidth": 1,
        "zeroline": False
    },
    "yaxis": {
        "tickfont": {"color": CHART_TEXT_COLOR},
        "titlefont": {"color": CHART_TEXT_COLOR},
        "gridcolor": CHART_GRID_STRONG,
        "gridwidth": 1,
        "zeroline": False
    },
    "legend": {"font": {"color": CHART_TEXT_COLOR}}
}

PLOTLY_CONFIG = {'locale': 'pt-br'}

# ==============================================================================
# 2. ESTILIZAÇÃO CSS (UI/UX)
# ==============================================================================
st.markdown("""
    <style>
    /* Tipografia: Poppins (Títulos) e Inter (Corpo) via Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;700;800&display=swap');

    /* Reset Global de Fontes */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3, h4, h5 { font-family: 'Poppins', sans-serif !important; }

    /* Customização da Barra Lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #143d29;
        border-right: 5px solid #4CAF50;
    }
    
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] input {
        color: #31333F !important;
        font-weight: 600;
        text-align: center !important; 
    }
    section[data-testid="stSidebar"] [data-testid="stDateInput"] svg {
        fill: #31333F !important;
    }
    
    /* Cards da Sidebar */
    .sidebar-card {
        background-color: rgba(255, 255, 255, 0.08);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
    }
    .sidebar-card h5 {
        margin-top: 0; font-size: 13px; color: #66BB6A !important; 
        font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;
    }
    .sidebar-card p { font-size: 13px; margin-bottom: 4px; color: #E0E0E0 !important; }
    .sidebar-card b { color: #FFFFFF !important; }
    .sidebar-footer { font-size: 11px; color: rgba(255, 255, 255, 0.4) !important; text-align: center; margin-top: 30px; }

    /* Fundo da Aplicação */
    .stApp { background-color: #F0F2F6; color: #31333F; }
    
    /* KPI Cards (Métricas) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #2E7D32;
        min-height: 160px; /* Garante altura para 2 linhas */
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 26px; /* Tamanho ajustado para impacto visual */
        color: #1E1E1E; 
        font-weight: 800;
        font-family: 'Poppins', sans-serif;
    }
    
    /* FIX: Permite quebra de linha e ajusta espaçamento */
    div[data-testid="stMetricValue"] > div {
        white-space: normal !important;     /* Permite quebra de linha */
        word-wrap: break-word !important;   /* Quebra palavras longas se necessário */
        overflow-wrap: break-word !important;
        line-height: 1.1 !important;        /* Altura de linha mais justa para ficar bonito */
        text-overflow: clip !important;     /* Remove reticências */
        overflow: visible !important;
    }
    
    div[data-testid="stMetricLabel"] { font-size: 15px; color: #616161; font-weight: 600; }

    /* Card de Insights */
    .custom-insight-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 6px solid #2E7D32;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    /* Cabeçalho */
    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 60px !important; font-weight: 900 !important;
        background: -webkit-linear-gradient(45deg, #143d29, #4CAF50);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-top: -20px; margin-bottom: -5px;
        letter-spacing: -2px; text-transform: uppercase;
    }
    .subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 20px; color: #555555; font-weight: 400;
        margin-bottom: 30px; border-left: 4px solid #4CAF50; padding-left: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. CAMADA DE DADOS (ETL)
# ==============================================================================
@st.cache_data
def carregar_dados_reais():
    """
    Carrega, limpa e integra dados de SQLite e CSV.
    """
    try:
        conn = sqlite3.connect('etl/green_horizon.db')
        df_clima_limpo = pd.read_sql_query("SELECT * FROM historico_clima", conn)
        df_logs_raw = pd.read_sql_query("SELECT * FROM logs_decisao", conn)
        conn.close()
        
        df_sujo = pd.read_csv('data/historico_leituras_sujo.csv')
        
        # Tratamento de timestamp
        for df in [df_clima_limpo, df_sujo, df_logs_raw]:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', format='mixed')
            df.dropna(subset=['timestamp'], inplace=True)
        
        # Junção de tabelas
        df_logs = pd.merge(df_logs_raw, df_clima_limpo[['timestamp', 'temp_ambiente']], on='timestamp', how='left')
        
        return df_clima_limpo, df_logs, df_sujo
    except Exception as e:
        st.error(f"Erro de conexão com dados: {e}")
        return None, None, None

df_limpo, df_logs, df_sujo = carregar_dados_reais()

if df_limpo is not None:
    # ==============================================================================
    # 4. SIDEBAR (CONTROLES)
    # ==============================================================================
    st.sidebar.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; text-align: center; padding-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 25px;">
        <img src="https://img.icons8.com/fluency/96/natural-food.png" width="80" style="margin-bottom: 10px;">
        <div>
            <h1 style="color: white; font-family: 'Poppins', sans-serif; font-size: 18px; font-weight: 900; margin: 0; line-height: 1.1; white-space: nowrap;">CENTRAL DE COMANDO</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("""
    <div class="sidebar-card">
        <h5>📍 Detalhes da Unidade</h5>
        <p><b>Cliente:</b> Smart Farm Solutions</p>
        <p><b>Unidade:</b> Experimental - RJ</p>
        <p><b>Local:</b> Próximo ao Cristo Redentor</p>
    </div>
    """, unsafe_allow_html=True)

    # Filtro Temporal
    st.sidebar.markdown("<h4 style='color: white; margin-bottom: 5px;'>📅 Período de Análise</h4>", unsafe_allow_html=True)
    min_date = df_limpo['timestamp'].min().date()
    max_date = df_limpo['timestamp'].max().date()
    
    data_sel = st.sidebar.date_input(
        "Selecione o Intervalo", 
        [min_date, max_date], 
        label_visibility="collapsed",
        format="DD/MM/YYYY"
    )

    if len(data_sel) == 2:
        start_date, end_date = data_sel
        df_limpo = df_limpo[(df_limpo['timestamp'].dt.date >= start_date) & (df_limpo['timestamp'].dt.date <= end_date)]
        df_logs  = df_logs[(df_logs['timestamp'].dt.date >= start_date) & (df_logs['timestamp'].dt.date <= end_date)]
        df_sujo  = df_sujo[(df_sujo['timestamp'].dt.date >= start_date) & (df_sujo['timestamp'].dt.date <= end_date)]

    st.sidebar.markdown("""
    <div class="sidebar-card" style="margin-top: 25px;">
        <h5>📶 Status do Sistema</h5>
        <p>🟢 Conexão: <b>Estável</b></p>
        <p>📡 Sensores: <b>Ativos</b></p>
        <p>🔄 Sincronização: <b>Automática</b></p>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown('<p class="sidebar-footer">v2.4.1 | Green Horizon System</p>', unsafe_allow_html=True)

    # ==============================================================================
    # 5. DASHBOARD (VISUALIZAÇÃO)
    # ==============================================================================
    st.markdown('<h1 class="main-title">Green Horizon</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AgroTech 2.0 | Monitoramento de Precisão & Inteligência de Dados</p>', unsafe_allow_html=True)
    
    if not df_logs.empty:
        ultima_leitura = df_logs.iloc[-1]
        
        # Cards de KPI
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Umidade do Solo", f"{ultima_leitura['umidade_solo']}%")
        with m2:
            st.metric("Previsão de Chuva", f"{ultima_leitura['previsao_chuva']}mm")
        with m3:
            st.metric("Tarifa Energética", ultima_leitura['tarifa'])
        with m4:
            acoes_inteligentes = df_logs[df_logs['acao'].str.contains("AGUARDAR|ADIAR", na=False, case=False)].shape[0]
            eficiencia = (acoes_inteligentes / len(df_logs)) * 100 if len(df_logs) > 0 else 0
            st.metric("Economia de Ciclos (%)", f"{eficiencia:.1f}%")

        st.info(f"**⚙️ Decisão Operacional:** {ultima_leitura['acao']} — **Justificativa Técnica:** {ultima_leitura['motivo']}")

        tab1, tab2, tab3 = st.tabs(["📊 Auditoria de Sensores", "📈 Correlação Hídrica", "💰 Impacto de Negócio"])

        # --- GRÁFICO 1: AUDITORIA DE DADOS ---
        with tab1:
            st.subheader("Auditoria da Qualidade dos Dados")
            fig_auditoria = go.Figure()
            
            # Dados Brutos (Sujo)
            fig_auditoria.add_trace(go.Scatter(
                x=df_sujo['timestamp'], 
                y=df_sujo['temp_ambiente'], 
                name="Leitura Bruta (Raw)", 
                line=dict(color='#E53935', width=1, dash='dot')
            ))
            
            # Dados Tratados (Validado)
            fig_auditoria.add_trace(go.Scatter(
                x=df_limpo['timestamp'], 
                y=df_limpo['temp_ambiente'], 
                name="Dado Tratado (Validado)", 
                line=dict(color='#1E88E5', width=2)
            ))
            
            # Aplicação de layout com tratamento de erro (Fallback para Cloud)
            try:
                fig_auditoria.update_layout(**layout_padrao_charts)
            except Exception:
                fig_auditoria.update_layout(template="plotly_white")
                
            fig_auditoria.update_layout(hovermode="x unified", title_text="", margin=dict(t=20))

            # Ajuste Fino dos Eixos
            fig_auditoria.update_yaxes(
                title_text="Temperatura (°C)",
                title_font=dict(color=CHART_TEXT_COLOR),
                tickvals=[0, 100, 200, 300, 400, 500],
                range=[-20, 530],
                gridcolor=CHART_GRID_SOFT, 
                zeroline=True,             
                zerolinecolor=CHART_GRID_STRONG,
                zerolinewidth=1
            )
            fig_auditoria.update_xaxes(
                gridcolor=CHART_GRID_SOFT,
                zeroline=True,
                zerolinecolor=CHART_GRID_STRONG,
                zerolinewidth=1
            )

            st.plotly_chart(fig_auditoria, use_container_width=True, config=PLOTLY_CONFIG)

        # --- GRÁFICO 2: MATRIZ DE DECISÃO ---
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
                color_discrete_sequence=THEME_COLOR_PALETTE
            )
            
            try:
                fig_scatter.update_layout(**layout_padrao_charts)
            except Exception:
                fig_scatter.update_layout(template="plotly_white")
            
            # Travamento de eixos para contexto visual
            fig_scatter.update_xaxes(range=[0, 45])  
            fig_scatter.update_yaxes(range=[0, 100])
            fig_scatter.update_traces(marker=dict(size=18)) 
            
            st.plotly_chart(fig_scatter, use_container_width=True, config=PLOTLY_CONFIG)

        # --- GRÁFICO 3: DISTRIBUIÇÃO E ECONOMIA ---
        with tab3:
            c1, c2 = st.columns([1, 2])
            
            with c1:
                total_economizado = df_logs[df_logs['acao'].str.contains("AGUARDAR|ADIAR", na=False, case=False)].shape[0]
                st.markdown(f"""
                <div class="custom-insight-card">
                    <h3 style="color: #2E7D32; margin-top: 0;">Economia Gerada</h3>
                    <p style="font-size: 18px; color: #1E1E1E;">O algoritmo evitou <b>{total_economizado}</b> ciclos de irrigação desnecessários.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with c2:
                df_dist = df_logs['acao'].value_counts().reset_index()
                fig_pie = px.pie(
                    df_dist, 
                    values='count', 
                    names='acao', 
                    hole=.4,
                    title="Mix de Operações da Fazenda",
                    color_discrete_sequence=THEME_COLOR_PALETTE
                )
                
                try:
                    fig_pie.update_layout(**layout_padrao_charts)
                except Exception:
                    fig_pie.update_layout(template="plotly_white")
                    
                fig_pie.update_traces(textfont_size=24)
                
                st.plotly_chart(fig_pie, use_container_width=True, config=PLOTLY_CONFIG)
    else:
        st.warning("⚠️ Nenhum dado encontrado. Ajuste o filtro de datas.")
else:
    st.error("Erro crítico: Banco de dados indisponível.")