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

# Lista de municípios da RMGSL
municipios_rmgsl = [
    "São Luís",
    "Paço do Lumiar",
    "Raposa",
    "São José de Ribamar",
    "Santa Rita",
    "Morros",
    "Icatu",
    "Rosário",
    "Bacabeira",
    "Cachoeira Grande",
    "Presidente Juscelino",
    "Alcântara"
]

coords_municipios_od2 = {
    # Subzonas de São Luís
    "São Luís - Bancaga": [-2.557948, -44.331238],
    "São Luís - Centro": [-2.515687, -44.296435],
    "São Luís - Cidade Operária": [-2.5705480438203296, -44.20412618522021],
    "São Luís - Cohab": [-2.541977, -44.212127],
    "São Luís - Cohama": [-2.5163246962493697, -44.24714652403556],
    "São Luís - Zona Industrial": [-2.614860861647258, -44.25655944286809],

    # Demais municípios
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
    "Cachoeira Grande": [-2.917, -44.223],
    "Presidente Juscelino": [-2.918, -44.068]
}


# === Filtros ===
st.sidebar.header("Filtros")
origens = st.sidebar.multiselect("Origem:", sorted(df["ORIGEM"].dropna().unique()), default=[])
destinos = st.sidebar.multiselect("Destino:", sorted(df["DESTINO"].dropna().unique()), default=[])
motivo = st.sidebar.multiselect("Motivo da Viagem:", sorted(df["Motivo"].dropna().unique()), default=[])
frequencia = st.sidebar.multiselect("Frequência:", sorted(df["Frequência"].dropna().unique()), default=[])
periodo = st.sidebar.multiselect("Período do dia:", sorted(df["Periodo do dia"].dropna().unique()), default=[])
modal = st.sidebar.multiselect("Principal Modal:", sorted(df["Principal Modal"].dropna().unique()), default=[])

# Filtros adicionais
filtro_origem_rmgsl = st.sidebar.checkbox("Apenas origens na RMGSL")
filtro_destino_rmgsl = st.sidebar.checkbox("Apenas destinos na RMGSL")

# === Aplicar filtros ===
df_filtrado = df.copy()
if filtro_origem_rmgsl:
    df_filtrado = df_filtrado[df_filtrado["ORIGEM"].isin(municipios_rmgsl)]
if filtro_destino_rmgsl:
    df_filtrado = df_filtrado[df_filtrado["DESTINO"].isin(municipios_rmgsl)]
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

# Mostrar quantidade de registros após filtragem
st.sidebar.markdown("---")
st.sidebar.markdown("**Total de pesquisas filtradas:**", unsafe_allow_html=True)
st.sidebar.markdown(
    f"<span style='font-size: 32px; font-weight: bold; color: #4B8BBE;'>{len(df_filtrado):,}</span>",
    unsafe_allow_html=True
)

# === Eliminar auto-deslocamentos ===
df_od = df_filtrado[df_filtrado["ORIGEM"] != df_filtrado["DESTINO"]].copy()

# === Agrupar deslocamentos bidirecionais ===
df_od["par_od"] = df_od.apply(lambda row: tuple(sorted([row["ORIGEM"], row["DESTINO"]])), axis=1)
fluxos = df_od.groupby("par_od").size().reset_index(name="total")
fluxos[["ORIGEM", "DESTINO"]] = pd.DataFrame(fluxos["par_od"].tolist(), index=fluxos.index)

# === Matriz OD ===
matriz = fluxos.pivot_table(index="ORIGEM", columns="DESTINO", values="total", fill_value=0)

# === Mapa interativo ===
mapa = folium.Map(location=[-2.53, -44.3], zoom_start=9, tiles="CartoDB Positron")
for _, row in fluxos.iterrows():
    origem, destino = row["ORIGEM"], row["DESTINO"]
    if origem in municipios_coords and destino in municipios_coords and municipios_coords[origem] and municipios_coords[destino]:
        coords = [municipios_coords[origem], municipios_coords[destino]]
        folium.PolyLine(
            coords,
            color="red",
            weight=1 + (row["total"] / 30) * 5,
            opacity=0.8,
            tooltip=f"{origem} ↔ {destino}: {row['total']} deslocamentos"
        ).add_to(mapa)

