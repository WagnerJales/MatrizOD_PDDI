
import streamlit as st
import pandas as pd
import folium
from folium import PolyLine, Marker
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Mapa Origem-Destino - RMGSL")

@st.cache_data
def carregar_dados():
    return pd.read_csv("dados_filtrados.csv")

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar o CSV: {e}")
    st.stop()

municipios_coords = {
    "São Luís": [-2.53, -44.3],
    "São José de Ribamar": [-2.56, -44.05],
    "Paço do Lumiar": [-2.52, -44.1],
    "Raposa": [-2.43, -44.1],
    "Rosário": [-2.9344, -44.2511],
    "Alcântara": [-2.41, -44.41],
    "Icatu": [-2.77, -44.05],
    "Morros": [-2.86, -44.04],
    "Bacabeira": [-2.96, -44.31],
    "AXIXÁ": [-3.48, -44.06],
    "FORA DA RMGSL": [-2.9533, -44.7966]
}

st.sidebar.header("Filtros")
origens = st.sidebar.multiselect("Origem:", sorted(df["ORIGEM 2"].dropna().unique()), default=[])
destinos = st.sidebar.multiselect("Destino:", sorted(df["DESTINO 2"].dropna().unique()), default=[])
motivo = st.sidebar.multiselect("Motivo da Viagem:", sorted(df["motivo_ajustado"].dropna().unique()), default=[])
frequencia = st.sidebar.multiselect("Frequência:", sorted(df["Com que frequência você faz essa viagem?"].dropna().unique()), default=[])
periodo = st.sidebar.multiselect("Período do dia:", sorted(df["A viagem foi realizada em qual período do dia?"].dropna().unique()), default=[])

# Aplicar filtros
df_filtrado = df.copy()
if origens:
    df_filtrado = df_filtrado[df_filtrado["ORIGEM 2"].isin(origens)]
if destinos:
    df_filtrado = df_filtrado[df_filtrado["DESTINO 2"].isin(destinos)]
if motivo:
    df_filtrado = df_filtrado[df_filtrado["motivo_ajustado"].isin(motivo)]
if frequencia:
    df_filtrado = df_filtrado[df_filtrado["Com que frequência você faz essa viagem?"].isin(frequencia)]
if periodo:
    df_filtrado = df_filtrado[df_filtrado["A viagem foi realizada em qual período do dia?"].isin(periodo)]

# Agrupar OD
df_agrupado = df_filtrado.groupby(["ORIGEM 2", "DESTINO 2"]).size().reset_index(name="total")

# Criar mapa
mapa = folium.Map(location=[-2.53, -44.3], zoom_start=10)

for _, row in df_agrupado.sort_values("total", ascending=False).head(100).iterrows():
    origem = row["ORIGEM 2"]
    destino = row["DESTINO 2"]
    if origem in municipios_coords and destino in municipios_coords:
        coords = [municipios_coords[origem], municipios_coords[destino]]
        folium.PolyLine(
            coords,
            color="red",
            weight=1 + (row["total"] / 30) * 5,
            opacity=0.8,
            tooltip=f"{origem} → {destino}: {row['total']} deslocamentos"
        ).add_to(mapa)

for cidade, coord in municipios_coords.items():
    folium.Marker(location=coord, popup=cidade, tooltip=cidade).add_to(mapa)

# Mostrar mapa
st.subheader("Mapa OD")
st_folium(mapa, width=1600, height=700)

# -------------------------
# Heatmap 1: Matriz OD
st.subheader("Matriz OD (Gráfico Térmico)")
matriz = df_filtrado.groupby(["ORIGEM 2", "DESTINO 2"]).size().unstack(fill_value=0)
st.plotly_chart(px.imshow(matriz, text_auto=True, color_continuous_scale="Purples", title="Matriz OD"), use_container_width=True)

# -------------------------
# Heatmaps adicionais em pares

# Motivo x Frequência
col3, col4 = st.columns(2)
with col3:
    st.subheader("Motivo x Frequência")
    heatmap_a = df_filtrado.groupby(["motivo_ajustado", "Com que frequência você faz essa viagem?"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_a, text_auto=True, color_continuous_scale="Blues", title="Motivo x Frequência"), use_container_width=True)

# Motivo x Período do Dia
with col4:
    st.subheader("Motivo x Período do Dia")
    heatmap_b = df_filtrado.groupby(["motivo_ajustado", "A viagem foi realizada em qual período do dia?"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_b, text_auto=True, color_continuous_scale="Greens", title="Motivo x Período do Dia"), use_container_width=True)

# Frequência x Período do Dia
col5, col6 = st.columns(2)
with col5:
    st.subheader("Frequência x Período do Dia")
    heatmap_c = df_filtrado.groupby(["Com que frequência você faz essa viagem?", "A viagem foi realizada em qual período do dia?"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_c, text_auto=True, color_continuous_scale="Oranges", title="Frequência x Período do Dia"), use_container_width=True)
