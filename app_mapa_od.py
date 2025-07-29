import streamlit as st
import pandas as pd
import folium
from folium import PolyLine, Marker
from streamlit_folium import st_folium
import plotly.express as px
import io

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
    "Alcântara": [-2.416, -44.437],
    "Anajatuba": [-3.291, -44.623],
    "Anapurus": [-3.668, -43.108],
    "Araguanã": [-2.948, -45.660],
    "Arari": [-3.448, -44.770],
    "Axixá": [-2.841, -44.054],
    "Bacabal": [-4.214, -44.783],
    "Bacabeira": [-2.969, -44.310],
    "Bacuri": [-1.701, -45.152],
    "Barreirinhas": [-2.754, -42.825],
    "Bequimão": [-2.438, -44.779],
    "Brejo": [-3.600, -43.010],
    "Buriti": [-3.547, -44.172],
    "Cachoeira Grande": [-2.932, -44.056],
    "Cafeteira": [-2.506, -44.178],
    "Cajari": [-5.464, -44.526],
    "Cantanhede": [-3.608, -44.370],
    "Caxias": [-4.861, -43.371],
    "Codó": [-4.454, -43.874],
    "Coelho Neto": [-3.453, -43.983],
    "Coroatá": [-3.308, -44.127],
    "Guimarães": [-5.793, -44.796],
    "Humberto de Campos": [-1.756, -44.793],
    "Icatu": [-2.762, -44.045],
    "Iguaíba": [-2.587, -44.099],
    "Imperatriz": [-5.518, -47.459],
    "Itapecuru Mirim": [-3.338, -44.341],
    "Lago da Pedra": [-4.002, -45.259],
    "Matinha": [-1.924, -45.167],
    "Miranda do Norte": [-4.021, -44.773],
    "Morros": [-2.864469, -44.039238],
    "Olinda Nova do Maranhão": [-3.036, -45.257],
    "Paço do Lumiar": [-2.510, -44.069],
    "Pedreiras": [-4.244, -44.574],
    "Pedro do Rosário": [-2.946, -44.927],
    "Penalva": [-4.111, -45.145],
    "Peritoró": [-4.246, -44.882],
    "Pinheiro": [-2.538, -45.082],
    "Presidente Dutra": [-5.237, -44.372],
    "Presidente Juscelino": [-3.488, -44.652],
    "Primeira Cruz": [-2.508889158522334, -43.44017897332363],
    "Raposa": [-2.476, -44.096],
    "Ribamar Fiquene": [-5.491, -46.355],
    "Rosário": [-2.943, -44.254],
    "Santa Inês": [-4.104, -45.278],
    "Santa Rita": [-3.1457417436986854, -44.332941569634805],
    "Santo Amaro": [-3.992, -45.356],
    "São Bento": [-5.425, -44.349],
    "São Domingos do Maranhão": [-3.867, -43.371],
    "São Domingos do Azeitão": [-5.709, -47.639],
    "São José de Ribamar": [-2.545, -44.022],
    "São Luís": [-2.538, -44.282],
    "São Mateus do Maranhão": [-3.840, -45.326],
    "São Pedro dos Crentes": [-7.308, -46.682],
    "São Raimundo das Mangabeiras": [-6.762, -45.366],
    "São Vicente Ferrer": [-2.893, -44.872],
    "Satubinha": [-5.502, -45.389],
    "Timon": [-5.096, -42.837],
    "Tuntum": [-4.116, -44.722],
    "Viana": [-3.232, -44.995],
    "Vitória do Mearim": [-3.512, -44.942]
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

df_agrupado = df_filtrado.groupby(["ORIGEM", "DESTINO"]).size().reset_index(name="total")
mapa = folium.Map(location=[-2.53, -43.9], zoom_start=10, tiles="CartoDB positron")
for _, row in df_agrupado.sort_values("total", ascending=False).head(100).iterrows():
    origem = row["ORIGEM"]
    destino = row["DESTINO"]
    if origem in municipios_coords and destino in municipios_coords:
        coords = [municipios_coords[origem], municipios_coords[destino]]
        folium.PolyLine(coords, color="red", weight=1 + (row["total"] / 30) * 5,
                        opacity=0.8, tooltip=f"{origem} → {destino}: {row['total']} deslocamentos").add_to(mapa)
for cidade, coord in municipios_coords.items():
    folium.Marker(location=coord, popup=cidade, tooltip=cidade, icon=folium.Icon(icon="circle")).add_to(mapa)

st_folium(mapa, width=1600, height=700)

st.subheader("Matriz OD (Gráfico Térmico)")
matriz = df_filtrado.groupby(["ORIGEM", "DESTINO"]).size().unstack(fill_value=0)
altura = 50 * len(matriz)
fig = px.imshow(matriz, text_auto=True, color_continuous_scale="Purples", height=altura)
st.plotly_chart(fig, use_container_width=True)

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
