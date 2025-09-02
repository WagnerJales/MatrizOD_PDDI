
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

def carregar_dados():
    try:
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
    except Exception as erro:
        st.error(f"Erro ao carregar dados: {erro}")
        return pd.DataFrame()

df = carregar_dados()
st.write("Pré-visualização dos dados:", df.head())



# Coordenadas dos municípios
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
    "Cachoeira Grande": None,
    "Presidente Juscelino": None
}

st.success("Parte lógica do sistema será reintroduzida aqui...")




# ========== PRÉ-VISUALIZAÇÃO ==========
st.subheader("Pré-visualização dos dados:")
st.dataframe(df.head())

# ========== FILTROS ==========
st.sidebar.header("Filtros")
origens = st.sidebar.multiselect("Origem:", sorted(df["Qual o município de ORIGEM"].dropna().unique()), default=[])
destinos = st.sidebar.multiselect("Destino:", sorted(df["Qual o município de DESTINO"].dropna().unique()), default=[])
motivo = st.sidebar.multiselect("Motivo da Viagem:", sorted(df["Motivo"].dropna().unique()), default=[])
frequencia = st.sidebar.multiselect("Frequência:", sorted(df["Frequência"].dropna().unique()), default=[])
periodo = st.sidebar.multiselect("Período do dia:", sorted(df["Periodo do dia"].dropna().unique()), default=[])

# ========== APLICAR FILTROS ==========
df_filtrado = df.copy()
if origens:
    df_filtrado = df_filtrado[df_filtrado["Qual o município de ORIGEM"].isin(origens)]
if destinos:
    df_filtrado = df_filtrado[df_filtrado["Qual o município de DESTINO"].isin(destinos)]
if motivo:
    df_filtrado = df_filtrado[df_filtrado["Motivo"].isin(motivo)]
if frequencia:
    df_filtrado = df_filtrado[df_filtrado["Frequência"].isin(frequencia)]
if periodo:
    df_filtrado = df_filtrado[df_filtrado["Periodo do dia"].isin(periodo)]

# Mostrar total filtrado
st.sidebar.markdown("**Total de registros filtrados:**")
st.sidebar.metric(label="Pesquisas", value=len(df_filtrado))

# ========== FILTRAR DIFERENTES ORIGEM/DESTINO ==========
df_od = df_filtrado[df_filtrado["Qual o município de ORIGEM"] != df_filtrado["Qual o município de DESTINO"]].copy()
df_od["par_od"] = df_od.apply(lambda row: tuple(sorted([row["Qual o município de ORIGEM"], row["Qual o município de DESTINO"]])), axis=1)
fluxos = df_od.groupby("par_od").size().reset_index(name="total")
fluxos[["ORIGEM", "DESTINO"]] = pd.DataFrame(fluxos["par_od"].tolist(), index=fluxos.index)

# ========== MAPA ==========
mapa = folium.Map(location=[-2.53, -44.3], zoom_start=9, tiles="CartoDB Positron")
for _, row in fluxos.iterrows():
    origem, destino = row["ORIGEM"], row["DESTINO"]
    if origem in municipios_coords and destino in municipios_coords:
        coord_o = municipios_coords.get(origem)
        coord_d = municipios_coords.get(destino)
        if coord_o and coord_d:
            folium.PolyLine(
                [coord_o, coord_d],
                color="red",
                weight=1 + (row["total"] / 30) * 5,
                opacity=0.8,
                tooltip=f"{origem} ↔ {destino}: {row['total']}"
            ).add_to(mapa)

# Marcadores
usados = set(df_od["Qual o município de ORIGEM"]).union(set(df_od["Qual o município de DESTINO"]))
for cidade in usados:
    if cidade in municipios_coords and municipios_coords[cidade]:
        folium.Marker(location=municipios_coords[cidade], popup=cidade, tooltip=cidade).add_to(mapa)

st.markdown("### Mapa Interativo - Fluxos OD")
st_folium(mapa, width=1400, height=600)

