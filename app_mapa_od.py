import streamlit as st
import pandas as pd
import folium
from folium import Marker, PolyLine
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

# === Filtros ===
st.sidebar.header("Filtros")
origens = st.sidebar.multiselect("Origem:", sorted(df["ORIGEM"].dropna().unique()), default=[])
destinos = st.sidebar.multiselect("Destino:", sorted(df["DESTINO"].dropna().unique()), default=[])
motivo = st.sidebar.multiselect("Motivo da Viagem:", sorted(df["Motivo"].dropna().unique()), default=[])
frequencia = st.sidebar.multiselect("Frequência:", sorted(df["Frequência"].dropna().unique()), default=[])
periodo = st.sidebar.multiselect("Período do dia:", sorted(df["Periodo do dia"].dropna().unique()), default=[])
modal = st.sidebar.multiselect("Principal Modal:", sorted(df["Principal Modal"].dropna().unique()), default=[])

sentido_selecionado = st.sidebar.selectbox("Sentido do deslocamento:", [
    "A-B (Origem-Destino)",
    "B-A (Destino-Origem)",
    "A-B e B-A (Bidirecional)"
])

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

df_od = df_filtrado[df_filtrado["ORIGEM"] != df_filtrado["DESTINO"]].copy()

# Agrupamento conforme sentido
if sentido_selecionado == "A-B (Origem-Destino)":
    df_od["ORIGEM_DESTINO"] = list(zip(df_od["ORIGEM"], df_od["DESTINO"]))
elif sentido_selecionado == "B-A (Destino-Origem)":
    df_od["ORIGEM_DESTINO"] = list(zip(df_od["DESTINO"], df_od["ORIGEM"]))
else:  # Bidirecional (sem sentido)
    df_od["ORIGEM_DESTINO"] = df_od.apply(lambda row: tuple(sorted([row["ORIGEM"], row["DESTINO"]])), axis=1)

# Agrupa os fluxos
fluxos = df_od.groupby("ORIGEM_DESTINO").size().reset_index(name="total")
fluxos[["ORIGEM", "DESTINO"]] = pd.DataFrame(fluxos["ORIGEM_DESTINO"].tolist(), index=fluxos.index)

# Criação da matriz OD
matriz = fluxos.pivot_table(index="ORIGEM", columns="DESTINO", values="total", fill_value=0)

# === Mapa OD ===
mapa = folium.Map(location=[-2.53, -44.3], zoom_start=9)

for _, row in fluxos.iterrows():
    origem, destino = row["ORIGEM"], row["DESTINO"]
    if origem in municipios_coords and destino in municipios_coords:
        coords = [municipios_coords[origem], municipios_coords[destino]]
        tooltip_text = f"{origem} → {destino}: {row['total']} deslocamentos"
        folium.PolyLine(
            coords,
            color="purple",
            weight=1 + (row["total"] / 30) * 5,
            opacity=0.8,
            tooltip=tooltip_text
        ).add_to(mapa)

# Apenas marcadores relevantes
municipios_presentes = set(df_filtrado["ORIGEM"]).union(set(df_filtrado["DESTINO"]))
for cidade in municipios_presentes:
    if cidade in municipios_coords:
        folium.Marker(location=municipios_coords[cidade], popup=cidade, tooltip=cidade).add_to(mapa)

col1, col2 = st.columns([2, 1])
with col1:
    st_folium(mapa, width=1200, height=700)

# === Heatmaps ===
def gerar_heatmap(df, eixo_x, eixo_y, titulo, cor="Blues"):
    st.subheader(titulo)
    matriz = df.groupby([eixo_x, eixo_y]).size().unstack(fill_value=0)
    st.plotly_chart(px.imshow(matriz, text_auto=True, color_continuous_scale=cor), use_container_width=True)
    return matriz

col1, col2 = st.columns(2)
with col1:
    heatmap_a = gerar_heatmap(df_filtrado, "Motivo", "Frequência", "Motivo x Frequência", "Blues")
with col2:
    heatmap_b = gerar_heatmap(df_filtrado, "Motivo", "Periodo do dia", "Motivo x Período do Dia", "Greens")

col3, col4 = st.columns(2)
with col3:
    heatmap_c = gerar_heatmap(df_filtrado, "Frequência", "Periodo do dia", "Frequência x Período do Dia", "Oranges")
with col4:
    heatmap_e = gerar_heatmap(df_filtrado, "Motivo", "Principal Modal", "Motivo x Modal", "Teal")

col5, col6 = st.columns(2)
with col5:
    heatmap_f = gerar_heatmap(df_filtrado, "Principal Modal", "Frequência", "Modal x Frequência", "Magenta")

# === Exportação ===
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
