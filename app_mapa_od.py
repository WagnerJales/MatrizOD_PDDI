# app_od_visualizacao.py

# ======================
# Carregar bibliotecas
# ======================

import streamlit as st
import pandas as pd
import plotly.express as px

# ======================
# Configurar layout da página
# ======================
st.set_page_config(layout="wide")

# ======================
# Carregar dados CSV
# ======================
@st.cache_data
def load_data():
    df = pd.read_csv("Pesquisa_OD_RMGSL_Agrupada.csv", encoding="latin1", sep=",", on_bad_lines='skip')
    return df

df = load_data()

st.title("Visualização dos Dados OD - Região Metropolitana de São Luís")

# ======================
# Filtros interativos
# ======================
st.sidebar.header("Filtros")

motivos = ["Todos"] + sorted(df["Motivo Agrupado"].dropna().unique().tolist())
rendas = ["Todos"] + sorted(df["Qual sua renda familiar mensal?"].dropna().unique().tolist())
tipos_viagem = ["Todos"] + sorted(df["A sua última viagem intermunicipal (entre municípios) foi:"].dropna().unique().tolist())

motivo_sel = st.sidebar.selectbox("Motivo da Viagem", motivos)
renda_sel = st.sidebar.selectbox("Renda Familiar", rendas)
tipo_viagem_sel = st.sidebar.selectbox("Tipo de Viagem", tipos_viagem)

df_filtrado = df.copy()

if motivo_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Motivo Agrupado"] == motivo_sel]

if renda_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Qual sua renda familiar mensal?"] == renda_sel]

if tipo_viagem_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["A sua última viagem intermunicipal (entre municípios) foi:"] == tipo_viagem_sel]

# ======================
# Exibir dados filtrados
# ======================
st.subheader("Tabela de Dados Filtrados")
st.dataframe(df_filtrado)

# Total de registros
st.markdown(f"""
<div style='font-size:24px; text-align:center; padding: 10px;'>
    Total de registros filtrados: <strong>{len(df_filtrado):,}</strong>
</div>
""", unsafe_allow_html=True)

# ======================
# Gráficos
# ======================

st.subheader("Distribuição dos Registros Filtrados")

col1, col2, col3 = st.columns(3)

with col1:
    fig_motivo = px.bar(df_filtrado["Motivo Agrupado"].value_counts().reset_index(),
                        x="index", y="Motivo Agrupado",
                        labels={"index": "Motivo da Viagem", "Motivo Agrupado": "Total"},
                        title="Motivo da Viagem")
    st.plotly_chart(fig_motivo, use_container_width=True)

with col2:
    fig_renda = px.bar(df_filtrado["Qual sua renda familiar mensal?"].value_counts().reset_index(),
                       x="index", y="Qual sua renda familiar mensal?",
                       labels={"index": "Renda Familiar", "Qual sua renda familiar mensal?": "Total"},
                       title="Renda Familiar")
    st.plotly_chart(fig_renda, use_container_width=True)

with col3:
    fig_tipo = px.bar(df_filtrado["A sua última viagem intermunicipal (entre municípios) foi:"].value_counts().reset_index(),
                      x="index", y="A sua última viagem intermunicipal (entre municípios) foi:",
                      labels={"index": "Tipo de Viagem", "A sua última viagem intermunicipal (entre municípios) foi:": "Total"},
                      title="Tipo de Viagem")
    st.plotly_chart(fig_tipo, use_container_width=True)

# ======================
# Rodapé
# ======================
st.markdown("""
<br><br>
<div style='text-align:center; font-size:20px;'>
    Fonte: Pesquisa OD RMGSL - Tabela agrupada.<br>
    Desenvolvido por <a href='https://www.linkedin.com/in/wagner-jales-663b4831/' target='_blank'>Wagner Jales</a>.
</div>
""", unsafe_allow_html=True)
