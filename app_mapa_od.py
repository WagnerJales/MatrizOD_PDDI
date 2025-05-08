import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

# Configurar layout da página
st.set_page_config(layout="wide")
st.title("Análise OD - Região Metropolitana de São Luís")

# Função para carregar CSV com normalização das colunas
@st.cache_data
def load_data():
    df = pd.read_csv("Pesquisa_OD_RMGSL_Agrupada.csv")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

df = load_data()

# Mostrar colunas para conferência
st.write("Colunas disponíveis:", list(df.columns))

st.sidebar.header("Filtros")

# Função auxiliar para pegar colunas de forma segura
def get_column(df, possible_names):
    for col in df.columns:
        if any(name in col for name in possible_names):
            return col
    return None

# Buscar colunas relevantes
motivo_col = get_column(df, ["motivo_agrupado"])
renda_col = get_column(df, ["renda_familiar", "qual_sua_renda_familiar_mensal"])
tipo_col = get_column(df, ["ultima_viagem", "foi"])

# Filtro: Motivo da Viagem
if motivo_col:
    motivos = ["Todos"] + sorted(df[motivo_col].dropna().unique().tolist())
    motivo_sel = st.sidebar.multiselect("Motivo da Viagem", motivos, default=["Todos"])
else:
    motivo_sel = ["Todos"]

# Filtro: Renda
if renda_col:
    rendas = ["Todos"] + sorted(df[renda_col].dropna().unique().tolist())
    renda_sel = st.sidebar.multiselect("Renda Familiar Mensal", rendas, default=["Todos"])
else:
    renda_sel = ["Todos"]

# Filtro: Tipo de Viagem
if tipo_col:
    tipos = ["Todos"] + sorted(df[tipo_col].dropna().unique().tolist())
    tipo_sel = st.sidebar.multiselect("Tipo da Viagem", tipos, default=["Todos"])
else:
    tipo_sel = ["Todos"]

# Aplicar filtros
df_filtrado = df.copy()

if "Todos" not in motivo_sel and motivo_col:
    df_filtrado = df_filtrado[df_filtrado[motivo_col].isin(motivo_sel)]

if "Todos" not in renda_sel and renda_col:
    df_filtrado = df_filtrado[df_filtrado[renda_col].isin(renda_sel)]

if "Todos" not in tipo_sel and tipo_col:
    df_filtrado = df_filtrado[df_filtrado[tipo_col].isin(tipo_sel)]

# Mostrar total
st.markdown(f"## Total de registros filtrados: **{len(df_filtrado)}**")

# Mostrar tabela
st.dataframe(df_filtrado, use_container_width=True)

# Visualização em mapa (folium simples)
st.header("Mapa de Exemplo (Folium)")
m = folium.Map(location=[-2.529722, -44.3028], zoom_start=10)
st_folium(m, width=700, height=500)

# Rodapé com crédito
st.markdown("""
<hr>
<p style='text-align:center; font-size:18px;'>
Desenvolvido por <a href='https://www.linkedin.com/in/wagner-jales-663b4831/' target='_blank'>Wagner Jales</a>
</p>
""", unsafe_allow_html=True)
