
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

