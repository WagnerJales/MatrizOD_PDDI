
import streamlit as st
import pandas as pd
import folium
from folium import PolyLine, Map, Marker
from streamlit_folium import st_folium

# Dados já tratados
df = pd.read_csv("dados_filtrados.csv")
municipios_json = {
    'São Luís','São José de Ribamar','Paço do Lumiar','Raposa','Alcântara','FORA DA RMGSL','Morros','Icatu','Bacabeira','Rosário','Cachoeira Grande','Presidente Juscelino','Axixá','Santa Rita'
}
