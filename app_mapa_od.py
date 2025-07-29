import streamlit as st
import pandas as pd

# Função para carregar os dados com tratamento de erro
@st.cache_data
def carregar_dados():
    try:
        return pd.read_csv("Planilha_Tratada_Final.csv", sep=";", quotechar='"')
    except FileNotFoundError:
        st.error("Arquivo 'Planilha_Tratada_Final.csv' não encontrado.")
        return pd.DataFrame()

# Carregando os dados
df = carregar_dados()

# Título do aplicativo
st.title("📍 Matriz Origem-Destino - Região Metropolitana")

# Verifica se os dados foram carregados corretamente
if df.empty:
    st.stop()

# Filtros na barra lateral
st.sidebar.header("Filtros")

origens = st.sidebar.multiselect("Origem", options=df["ORIGEM"].dropna().unique())
destinos = st.sidebar.multiselect("Destino", options=df["DESTINO"].dropna().unique())
transportes = st.sidebar.multiselect("Meio de Transporte", options=df["Qual foi o principal meio de transporte que você usou?"].dropna().unique())

# Aplicando os filtros
df_filtrado = df.copy()

if origens:
    df_filtrado = df_filtrado[df_filtrado["ORIGEM"].isin(origens)]
if destinos:
    df_filtrado = df_filtrado[df_filtrado["DESTINO"].isin(destinos)]
if transportes:
    df_filtrado = df_filtrado[df_filtrado["Qual foi o principal meio de transporte que você usou?"].isin(transportes)]

# Exibir os dados filtrados
st.subheader("📄 Dados Filtrados")
st.dataframe(df_filtrado)

# Estatísticas e Gráficos
st.subheader("📊 Estatísticas")

st.write(f"**Total de registros filtrados:** {df_filtrado.shape[0]}")

if not df_filtrado.empty:
    st.write("**Viagens por município de origem**")
    st.bar_chart(df_filtrado["ORIGEM"].value_counts())

    st.write("**Viagens por município de destino**")
    st.bar_chart(df_filtrado["DESTINO"].value_counts())

    st.write("**Meios de transporte utilizados**")
    st.bar_chart(df_filtrado["Qual foi o principal meio de transporte que você usou?"].value_counts())
else:
    st.info("Nenhum dado disponível com os filtros aplicados.")

