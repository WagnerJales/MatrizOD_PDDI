# Carregar bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar layout da página
st.set_page_config(layout="wide")

# --- Passo 1: Carregar o CSV corretamente ---
@st.cache_data
def load_data():
    df = pd.read_csv("Pesquisa_OD_RMGSL_Agrupada.csv", encoding='latin1', sep=';', on_bad_lines='skip')
    return df

# Carregar dados
st.title("Visualizador da Pesquisa OD - RMGSL")
df = load_data()

# Exibir dados
st.subheader("Visualização dos Dados Brutos (OD)")
st.dataframe(df)

# --- Passo 2: Filtros para explorar os dados ---

st.sidebar.header("Filtros")

# Filtro por Motivo Agrupado
motivos = ["Todos"] + sorted(df["Motivo Agrupado"].dropna().unique().tolist())
motivo_sel = st.sidebar.multiselect("Motivo da Viagem", motivos, default=["Todos"])

# Filtro por Renda
rendas = ["Todos"] + sorted(df["Qual sua renda familiar mensal?"].dropna().unique().tolist())
renda_sel = st.sidebar.multiselect("Renda Familiar", rendas, default=["Todos"])

# Filtro por Tipo de Viagem
tipos_viagem = ["Todos"] + sorted(df["A sua última viagem intermunicipal (entre municípios) foi:"].dropna().unique().tolist())
tipo_sel = st.sidebar.multiselect("Tipo da Viagem", tipos_viagem, default=["Todos"])

# --- Passo 3: Aplicar filtros ---

df_filtrado = df.copy()

if "Todos" not in motivo_sel:
    df_filtrado = df_filtrado[df_filtrado["Motivo Agrupado"].isin(motivo_sel)]

if "Todos" not in renda_sel:
    df_filtrado = df_filtrado[df_filtrado["Qual sua renda familiar mensal?"].isin(renda_sel)]

if "Todos" not in tipo_sel:
    df_filtrado = df_filtrado[df_filtrado["A sua última viagem intermunicipal (entre municípios) foi:"].isin(tipo_sel)]

st.subheader("Total de Registros Filtrados")
st.metric(label="Quantidade", value=len(df_filtrado))

# --- Passo 4: Visualização gráfica ---

st.subheader("Distribuição das Viagens por Motivo")
fig_motivo = px.histogram(df_filtrado, x="Motivo Agrupado", color="Motivo Agrupado", text_auto=True)
st.plotly_chart(fig_motivo, use_container_width=True)

st.subheader("Distribuição das Viagens por Renda")
fig_renda = px.histogram(df_filtrado, x="Qual sua renda familiar mensal?", color="Qual sua renda familiar mensal?", text_auto=True)
st.plotly_chart(fig_renda, use_container_width=True)

st.subheader("Distribuição das Viagens por Tipo de Viagem")
fig_tipo = px.histogram(df_filtrado, x="A sua última viagem intermunicipal (entre municípios) foi:", color="A sua última viagem intermunicipal (entre municípios) foi:", text_auto=True)
st.plotly_chart(fig_tipo, use_container_width=True)

# --- Passo 5: Nota de rodapé ---
st.markdown("""
<div style='text-align: center; font-size: 14px;'>
Fonte: Pesquisa OD RMGSL Agrupada | Desenvolvido por Wagner Jales - <a href='https://www.linkedin.com/in/wagner-jales-663b4831/' target='_blank'>LinkedIn</a>
</div>
""", unsafe_allow_html=True)
""", unsafe_allow_html=True)