# ========== HEATMAPS ==========
def gerar_heatmap(df, eixo_x, eixo_y, titulo, cor="Blues"):
    st.subheader(titulo)
    matriz = df.groupby([eixo_x, eixo_y]).size().unstack(fill_value=0)
    fig = px.imshow(matriz, text_auto=True, color_continuous_scale=cor)
    st.plotly_chart(fig, use_container_width=True)
    return matriz

col1, col2 = st.columns(2)
with col1:
    heatmap_a = gerar_heatmap(df_filtrado, "Motivo", "Frequência", "Motivo x Frequência", "Blues")
with col2:
    heatmap_b = gerar_heatmap(df_filtrado, "Motivo", "Periodo do dia", "Motivo x Período do Dia", "Greens")

# ========== EXPORTAÇÃO ==========
st.header("Exportar Matrizes como CSV")
def exportar_csv(df, nome_arquivo):
    buffer = io.BytesIO()
    df.to_csv(buffer, index=True)
    st.download_button(label=f"Baixar {nome_arquivo}", data=buffer.getvalue(), file_name=f"{nome_arquivo}.csv", mime="text/csv")

exportar_csv(heatmap_a, "Matriz_Motivo_x_Frequencia")
exportar_csv(heatmap_b, "Matriz_Motivo_x_Periodo")



# === Mapa com subzonas de São Luís ===
coords_municipios_od2 = {
    "São Luís - Bancaga": [-2.557948, -44.331238],
    "São Luís - Centro": [-2.515687, -44.296435],
    "São Luís - Cidade Operária": [-2.5705480438203296, -44.20412618522021],
    "São Luís - Cohab": [-2.541977, -44.212127],
    "São Luís - Cohama": [-2.5163246962493697, -44.24714652403556],
    "São Luís - Zona Industrial": [-2.614860861647258, -44.25655944286809],
    "Paço do Lumiar": [-2.510, -44.069],
    "Raposa": [-2.476, -44.096],
    "São José de Ribamar": [-2.545, -44.022],
    "Alcântara": [-2.416, -44.437]
}

st.subheader("🌐 Mapa OD com subzonas de São Luís")

if "Qual o município de ORIGEM" in df.columns and "Qual o município de DESTINO" in df.columns:
    df_od2 = df_filtrado[
        df_filtrado["Qual o município de ORIGEM"].isin(coords_municipios_od2.keys()) &
        df_filtrado["Qual o município de DESTINO"].isin(coords_municipios_od2.keys())
    ].copy()

    df_od2 = df_od2[df_od2["Qual o município de ORIGEM"] != df_od2["Qual o município de DESTINO"]]
    df_od2["par_od"] = df_od2.apply(lambda row: tuple(sorted([row["Qual o município de ORIGEM"], row["Qual o município de DESTINO"]])), axis=1)

    fluxo_od2 = df_od2.groupby("par_od").size().reset_index(name="total")
    fluxo_od2[["ORIGEM", "DESTINO"]] = pd.DataFrame(fluxo_od2["par_od"].tolist(), index=fluxo_od2.index)

    mapa_od2 = folium.Map(location=[-2.53, -44.3], zoom_start=11, tiles="CartoDB Positron")

    for _, row in fluxo_od2.iterrows():
        origem, destino = row["ORIGEM"], row["DESTINO"]
        if origem in coords_municipios_od2 and destino in coords_municipios_od2:
            coords = [coords_municipios_od2[origem], coords_municipios_od2[destino]]
            folium.PolyLine(
                coords,
                color="purple",
                weight=1 + (row["total"] / 15),
                opacity=0.6,
                tooltip=f"{origem} ↔ {destino}: {row['total']} deslocamentos"
            ).add_to(mapa_od2)

    for nome, coord in coords_municipios_od2.items():
        folium.Marker(location=coord, tooltip=nome).add_to(mapa_od2)

    st_folium(mapa_od2, use_container_width=True, height=550)
else:
    st.warning("As colunas de subzonas 'Qual o município de ORIGEM' e 'Qual o município de DESTINO' não foram encontradas.")
