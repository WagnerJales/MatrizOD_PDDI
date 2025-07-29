import streamlit as st
import pandas as pd

# Função para carregar os dados com tratamento de erro
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("PesquisaOD_2.xlsx", sheet_name="RESPOSTAS")
        return df
    except FileNotFoundError:
        st.error("Arquivo 'PesquisaOD_2.xlsx' não encontrado.")
        return pd.DataFrame()

# Carregamento dos dados
df = load_data()

# Título do app
st.title("📍 Pesquisa Origem-Destino - Região Metropolitana")

# Verifica se os dados foram carregados corretamente
if df.empty:
    st.stop()

# Filtros na barra lateral
st.sidebar.header("Filtros")

faixas_etarias = st.sidebar.multiselect(
    "Faixa Etária",
    options=df["Qual sua faixa etária?"].dropna().unique()
)

generos = st.sidebar.multiselect(
    "Gênero",
    options=df["Qual seu gênero?"].dropna().unique()
)

origens = st.sidebar.multiselect(
    "Município de Origem",
    options=df["Qual o município de ORIGEM"].dropna().unique()
)

destinos = st.sidebar.multiselect(
    "Município de Destino",
    options=df["Qual o município de DESTINO"].dropna().unique()
)

# Aplicando filtros
df_filtrado = df.copy()

if faixas_etarias:
    df_filtrado = df_filtrado[df_filtrado["Qual sua faixa etária?"].isin(faixas_etarias)]

if generos:
    df_filtrado = df_filtrado[df_filtrado["Qual seu gênero?"].isin(generos)]

if origens:
    df_filtrado = df_filtrado[df_filtrado["Qual o município de ORIGEM"].isin(origens)]

if destinos:
    df_filtrado = df_filtrado[df_filtrado["Qual o município de DESTINO"].isin(destinos)]

# Exibir dados filtrados
st.subheader("📄 Respostas Filtradas")
st.dataframe(df_filtrado)

# Estatísticas
st.subheader("📊 Estatísticas")

st.write(f"**Total de respostas filtradas:** {df_filtrado.shape[0]}")

# Gráfico - Meio de transporte
if not df_filtrado.empty:
    st.write("**Meio de transporte mais usado**")
    st.bar_chart(df_filtrado["Qual foi o principal meio de transporte que você usou?"].value_counts())

    st.write("**Motivo da viagem**")
    st.bar_chart(df_filtrado["Qual o motivo da viagem?"].value_counts())

    st.write("**Tempo de duração das viagens**")
    st.bar_chart(df_filtrado["Quanto tempo durou a viagem?"].value_counts())
else:
    st.info("Nenhum dado disponível com os filtros selecionados.")
