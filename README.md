<h1 align="center">🌱 Projeto Green Horizon - AgroTech 2.0</h1>

<p align="center">
  <strong>Sistema Inteligente de Irrigação com Dados Climáticos e Tarifas de Energia</strong>
</p>

<p align="center">
  📍 Unidade Experimental: <strong>Rio de Janeiro (Cristo Redentor)</strong><br>
  🔗 Repositório: <a href="https://github.com/gicardinas/GreenHorizon">GitHub</a> | 
  🌐 Dashboard: <a href="https://greenhorizon.streamlit.app/">Streamlit</a>
</p>

<hr>

<h2>📌 Visão Geral</h2>

<p>
O <strong>Green Horizon</strong> é um projeto de <b>AgroTech preditivo</b> que simula um sistema automatizado de irrigação agrícola,
integrando dados históricos de sensores, previsão climática em tempo real e tarifas de energia.
</p>

<p>O sistema decide automaticamente se deve:</p>

<ul>
  <li>✅ Irrigar</li>
  <li>⏳ Adiar</li>
  <li>🚫 Não irrigar</li>
</ul>

<p>Com foco em:</p>

<ul>
  <li>🌿 Economia de água</li>
  <li>⚡ Economia de energia</li>
  <li>📈 Eficiência operacional</li>
</ul>

<hr>

<h2>🏗️ Estrutura do Projeto</h2>

<pre>
GREENHORIZON/
│
├── backend/
│   ├── clima_API.py
│   ├── decisao_irrigacao.py
│   ├── testar_sistema.py
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── config_culturas.csv
│   ├── historico_leituras_sujo.csv
│   └── tarifas_energia.csv
│
├── database/
│   └── agro.db
│
├── etl/
│   ├── etl_pipeline.py
│   ├── limpar_dados.py
│   └── green_horizon.db
│
├── requirements.txt
└── README.md
</pre>

<hr>

<h2>⚙️ Tecnologias Utilizadas</h2>

<ul>
  <li><b>Linguagem:</b> Python</li>
  <li><b>Bibliotecas:</b> pandas, sqlite3, datetime, pathlib, streamlit, plotly.express, requests</li>
  <li><b>API:</b> Open-Meteo</li>
</ul>

<hr>

<h2>🧪 Fase 1 – Engenharia de Dados (ETL)</h2>

<p><b>Responsáveis:</b> Giovanna e Sabrina<br>
<b>Revisão:</b> Mateus</p>

<ul>
  <li>Remoção de valores nulos</li>
  <li>Remoção de ruídos (temperaturas &gt; 60°C)</li>
  <li>Criação de script de limpeza</li>
  <li>Criação de banco SQLite</li>
  <li>Inserção de dados tratados</li>
  <li>Validação da base limpa</li>
</ul>

<hr>

<h2>🤖 Fase 2 – Lógica de Decisão</h2>

<p><b>Responsáveis:</b> Eric e Mateus</p>

<p><b>Entradas do sistema:</b></p>

<ul>
  <li>Umidade do solo (sensor)</li>
  <li>Previsão de chuva (API)</li>
  <li>Tarifa de energia (CSV)</li>
  <li>Histórico climático (SQLite)</li>
</ul>

<p><b>Regras principais:</b></p>

<ul>
  <li>Se houver previsão de chuva → <b>AGUARDAR</b></li>
  <li>Se não houver chuva:
    <ul>
      <li>Verifica umidade do solo</li>
      <li>Verifica tarifa de energia</li>
      <li>Decide irrigar ou adiar</li>
    </ul>
  </li>
</ul>

<hr>

<h2>📊 Fase 3 – Dashboard</h2>

<p><b>Responsáveis:</b> Thayna e Rita</p>

<ul>
  <li>Exibir status do sistema</li>
  <li>Mostrar dados tratados</li>
  <li>Mostrar previsão climática</li>
  <li>KPIs de economia</li>
  <li>Gráficos de decisões</li>
</ul>

<p>🔗 Dashboard online: 
<a href="https://greenhorizon.streamlit.app/">https://greenhorizon.streamlit.app/</a>
</p>

<hr>

<h2>📈 Indicadores (KPIs)</h2>

<ul>
  <li>Umidade do solo</li>
  <li>Volume de chuva previsto</li>
  <li>Tarifa energética atual</li>
  <li>Quantidade de ações evitadas</li>
  <li>Economia financeira estimada</li>
</ul>

<hr>

<h2>▶️ Como Executar o Projeto</h2>

<pre>
git clone https://github.com/gicardinas/GreenHorizon.git
pip install -r requirements.txt
streamlit run dashboard/app.py
</pre>

<hr>

<h2>👥 Equipe</h2>

<ul>
  <li>Giovanna – ETL</li>
  <li>Sabrina – ETL</li>
  <li>Mateus – Revisão e lógica</li>
  <li>Eric – Lógica de decisão</li>
  <li>Thayna – Dashboard</li>
  <li>Rita – Dashboard</li>
</ul>

<hr>

<h2>📌 Considerações Finais</h2>

<p>
O Green Horizon demonstra a aplicação prática de conceitos de Engenharia de Dados, Ciência de Dados e Automação,
simulando um cenário real de irrigação inteligente com foco em sustentabilidade e eficiência operacional.
</p>