import streamlit as st
import pandas as pd
import folium
from folium import Marker
from streamlit_folium import st_folium
import plotly.express as px
import io
import math

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Mapa Origem-Destino - RMGSL PDDI (2025)")

@st.cache_data
def carregar_dados():
    df = pd.read_excel("PesquisaOD_2.xlsx", engine="openpyxl")
    df = df.rename(columns={
        "Qual o motivo da viagem?": "Motivo",
        "Com que frequência você faz essa viagem?": "Frequência",
        "A viagem foi realizada em qual período do dia?": "Periodo do dia",
        "Qual foi o principal meio de transporte que você usou?": "Principal Modal"
    })
    colunas_esperadas = ["ORIGEM", "DESTINO", "Motivo", "Frequência", "Periodo do dia", "Principal Modal"]
    faltando = [col for col in colunas_esperadas if col not in df.columns]
    if faltando:
        raise ValueError(f"Colunas faltando: {faltando}")
    return df

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar o Excel: {e}")
    st.stop()

municipios_coords = {
    "São Luís": [-2.538, -44.282],
    "Paço do Lumiar": [-2.510, -44.069],
    "Raposa": [-2.476, -44.096],
    "São José de Ribamar": [-2.545, -44.022],
    "Santa Rita": [-3.1457417436986854, -44.332941569634805],
    "Morros": [-2.864469, -44.039238],
    "Icatu": [-2.762, -44.045],
    "Rosário": [-2.943, -44.254],
    "Bacabeira": [-2.969, -44.310],
    "Itapecuru Mirim": [-3.338, -44.341],
    "Cantanhede": [-3.608, -44.370],
    "Codó": [-4.454, -43.874],
    "Timon": [-5.096, -42.837],
    "Caxias": [-4.861, -43.371],
    "São Mateus do Maranhão": [-3.840, -45.326],
    "Viana": [-3.232, -44.995],
    "Bequimão": [-2.438, -44.779],
    "Pinheiro": [-2.538, -45.082],
    "Anajatuba": [-3.291, -44.623],
    "Alcântara": [-2.416, -44.437],
    "Humberto de Campos": [-1.756, -44.793],
    "Barreirinhas": [-2.754, -42.825],
    "Primeira Cruz": [-2.508889158522334, -43.44017897332363],
    "Santo Amaro": [-2.5047542734648762, -43.255933552698686],
}

st.sidebar.header("Filtros")
origens = st.sidebar.multiselect("Origem:", sorted(df["ORIGEM"].dropna().unique()), default=[])
destinos = st.sidebar.multiselect("Destino:", sorted(df["DESTINO"].dropna().unique()), default=[])
motivo = st.sidebar.multiselect("Motivo da Viagem:", sorted(df["Motivo"].dropna().unique()), default=[])
frequencia = st.sidebar.multiselect("Frequência:", sorted(df["Frequência"].dropna().unique()), default=[])
periodo = st.sidebar.multiselect("Período do dia:", sorted(df["Periodo do dia"].dropna().unique()), default=[])
modal = st.sidebar.multiselect("Principal Modal:", sorted(df["Principal Modal"].dropna().unique()), default=[])

df_filtrado = df.copy()
if origens:
    df_filtrado = df_filtrado[df_filtrado["ORIGEM"].isin(origens)]
if destinos:
    df_filtrado = df_filtrado[df_filtrado["DESTINO"].isin(destinos)]
if motivo:
    df_filtrado = df_filtrado[df_filtrado["Motivo"].isin(motivo)]
if frequencia:
    df_filtrado = df_filtrado[df_filtrado["Frequência"].isin(frequencia)]
if periodo:
    df_filtrado = df_filtrado[df_filtrado["Periodo do dia"].isin(periodo)]
if modal:
    df_filtrado = df_filtrado[df_filtrado["Principal Modal"].isin(modal)]

# Remove deslocamentos onde origem = destino
df_od = df_filtrado[df_filtrado["ORIGEM"] != df_filtrado["DESTINO"]].copy()

# Cria um identificador de par ordenado (independente do sentido)
df_od["par_od"] = df_od.apply(lambda row: tuple(sorted([row["ORIGEM"], row["DESTINO"]])), axis=1)

# Agrupa e soma os deslocamentos nos dois sentidos
fluxos = df_od.groupby("par_od").size().reset_index(name="total")

# Mapa
mapa = folium.Map(location=[-2.53, -44.3], zoom_start=9)

for _, row in fluxos.iterrows():
    origem = row["par_od"][0]
    destino = row["par_od"][1]
    if origem in municipios_coords and destino in municipios_coords:
        coords = [municipios_coords[origem], municipios_coords[destino]]
        folium.PolyLine(
            coords,
            color="purple",
            weight=1 + (row["total"] / 30) * 5,
            opacity=0.8,
            tooltip=f"{origem} <-> {destino}: {row['total']} deslocamentos"
        ).add_to(mapa)
for cidade, coord in municipios_coords.items():
    folium.Marker(location=coord, popup=cidade, tooltip=cidade).add_to(mapa)

# Layout com mapa + gráfico da matriz OD
col1, col2 = st.columns([2, 1])
with col1:
    st_folium(mapa, width=1200, height=700)



col1, col2 = st.columns(2)
with col1:
    st.subheader("Motivo x Frequência")
    heatmap_a = df_filtrado.groupby(["Motivo", "Frequência"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_a, text_auto=True, color_continuous_scale="Blues"), use_container_width=True)
with col2:
    st.subheader("Motivo x Período do Dia")
    heatmap_b = df_filtrado.groupby(["Motivo", "Periodo do dia"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_b, text_auto=True, color_continuous_scale="Greens"), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Frequência x Período do Dia")
    heatmap_c = df_filtrado.groupby(["Frequência", "Periodo do dia"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_c, text_auto=True, color_continuous_scale="Oranges"), use_container_width=True)
with col4:
    st.subheader("Motivo x Modal (Principal Modal)")
    heatmap_e = df_filtrado.groupby(["Motivo", "Principal Modal"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_e, text_auto=True, color_continuous_scale="Teal"), use_container_width=True)

col5, col6 = st.columns(2)
with col5:
    st.subheader("Modal x Frequência")
    heatmap_f = df_filtrado.groupby(["Principal Modal", "Frequência"]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(heatmap_f, text_auto=True, color_continuous_scale="Pinkyl"), use_container_width=True)

# EXPORTAÇÃO
st.header("Exportar Matrizes")
def exportar_csv(df, nome_arquivo):
    buffer = io.BytesIO()
    df.to_csv(buffer, index=True)
    st.download_button(label=f"\U0001F4E5 Baixar {nome_arquivo}", data=buffer.getvalue(), file_name=f"{nome_arquivo}.csv", mime="text/csv")

exportar_csv(matriz, "Matriz_OD")
exportar_csv(heatmap_a, "Matriz_Motivo_x_Frequencia")
exportar_csv(heatmap_b, "Matriz_Motivo_x_Periodo")
exportar_csv(heatmap_c, "Matriz_Frequencia_x_Periodo")
exportar_csv(heatmap_e, "Matriz_Motivo_x_Modal")
exportar_csv(heatmap_f, "Matriz_Modal_x_Frequencia")

st.markdown("---")
st.markdown("Desenvolvido por [Wagner Jales](https://www.wagnerjales.com.br)")
