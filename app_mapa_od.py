import streamlit as st
import pandas as pd
import pydeck as pdk

# Configurar layout da página
st.set_page_config(layout="wide")

# Carregar dados CSV
@st.cache_data

def load_data():
    df = pd.read_csv("Pesquisa_OD_RMGSL_Agrupada.csv")
    # Normalizar colunas: remover espaços e transformar em minúsculas
    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()

# Obter listas únicas para filtros
motivos = ["Todos"] + sorted(df["motivo agrupado"].dropna().unique().tolist())
rendas = ["Todos"] + sorted(df["qual sua renda familiar mensal?"].dropna().unique().tolist())
tipos_viagem = ["Todos"] + sorted(df["a sua última viagem intermunicipal (entre municípios) foi:"].dropna().unique().tolist())

# Filtros
st.sidebar.header("Filtros")

motivo_sel = st.sidebar.multiselect("Motivo da Viagem", motivos, default=["Todos"])
renda_sel = st.sidebar.multiselect("Renda Familiar", rendas, default=["Todos"])
tipo_sel = st.sidebar.multiselect("Tipo de Viagem", tipos_viagem, default=["Todos"])

# Aplicar filtros
df_filtrado = df.copy()

if "Todos" not in motivo_sel:
    df_filtrado = df_filtrado[df_filtrado["motivo agrupado"].isin(motivo_sel)]

if "Todos" not in renda_sel:
    df_filtrado = df_filtrado[df_filtrado["qual sua renda familiar mensal?"].isin(renda_sel)]

if "Todos" not in tipo_sel:
    df_filtrado = df_filtrado[df_filtrado["a sua última viagem intermunicipal (entre municípios) foi:"].isin(tipo_sel)]

# Mostrar dados filtrados
st.header("Dados Filtrados da Pesquisa OD")
st.dataframe(df_filtrado)

# Mostrar resumo
st.header("Resumo")
st.write(f"Total de viagens filtradas: {len(df_filtrado)}")

st.markdown("""
<small>Fonte: Pesquisa OD RMGSL - Desenvolvido por Wagner Jales (<a href='https://www.linkedin.com/in/wagner-jales-663b4831/' target='_blank'>LinkedIn</a>)</small>
""", unsafe_allow_html=True)

# Exemplo de mapa básico (opcional)
if st.checkbox("Mostrar Mapa de Origem/Destino?"):
    if "qual o município de origem" in df_filtrado.columns and "qual o município de destino" in df_filtrado.columns:
        st.map(df_filtrado.rename(columns={
            "qual o município de origem": "lat",
            "qual o município de destino": "lon"
        }))
    else:
        st.write("Colunas de origem e destino não disponíveis para mapa.")
