import streamlit as st
import pandas as pd

# Carregar os dados
@st.cache_data
def load_data():
    df = pd.read_excel("PesquisaOD_2.xlsx", sheet_name="RESPOSTAS")
    return df

df = load_data()

st.title("📍 Pesquisa Origem-Destino - Região Metropolitana")

st.sidebar.header("Filtros")

# Filtros laterais
idade = st.sidebar.multiselect("Faixa etária", options=df["Qual sua faixa etária?"].unique())
genero = st.sidebar.multiselect("Gênero", options=df["Qual seu gênero?"].unique())
origem = st.sidebar.multiselect("Município de Origem", options=df["Qual o município de ORIGEM"].unique())
destino = st.sidebar.multiselect("Município de Destino", options=df["Qual o município de DESTINO"].unique())

# Aplicar filtros
df_filtrado = df.copy()
if idade:
    df_filtrado = df_filtrado[df_filtrado["Qual sua faixa etária?"].isin(idade)]
if genero:
    df_filtrado = df_filtrado[df_filtrado["Qual seu gênero?"].isin(genero)]
if origem:
    df_filtrado = df_filtrado[df_filtrado["Qual o município de ORIGEM"].isin(origem)]
if destino:
    df_filtrado = df_filtrado[df_filtrado["Qual o município de DESTINO"].isin(destino)]

# Mostrar dados filtrados
st.subheader("📄 Dados Filtrados")
st.dataframe(df_filtrado)

# Estatísticas básicas
st.subheader("📈 Estatísticas da Amostra")
st.write("Total de respostas:", df_filtrado.shape[0])
st.write("Principais meios de transporte utilizados:")
st.bar_chart(df_filtrado["Qual foi o principal meio de transporte que você usou?"].value_counts())

st.write("Motivos mais comuns da viagem:")
st.bar_chart(df_filtrado["Qual o motivo da viagem?"].value_counts())

st.write("Tempo de duração das viagens:")
st.bar_chart(df_filtrado["Quanto tempo durou a viagem?"].value_counts())
