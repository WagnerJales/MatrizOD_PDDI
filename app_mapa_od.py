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
   "Alcântara": [-2.41, -44.42],
    "Anajatuba": [-3.263, -44.613],
    "Anapurus": [-3.676, -43.102],
    "Araguanã": [-2.947, -45.659],
    "Arari": [-3.453, -44.766],
    "Axixá": [-2.839, -44.053],
    "Bacabal": [-4.224, -44.783],
    "Bacabeira": [-2.965, -44.316],
    "Bacuri": [-1.706, -45.144],
    "Barreirinhas": [-5.704, -46.924],
    "Bequimão": [-2.445, -44.784],
    "Brejo": [-3.588, -43.007],
    "Buriti": [-3.827, -42.918],
    "Cachoeira Grande": [-2.931, -44.053],
    "Cafeteira": [-2.52, -44.188],
    "Cajari": [-5.451, -44.524],
    "Cantanhede": [-3.637, -44.382],
    "Caxias": [-4.865, -43.363],
    "Codó": [-4.265, -46.01],
    "Coelho Neto": [-3.446, -44.094],
    "Coroatá": [-2.735, -43.032],
    "Guimarães": [-5.792, -44.803],
    "Humberto de Campos": [-5.02, -44.308],
    "Icatu": [-4.973, -44.365],
    "Iguaiba": [-2.588, -44.099],
    "Imperatriz": [-5.526, -47.491],
    "Itapecuru Mirim": [-3.402, -44.351],
    "Lago da Pedra": [-2.794, -45.067],
    "Matinha": [-2.488, -46.338],
    "Miranda do Norte": [-5.042, -44.342],
    "Morros": [-3.493, -45.822],
    "Olinda Nova do Maranhão": [-2.992, -44.989],
    "Paço do Lumiar": [-2.516, -44.101],
    "Pedreiras": [-4.21, -43.642],
    "Pedro do Rosário": [-2.971, -45.35],
    "Penalva": [-4.31, -45.15],
    "Peritoró": [-4.957, -45.568],
    "Pinheiro": [-5.778, -44.501],
    "Presidente Dutra": [-3.659, -47.716],
    "Presidente Juscelino": [-3.789, -45.746],
    "Primeira Cruz": [-4.773, -47.264],
    "Raposa": [-5.184, -43.246],
    "Ribeira": [-3.759, -45.454],
    "Rosário": [-2.934, -44.254],
    "Santa Inês": [-3.653, -45.377],
    "Santa Rita": [-3.139, -44.325],
    "Santo Amaro": [-4.622, -47.781],
    "São Bento": [-2.698, -44.824],
    "São Domingos": [-4.192, -44.526],
    "São Domingos do Azeitão": [-6.814, -44.65],
    "São José de Ribamar": [-2.561, -44.054],
    "São Luís": [-2.531, -44.307],
    "São Mateus do Maranhão": [-4.039, -44.471],
    "São Pedro dos Crentes": [-6.823, -46.531],
    "São Raimundo das Mangabeiras": [-7.021, -45.481],
    "São Vicente Ferrer": [-2.895, -44.88],
    "Satubinha": [-4.878, -44.828],
    "Timon": [-5.096, -42.837],
    "Tuntum": [-4.656, -44.625],
    "Viana": [-3.202, -44.991],
    "Vitória do Mearim": [-3.451, -44.869]
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
