import streamlit as st
import pandas as pd
import folium
from folium import PolyLine
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

# Controle de navegação entre páginas
if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "inicial"

@st.cache_data
def carregar_dados():
    df = pd.read_excel("PesquisaOD_2.xlsx", engine="openpyxl")
    df = df.rename(columns={
        "Qual o motivo da viagem?": "Motivo",
        "Com que frequência você faz essa viagem?": "Frequência",
        "A viagem foi realizada em qual período do dia?": "Periodo do dia",
        "Qual foi o principal meio de transporte que você usou?": "Principal Modal"
    })
    return df

try:
    df = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar o Excel: {e}")
    st.stop()

municipios_rmgsl = [
    "São Luís", "Paço do Lumiar", "Raposa", "São José de Ribamar",
    "Santa Rita", "Morros", "Icatu", "Rosário", "Bacabeira",
    "Cachoeira Grande", "Presidente Juscelino", "Alcântara"
]

municipios_coords = {
    "São Luís": [-2.538, -44.282], "Paço do Lumiar": [-2.510, -44.069],
    "Raposa": [-2.476, -44.096], "São José de Ribamar": [-2.545, -44.022],
    "Santa Rita": [-3.145, -44.332], "Morros": [-2.864, -44.039],
    "Icatu": [-2.762, -44.045], "Rosário": [-2.943, -44.254],
    "Bacabeira": [-2.969, -44.310], "Itapecuru Mirim": [-3.338, -44.341],
    "Cantanhede": [-3.608, -44.370], "Codó": [-4.454, -43.874],
    "Timon": [-5.096, -42.837], "Caxias": [-4.861, -43.371],
    "São Mateus do Maranhão": [-3.840, -45.326], "Viana": [-3.232, -44.995],
    "Bequimão": [-2.438, -44.779], "Pinheiro": [-2.538, -45.082],
    "Anajatuba": [-3.291, -44.623], "Alcântara": [-2.416, -44.437],
    "Humberto de Campos": [-1.756, -44.793], "Barreirinhas": [-2.754, -42.825],
    "Primeira Cruz": [-2.508, -43.440], "Santo Amaro": [-2.504, -43.255],
    "Cachoeira Grande": [-2.917, -44.223], "Presidente Juscelino": [-2.918, -44.068]
}

coords_municipios_od2 = {
    **municipios_coords,
    "São Luís - Bancaga": [-2.557948, -44.331238],
    "São Luís - Centro": [-2.515687, -44.296435],
    "São Luís - Cidade Operária": [-2.570548, -44.204126],
    "São Luís - Cohab": [-2.541977, -44.212127],
    "São Luís - Cohama": [-2.516324, -44.247146],
    "São Luís - Zona Industrial": [-2.614860, -44.256559]
}

# Página Inicial
if st.session_state.pagina_atual == "inicial":
    st.title("Pesquisa Origem-Destino - RMGSL 2025")
    st.markdown("""
    Esta aplicação apresenta os resultados da **Pesquisa Origem-Destino** realizada entre os dias
    **18/07/2025 a 25/07/2025**, com foco na Região Metropolitana da Grande São Luís (RMGSL):

    - **São Luís**
    - **Paço do Lumiar**
    - **Raposa**
    - **São José de Ribamar**
    - E demais municípios do entorno.

    Você pode visualizar os dados de duas formas:

    - 🔴 **Por município** (visão tradicional)
    - 🔵 **Subzonas de São Luís** (6 áreas internas)
    """)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔴 Ver Mapa por Município"):
            st.session_state.pagina_atual = "municipios"
            st.experimental_rerun()
    with col2:
        if st.button("🔵 Ver Mapa com Subzonas de São Luís"):
            st.session_state.pagina_atual = "subzonas"
            st.experimental_rerun()

