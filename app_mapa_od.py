
import streamlit as st
import pandas as pd
import folium
from folium import PolyLine, Marker
from streamlit_folium import st_folium
import plotly.express as px

st.set_page_config(layout="wide")  # ✅ PRIMEIRA CHAMADA STREAMLIT

# 🔽 Remover o espaço acima do título
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Mapa Origem-Destino - RMGSL")

# Carregar os dados
df = pd.read_csv("dados_filtrados.csv")

# Coordenadas aproximadas dos municípios (incluindo Rosário)
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
    "FORA DA RMGSL": [-3.0, -44.5]
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

# Mapa
mapa = folium.Map(location=[-2.53, -44.3], zoom_start=11)

for _, row in df_agrupado.iterrows():
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

# Layout com mapa + gráfico da matriz OD
col1, col2 = st.columns([2, 1])
with col1:
    st_folium(mapa, width=1200, height=700)

with col2:
    st.subheader("Matriz OD (Gráfico Térmico)")
    matriz = df_filtrado.groupby(["ORIGEM 2", "DESTINO 2"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(matriz, text_auto=True, color_continuous_scale="Purples", title="Matriz OD"), use_container_width=True)
