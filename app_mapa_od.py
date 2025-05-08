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

# Função para obter valores únicos de uma coluna (com verificação se existe)
def get_unique_values(df, column_name):
    if column_name in df.columns:
        return ["Todos"] + sorted(df[column_name].dropna().unique().tolist())
    else:
        return ["Todos"]

# Motivo Agrupado
motivo_col = "motivo_agrupado"
motivos = get_unique_values(df, motivo_col)
motivo_sel = st.sidebar.multiselect("Motivo da Viagem", motivos, default=["Todos"])

# Renda Familiar
renda_col = "qual_sua_renda_familiar_mensal"
rendas = get_unique_values(df, renda_col)
renda_sel = st.sidebar.multiselect("Renda Familiar Mensal", rendas, default=["Todos"])

# Tipo de Viagem
tipo_col = "a_sua_ultima_viagem_intermunicipal_(entre_municipios)_foi"
tipos = get_unique_values(df, tipo_col)
tipo_sel = st.sidebar.multiselect("Tipo da Viagem", tipos, default=["Todos"])

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
