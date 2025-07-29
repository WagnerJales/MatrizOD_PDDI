import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.set_page_config(layout="wide")

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel("PesquisaOD_2.xlsx", sheet_name="RESPOSTAS")
    coords = pd.read_csv("coordenadas_municipios.csv")
    return df, coords

df, coords = load_data()

# Criar coluna de contagem
df["volume"] = 1

# Filtrar e renomear
df_od = df[["ORIGEM", "DESTINO", "volume"]].groupby(["ORIGEM", "DESTINO"]).count().reset_index()

# Adicionar coordenadas de origem e destino
coords_dict = coords.set_index("local")[["latitude", "longitude"]].to_dict("index")

def get_coords(local, tipo):
    if local in coords_dict:
        return coords_dict[local]["latitude"] if tipo == "lat" else coords_dict[local]["longitude"]
    return None

df_od["orig_lat"] = df_od["ORIGEM"].apply(lambda x: get_coords(x, "lat"))
df_od["orig_lon"] = df_od["ORIGEM"].apply(lambda x: get_coords(x, "lon"))
df_od["dest_lat"] = df_od["DESTINO"].apply(lambda x: get_coords(x, "lat"))
df_od["dest_lon"] = df_od["DESTINO"].apply(lambda x: get_coords(x, "lon"))

# Filtros
st.sidebar.header("Filtros")
origens = st.sidebar.multiselect("Origem", options=sorted(df_od["ORIGEM"].unique()), default=sorted(df_od["ORIGEM"].unique()))
destinos = st.sidebar.multiselect("Destino", options=sorted(df_od["DESTINO"].unique()), default=sorted(df_od["DESTINO"].unique()))
vol_range = st.sidebar.slider("Volume", 1, int(df_od["volume"].max()), (1, int(df_od["volume"].max())))

df_filtrado = df_od[
    (df_od["ORIGEM"].isin(origens)) &
    (df_od["DESTINO"].isin(destinos)) &
    (df_od["volume"] >= vol_range[0]) &
    (df_od["volume"] <= vol_range[1])
]

# Camadas para mapa
od_lines = [
    {
        "from_lat": row.orig_lat, "from_lon": row.orig_lon,
        "to_lat": row.dest_lat, "to_lon": row.dest_lon,
        "volume": row.volume
    }
    for _, row in df_filtrado.iterrows()
    if pd.notnull(row.orig_lat) and pd.notnull(row.dest_lat)
]

line_layer = pdk.Layer(
    "LineLayer",
    od_lines,
    get_source_position=["from_lon", "from_lat"],
    get_target_position=["to_lon", "to_lat"],
    get_width="volume",
    get_color="[255, 0, 0, 140]",
    pickable=True
)

view_state = pdk.ViewState(
    latitude=df_od["orig_lat"].mean(),
    longitude=df_od["orig_lon"].mean(),
    zoom=9
)

# Mapa
st.title("📍 Matriz Origem-Destino baseada na Pesquisa OD")

st.pydeck_chart(pdk.Deck(
    layers=[line_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v9"
))

# Total
st.markdown(f"""
<div style='font-size:20px; font-weight:bold; text-align:center; padding: 10px;'>
    Total de viagens exibidas: {df_filtrado["volume"].sum():,}
</div>
""".replace(",", "X").replace(".", ",").replace("X", "."), unsafe_allow_html=True)

# Gráfico
st.subheader("Gráfico por Par OD")
df_filtrado["par"] = df_filtrado["ORIGEM"] + " → " + df_filtrado["DESTINO"]
fig = px.bar(df_filtrado, x="par", y="volume", labels={"par": "Par OD", "volume": "Viagens"})
st.plotly_chart(fig, use_container_width=True)
