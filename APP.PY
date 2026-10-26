import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Configuración de pantalla
st.set_page_config(page_title="Mapa de Reportes", layout="wide")
st.title("📍 Monitoreo de Sucursales e Incidencias")

# Datos de respaldo exactos de tu lista para que el mapa no falle nunca
datos_locales = [
    {"ESTADO": "AGUASCALIENTES", "SUCURSAL": "AGUASCALIENTES", "LAT": 21.8823, "LON": -102.2826, "REPORTE": "REP-01", "FECHA": "2026-10-24"},
    {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "MEXICALI", "LAT": 32.6245, "LON": -115.4522, "REPORTE": None, "FECHA": None},
    {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "TIJUANA", "LAT": 32.5149, "LON": -117.0382, "REPORTE": "REP-02", "FECHA": "2026-10-15"},
    {"ESTADO": "BAJA CALIFORNIA SUR", "SUCURSAL": "LA PAZ", "LAT": 24.1426, "LON": -110.3128, "REPORTE": None, "FECHA": None},
    {"ESTADO": "CHIAPAS", "SUCURSAL": "TUXTLA GUTIERREZ", "LAT": 16.7569, "LON": -93.1292, "REPORTE": "REP-03", "FECHA": "2026-10-05"},
    {"ESTADO": "CDMX", "SUCURSAL": "CENTRO HISTORICO", "LAT": 19.4326, "LON": -99.1332, "REPORTE": "REP-04", "FECHA": "2026-10-25"}
]

# Intentar leer desde Google Sheets (si ya pusiste tu link) o usar el respaldo
sheet_url = "REEMPLAZA_CON_TU_LINK_DE_GOOGLE_SHEETS"

if "://google.com" in sheet_url:
    try:
        df = pd.read_csv(sheet_url)
        df['ESTADO'] = df['ESTADO'].ffill()
        df['FECHA DE REPORTE'] = pd.to_datetime(df['FECHA DE REPORTE'], errors='coerce')
        st.success("🔄 Conectado en vivo a tu Google Sheets.")
    except:
        st.warning("⚠️ No se pudo leer el archivo en la nube. Mostrando datos de respaldo.")
        df = pd.DataFrame(datos_locales)
else:
    st.info("ℹ️ Mostrando vista previa del mapa. Para conectar tu Excel real, edita la variable 'sheet_url' en GitHub.")
    df = pd.DataFrame(datos_locales)

# Crear el mapa interactivo centrado en México
m = folium.Map(location=[23.6345, -102.5528], zoom_start=5)

# Lógica de color por días transcurridos
def calcular_color(fecha_str):
    if pd.isna(fecha_str) or not fecha_str:
        return "#1E90FF"  # Azul para sucursales normales
    
    try:
        fecha_rep = pd.to_datetime(fecha_str)
        hoy = datetime.now()
        dias = (hoy - fecha_rep).days
        
        if dias <= 3:
            return "#FFD700"  # Amarillo limpio (0-3 días)
        
        # Degradado controlado hacia el Rojo
        factor = min((dias - 3) / 12, 1.0)
        g = int(215 * (1 - factor))
        return f"#ff{g:02x}00"
    except:
        return "#FFD700"

# Dibujar marcadores
for idx, fila in df.iterrows():
    lat = fila.get('LAT', 19.4326)
    lon = fila.get('LON', -99.1332)
    rep = fila.get('REPORTE') or fila.get('No. REPORTE')
    fec = fila.get('FECHA') or fila.get('FECHA DE REPORTE')
    
    color = calcular_color(fec)
    
    popup_text = f"<b>Sucursal:</b> {fila['SUCURSAL']}<br><b>Estado:</b> {fila['ESTADO']}"
    if pd.notna(rep) and rep:
        popup_text += f"<br><b>Reporte:</b> {rep}<br><b>Fecha:</b> {fec}"
    
    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        popup=folium.Popup(popup_text, max_width=250),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8
    ).add_to(m)

st_folium(m, width="100%", height=600)
st.dataframe(df)
