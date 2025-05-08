import streamlit as st
import pandas as pd

# Configurar layout da página
st.set_page_config(layout="wide")

st.title("Análise OD - Região Metropolitana de São Luís")

# Carregar os dados CSV
@st.cache_data
def load_data():
    df = pd.read_csv("Pesquisa_OD_RMGSL_Agrupada.csv")
    # Normalizar nomes de colunas para evitar KeyError
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

df = load_data()

# Verificar as colunas disponíveis
st.write("Colunas disponíveis:", list(df.columns))

# Filtros
st.sidebar.header("Filtros")

# Motivo Agrupado
motivo_col = "motivo_agrupado"
if motivo_col in df.columns:
    motivos = ["Todos"] + sorted(df[motivo_col].dropna().unique().tolist())
    motivo_sel = st.sidebar.multiselect("Motivo da Viagem", motivos, default=["Todos"])
else:
    motivo_sel = ["Todos"]

# Renda Familiar
renda_col = "qual_sua_renda_familiar_mensal"
if renda_col in df.columns:
    rendas = ["Todos"] + sorted(df[renda_col].dropna().unique().tolist())
    renda_sel = st.sidebar.multiselect("Renda Familiar Mensal", rendas, default=["Todos"])
else:
    renda_sel = ["Todos"]

# Tipo de Viagem
tipo_col = "a_sua_ultima_viagem_intermunicipal_(entre_municipios)_foi"
if tipo_col in df.columns:
    tipos = ["Todos"] + sorted(df[tipo_col].dropna().unique().tolist())
    tipo_sel = st.sidebar.multiselect("Tipo da Viagem", tipos, default=["Todos"])
else:
    tipo_sel = ["Todos"]

# Aplicar filtros
df_filtrado = df.copy()

if "Todos" not in motivo_sel:
    df_filtrado = df_filtrado[df_filtrado[motivo_col].isin(motivo_sel)]

if "Todos" not in renda_sel:
    df_filtrado = df_filtrado[df_filtrado[renda_col].isin(renda_sel)]

if "Todos" not in tipo_sel:
    df_filtrado = df_filtrado[df_filtrado[tipo_col].isin(tipo_sel)]

# Exibir total filtrado
st.markdown(f"## Total de registros filtrados: **{len(df_filtrado)}**")

# Exibir tabela
st.dataframe(df_filtrado, use_container_width=True)

# Rodapé com crédito
st.markdown("""
<hr>
<p style='text-align:center; font-size:18px;'>
Desenvolvido por <a href='https://www.linkedin.com/in/wagner-jales-663b4831/' target='_blank'>Wagner Jales</a>
</p>
""", unsafe_allow_html=True)
