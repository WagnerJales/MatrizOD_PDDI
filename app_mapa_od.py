import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium import PolyLine
import plotly.express as px

# Configuração da página
st.set_page_config(layout="wide")

# Função para carregar os dados
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("PesquisaOD_2.xlsx", engine="openpyxl")
        df = df.rename(columns={
            "Qual o motivo da viagem?": "Motivo",
            "Com que frequência você faz essa viagem?": "Frequência",
            "A viagem foi realizada em qual período do dia?": "Periodo do dia",
            "Qual foi o principal meio de transporte que você usou?": "Principal Modal",
            "Qual o município de ORIGEM": "Município ORIGEM",
            "Qual o município de DESTINO": "Município DESTINO",
        })
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.stop()

# Inicializa a página se necessário
def inicializar_pagina():
    if "pagina" not in st.session_state:
        st.session_state.pagina = "inicio"

inicializar_pagina()

# Dados dos municípios (visão por subzonas de São Luís)
coord_subzonas = {
    "São Luís - Bancaga": [-2.557948, -44.331238],
    "São Luís - Centro": [-2.515687, -44.296435],
    "São Luís - Cidade Operária": [-2.5705480438203296, -44.20412618522021],
    "São Luís - Cohab": [-2.541977, -44.212127],
    "São Luís - Cohama": [-2.5163246962493697, -44.24714652403556],
    "São Luís - Zona Industrial": [-2.614860861647258, -44.25655944286809]
}

# Dados dos municípios (visão tradicional)
coord_municipios = {
    "São Luís": [-2.538, -44.282],
    "Paço do Lumiar": [-2.510, -44.069],
    "Raposa": [-2.476, -44.096],
    "São José de Ribamar": [-2.545, -44.022],
    "Santa Rita": [-3.1457, -44.3329],
    "Morros": [-2.8644, -44.0392],
    "Icatu": [-2.762, -44.045],
    "Rosário": [-2.943, -44.254],
    "Bacabeira": [-2.969, -44.310],
    "Alcântara": [-2.416, -44.437],
    "Cachoeira Grande": [-2.930, -44.220],
    "Presidente Juscelino": [-2.915, -44.070]
}

# Página inicial
if st.session_state.pagina == "inicio":
    st.title("Pesquisa Origem-Destino - RMGSL 2025")
    st.markdown("""
    Esta aplicação apresenta os resultados da **Pesquisa Origem-Destino** realizada entre os dias **18/07/2025 a 25/07/2025**, com foco na Região Metropolitana da Grande São Luís (RMGSL):

    - **São Luís**
    - **Paço do Lumiar**
    - **Raposa**
    - **São José de Ribamar**
    - E demais municípios do entorno.

    Você pode visualizar os dados de duas formas:

    <span style='color:red'>●</span> **Por município** (visão tradicional)  
    <span style='color:navy'>●</span> **Subzonas de São Luís** (6 áreas internas)
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔴 Ver Mapa por Município"):
            st.session_state.pagina = "municipios"
            st.rerun()
    with col2:
        if st.button(":large_blue_circle: Ver Mapa com Subzonas de São Luís"):
            st.session_state.pagina = "subzonas"
            st.rerun()

# Demais páginas
else:
    df = carregar_dados()

    # Definir colunas conforme a página
    if st.session_state.pagina == "municipios":
        origem_col = "Município ORIGEM"
        destino_col = "Município DESTINO"
        coordenadas = coord_municipios
        titulo = "Mapa OD por Município"
    else:
        origem_col = "ORIGEM"
        destino_col = "DESTINO"
        coordenadas = coord_subzonas
        titulo = "Mapa OD por Subzonas de São Luís"

    st.title(titulo)
    if st.button("🢞 Voltar à Página Inicial"):
        st.session_state.pagina = "inicio"
        st.rerun()

    # Filtros
    st.sidebar.header("Filtros")
    origens = st.sidebar.multiselect("Origem:", sorted(df[origem_col].dropna().unique()), default=[])
    destinos = st.sidebar.multiselect("Destino:", sorted(df[destino_col].dropna().unique()), default=[])
    motivo = st.sidebar.multiselect("Motivo da Viagem:", sorted(df["Motivo"].dropna().unique()), default=[])
    frequencia = st.sidebar.multiselect("Frequência:", sorted(df["Frequência"].dropna().unique()), default=[])
    periodo = st.sidebar.multiselect("Período do dia:", sorted(df["Periodo do dia"].dropna().unique()), default=[])
    modal = st.sidebar.multiselect("Principal Modal:", sorted(df["Principal Modal"].dropna().unique()), default=[])
    cor_linha = st.sidebar.color_picker("Cor das linhas OD", value="#FF0000")
    peso_base = st.sidebar.slider("Espessura base das linhas", 1.0, 10.0, 2.0)
    peso_fator = st.sidebar.slider("Fator de espessura por volume", 0.01, 1.0, 0.05)

    df_filtrado = df.copy()
    if origens:
        df_filtrado = df_filtrado[df_filtrado[origem_col].isin(origens)]
    if destinos:
        df_filtrado = df_filtrado[df_filtrado[destino_col].isin(destinos)]
    if motivo:
        df_filtrado = df_filtrado[df_filtrado["Motivo"].isin(motivo)]
    if frequencia:
        df_filtrado = df_filtrado[df_filtrado["Frequência"].isin(frequencia)]
    if periodo:
        df_filtrado = df_filtrado[df_filtrado["Periodo do dia"].isin(periodo)]
    if modal:
        df_filtrado = df_filtrado[df_filtrado["Principal Modal"].isin(modal)]

    # Contagem
    st.sidebar.markdown(
        f"<span style='font-size: 24px; font-weight: bold; color: #4B8BBE;'>Total: {len(df_filtrado):,} registros</span>",
        unsafe_allow_html=True
    )

    # Construir mapa
    mapa = folium.Map(location=[-2.53, -44.3], zoom_start=10, tiles="CartoDB positron")

    # Agregando OD
    od_agrupado = df_filtrado.groupby([origem_col, destino_col]).size().reset_index(name="count")

    for _, row in od_agrupado.iterrows():
        origem = row[origem_col]
        destino = row[destino_col]
        count = row["count"]

        if origem in coordenadas and destino in coordenadas and origem != destino:
            coord_origem = coordenadas[origem]
            coord_destino = coordenadas[destino]
            folium.PolyLine([coord_origem, coord_destino], weight=peso_base + count * peso_fator, color=cor_linha, opacity=0.6).add_to(mapa)

    st_folium(mapa, width=1000, height=600)