# Página 1 – Mapa por Município
elif st.session_state.pagina_atual == "municipios":
    st.title("Mapa OD por Município")
    if st.button("🔙 Voltar à Página Inicial"):
        st.session_state.pagina_atual = "inicial"
        st.experimental_rerun()

    st.sidebar.header("Filtros")
    origens = st.sidebar.multiselect("Origem:", sorted(df["ORIGEM"].dropna().unique()))
    destinos = st.sidebar.multiselect("Destino:", sorted(df["DESTINO"].dropna().unique()))
    motivo = st.sidebar.multiselect("Motivo:", sorted(df["Motivo"].dropna().unique()))
    frequencia = st.sidebar.multiselect("Frequência:", sorted(df["Frequência"].dropna().unique()))
    periodo = st.sidebar.multiselect("Período:", sorted(df["Periodo do dia"].dropna().unique()))
    modal = st.sidebar.multiselect("Modal:", sorted(df["Principal Modal"].dropna().unique()))
    filtro_origem_rmgsl = st.sidebar.checkbox("Somente Origem na RMGSL")
    filtro_destino_rmgsl = st.sidebar.checkbox("Somente Destino na RMGSL")

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

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Total de pesquisas filtradas:**")
    st.sidebar.markdown(
        f"<span style='font-size:28px;color:#1f77b4;font-weight:bold'>{len(df_filtrado)}</span>",
        unsafe_allow_html=True
    )

    df_od = df_filtrado[df_filtrado["ORIGEM"] != df_filtrado["DESTINO"]].copy()
    df_od["par_od"] = df_od.apply(lambda row: tuple(sorted([row["ORIGEM"], row["DESTINO"]])), axis=1)
    fluxos = df_od.groupby("par_od").size().reset_index(name="total")
    fluxos[["ORIGEM", "DESTINO"]] = pd.DataFrame(fluxos["par_od"].tolist(), index=fluxos.index)

    mapa = folium.Map(location=[-2.53, -44.3], zoom_start=9, tiles="CartoDB Positron")
    for _, row in fluxos.iterrows():
        o, d = row["ORIGEM"], row["DESTINO"]
        if o in municipios_coords and d in municipios_coords:
            coords = [municipios_coords[o], municipios_coords[d]]
            folium.PolyLine(coords, color="red", weight=1 + row["total"]/30 * 5, opacity=0.8,
                            tooltip=f"{o} ↔ {d}: {row['total']}").add_to(mapa)
    st_folium(mapa, use_container_width=True, height=550)

# Página 2 – Mapa com Subzonas de São Luís
elif st.session_state.pagina_atual == "subzonas":
    st.title("Mapa OD com Subzonas de São Luís")
    if st.button("🔙 Voltar à Página Inicial"):
        st.session_state.pagina_atual = "inicial"
        st.experimental_rerun()

    df2 = df.copy()
    df2 = df2.rename(columns={
        "Qual o município de ORIGEM": "ORIGEM",
        "Qual o município de DESTINO": "DESTINO"
    })

    df2 = df2[df2["ORIGEM"].isin(coords_municipios_od2.keys()) & df2["DESTINO"].isin(coords_municipios_od2.keys())]
    df2 = df2[df2["ORIGEM"] != df2["DESTINO"]]
    df2["par_od"] = df2.apply(lambda row: tuple(sorted([row["ORIGEM"], row["DESTINO"]])), axis=1)
    fluxos2 = df2.groupby("par_od").size().reset_index(name="total")
    fluxos2[["ORIGEM", "DESTINO"]] = pd.DataFrame(fluxos2["par_od"].tolist(), index=fluxos2.index)

    mapa2 = folium.Map(location=[-2.53, -44.3], zoom_start=10, tiles="CartoDB Positron")
    for _, row in fluxos2.iterrows():
        o, d = row["ORIGEM"], row["DESTINO"]
        if o in coords_municipios_od2 and d in coords_municipios_od2:
            coords = [coords_municipios_od2[o], coords_municipios_od2[d]]
            folium.PolyLine(coords, color="darkblue", weight=1 + row["total"]/20 * 4, opacity=0.7,
                            tooltip=f"{o} ↔ {d}: {row['total']}").add_to(mapa2)
    for nome, coord in coords_municipios_od2.items():
        folium.Marker(location=coord, tooltip=nome).add_to(mapa2)

    st_folium(mapa2, use_container_width=True, height=550)