# Marcadores apenas para municípios usados
municipios_usados = set(df_od["ORIGEM"]).union(set(df_od["DESTINO"]))
for cidade in municipios_usados:
    if cidade in municipios_coords and municipios_coords[cidade]:
        folium.Marker(location=municipios_coords[cidade], popup=cidade, tooltip=cidade).add_to(mapa)

with st.container():
    st_folium(mapa, width=1600, height=600)

# Mapa 2 - sbuáreas Sao Luis
st.markdown("---")
st.subheader("🌐 Mapa OD com colunas específicas de origem/destino (incluindo subzonas de São Luís)")

if "Qual o município de ORIGEM" in df.columns and "Qual o município de DESTINO" in df.columns:

    df_od2 = df[
        df["Qual o município de ORIGEM"].isin(coords_municipios_od2.keys()) &
        df["Qual o município de DESTINO"].isin(coords_municipios_od2.keys())
    ].copy()

    df_od2 = df_od2[df_od2["Qual o município de ORIGEM"] != df_od2["Qual o município de DESTINO"]]
    df_od2["par_od"] = df_od2.apply(lambda row: tuple(sorted([row["Qual o município de ORIGEM"], row["Qual o município de DESTINO"]])), axis=1)

    fluxo_od2 = df_od2.groupby("par_od").size().reset_index(name="total")
    fluxo_od2[["ORIGEM", "DESTINO"]] = pd.DataFrame(fluxo_od2["par_od"].tolist(), index=fluxo_od2.index)

    mapa_od2 = folium.Map(location=[-2.53, -44.3], zoom_start=10, tiles="CartoDB Positron")

    for _, row in fluxo_od2.iterrows():
        origem, destino = row["ORIGEM"], row["DESTINO"]
        if origem in coords_municipios_od2 and destino in coords_municipios_od2:
            coords = [coords_municipios_od2[origem], coords_municipios_od2[destino]]
            folium.PolyLine(
                coords,
                color="darkblue",
                weight=1 + (row["total"] / 20) * 4,
                opacity=0.7,
                tooltip=f"{origem} ↔ {destino}: {row['total']} deslocamentos"
            ).add_to(mapa_od2)

    for nome, coord in coords_municipios_od2.items():
        folium.Marker(location=coord, tooltip=nome).add_to(mapa_od2)

    st_folium(mapa_od2, use_container_width=True, height=550)

else:
    st.warning("As colunas 'Qual o município de ORIGEM' e 'Qual o município de DESTINO' não foram encontradas na base.")



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

# === Exportação de matrizes ===
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

# === SHAPEFILE para QGIS ===
st.header("Exportar Shapefile para QGIS")
def gerar_shapefile_zip(fluxos, coords_dict, nome_arquivo="fluxo_od"):
linhas = []
for _, row in fluxos.iterrows():
origem, destino = row["ORIGEM"], row["DESTINO"]
if origem in coords_dict and destino in coords_dict:
coord_origem = coords_dict[origem]
coord_destino = coords_dict[destino]
if coord_origem and coord_destino:
linha = LineString([
tuple(reversed(coord_origem)),
tuple(reversed(coord_destino))
])
linhas.append({
"ORIGEM": origem,
"DESTINO": destino,
"TOTAL": row["total"],
"geometry": linha
})


gdf = gpd.GeoDataFrame(linhas, crs="EPSG:4326")
pasta = f"{nome_arquivo}_shp"
os.makedirs(pasta, exist_ok=True)
caminho_shp = os.path.join(pasta, f"{nome_arquivo}.shp")
gdf.to_file(caminho_shp)


zip_path = f"{nome_arquivo}.zip"
with zipfile.ZipFile(zip_path, 'w') as zipf:
for file in os.listdir(pasta):
zipf.write(os.path.join(pasta, file), arcname=file)


return zip_path


# Verifica se variáveis necessárias existem antes de exportar
if 'fluxos' in locals() and 'municipios_coords' in locals():
arquivo_zip = gerar_shapefile_zip(fluxos, municipios_coords)
with open(arquivo_zip, "rb") as f:
st.download_button(
label="\U0001F4E5 Baixar Shapefile de Fluxos OD",
data=f.read(),
file_name="fluxo_od.zip",
mime="application/zip"
)
else:
st.warning("As variáveis de fluxo ou coordenadas não estão disponíveis para exportar o shapefile.")
