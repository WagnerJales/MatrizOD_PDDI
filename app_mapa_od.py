import streamlit as st
import pandas as pd
import folium
from folium import PolyLine, Marker
from streamlit_folium import st_folium

# Título
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

# Filtros
col1, col2 = st.columns(2)
with col1:
    motivo = st.selectbox("Motivo da Viagem:", ["Todos"] + sorted(df["motivo_ajustado"].dropna().unique().tolist()))
with col2:
    frequencia = st.selectbox("Frequência:", ["Todas"] + sorted(df["Com que frequência você faz essa viagem?"].dropna().unique().tolist()))

# Aplicar filtros
df_filtrado = df.copy()
if motivo != "Todos":
    df_filtrado = df_filtrado[df_filtrado["motivo_ajustado"] == motivo]
if frequencia != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Com que frequência você faz essa viagem?"] == frequencia]

# Agrupar os dados
df_agrupado = df_filtrado.groupby(["ORIGEM 2", "DESTINO 2"]).size().reset_index(name="total")

# Criar mapa
mapa = folium.Map(location=[-2.53, -44.3], zoom_start=9)

# Desenhar linhas
for _, row in df_agrupado.iterrows():
    origem = row["ORIGEM 2"]
    destino = row["DESTINO 2"]
    if origem in municipios_coords and destino in municipios_coords:
        coords = [municipios_coords[origem], municipios_coords[destino]]
        folium.PolyLine(
            coords,
            color="purple",
            weight=1 + (row["total"] / 30) * 5,
            opacity=0.8,
            tooltip=f"{origem} → {destino}: {row['total']} deslocamentos"
        ).add_to(mapa)

# Marcadores
for cidade, coord in municipios_coords.items():
    folium.Marker(location=coord, popup=cidade, tooltip=cidade).add_to(mapa)

# Mostrar no Streamlit
st_folium(mapa, width=800, height=600)
