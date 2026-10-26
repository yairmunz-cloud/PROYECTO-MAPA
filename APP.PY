import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Configuración de la página web de visualización
st.set_page_config(page_title="Mapa de Reportes Sucursales", layout="wide")
st.title("📍 Monitoreo de Sucursales e Incidencias en la República Mexicana")
st.markdown("Los datos se actualizan automáticamente desde el archivo maestro. El color del marcador cambia de amarillo a rojo según la antigüedad del reporte.")

# 1. FUNCIÓN PARA CONECTAR EL EXCEL EN LA NUBE (Google Sheets)
# Reemplaza 'TU_LINK_DE_SHARE_A_CSV' con el enlace de publicación en la nube de tu documento
@st.cache_data(ttl=600)  # Se actualiza automáticamente cada 10 minutos
def cargar_datos():
    # URL de ejemplo (deberás sustituirla por la tuya exportada en CSV)
    sheet_url = "https://google.com"
    df = pd.read_csv(sheet_url)
    
    # Rellenar estados hacia abajo en caso de celdas combinadas del Excel original
    df['ESTADO'] = df['ESTADO'].ffill()
    df['FECHA DE REPORTE'] = pd.to_datetime(df['FECHA DE REPORTE'], errors='coerce')
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error("Por el momento, conecta el enlace de tu archivo maestro para visualizar los datos en vivo.")
    # Mapeo de respaldo local con tus datos estructurados para fines informativos
    df = pd.DataFrame({
        'ESTADO': ['AGUASCALIENTES', 'BAJA CALIFORNIA NORTE', 'BAJA CALIFORNIA NORTE', 'CDMX'],
        'SUCURSAL': ['AGUASCALIENTES', 'MEXICALI', 'TIJUANA', 'CENTRO HISTORICO'],
        'LINEA TELMEX': ['449-918-5090', '686-554-8832', '664-684-1622', '555-521-8224'],
        'No. REPORTE': ['REP-001', None, 'REP-002', 'REP-003'],
        'FECHA DE REPORTE': [pd.Timestamp('2026-10-24'), pd.NaT, pd.Timestamp('2026-10-20'), pd.Timestamp('2026-10-10')]
    })

# 2. FUNCIÓN PARA CALCULAR EL DEGRADADO DE COLOR (Amarillo -> Rojo)
def obtener_color_por_antiguedad(fecha_reporte):
    if pd.isna(fecha_reporte):
        return "#3186cc"  # Azul estándar si no hay fecha válida
        
    hoy = datetime.now()
    dias_transcurridos = (hoy - fecha_reporte).days
    
    if dias_transcurridos <= 3:
        return "#FFD700"  # Amarillo limpio (0 a 3 días)
    
    # Degradado dinámico a partir del día 4 hasta el 15 (Máximo rojo)
    # Factor de transicion entre 0.0 (Amarillo) y 1.0 (Rojo total)
    max_dias_criticos = 15
    factor = min((dias_transcurridos - 3) / (max_dias_criticos - 3), 1.0)
    
    # Interpolación RGB de Amarillo (255, 215, 0) a Rojo (255, 0, 0)
    r = 255
    g = int(215 * (1 - factor))
    b = 0
    
    return f"#{r:02x}{g:02x}{b:02x}"

# 3. PROCESAMIENTO DE GEOLOCALIZACIÓN
geolocator = Nominatim(user_agent="mexico_branch_coder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Inicializar mapa centrado en la República Mexicana
m = folium.Map(location=[23.634501, -102.552784], zoom_start=5, control_scale=True)

# Colocar marcadores en el mapa
for idx, fila in df.iterrows():
    sucursal = fila['SUCURSAL']
    estado = fila['ESTADO']
    reporte = fila['No. REPORTE']
    fecha = fila['FECHA DE REPORTE']
    telefonos = fila['LINEA TELMEX']
    
    # Crear consulta de dirección
    direccion_busqueda = f"{sucursal}, {estado}, Mexico"
    location = geolocator.geocode(direccion_busqueda)
    
    if location:
        # Definir lógica de color de marcador
        tiene_reporte = pd.notna(reporte) and str(reporte).strip() != ""
        
        if tiene_reporte:
            color_hex = obtener_color_por_antiguedad(fecha)
            dias = (datetime.now() - fecha).days if pd.notna(fecha) else "Sin Fecha"
            info_reporte = f"<b>No. Reporte:</b> {reporte}<br><b>Fecha:</b> {fecha.strftime('%Y-%m-%d') if pd.notna(fecha) else 'N/A'}<br><b>Días de retraso:</b> {dias}"
        else:
            color_hex = "#1E90FF"  # Azul para sucursales operando normal sin reportes
            info_reporte = "<i>Sin reportes activos</i>"
            
        # Contenido del cuadro interactivo (Popup)
        popup_html = f"""
        <div style='font-family: Arial, sans-serif; size: 12px;'>
            <h4 style='margin:0 0 5px 0; color:#333;'>Sucursal {sucursal}</h4>
            <b>Estado:</b> {estado}<br>
            <b>Teléfonos:</b><br>{str(telefonos).replace('\n', '<br>')}<br><br>
            <div style='padding: 5px; background-color: {color_hex}22; border-left: 4px solid {color_hex};'>
                {info_reporte}
            </div>
        </div>
        """
        
        # Dibujar marcador circular con el color correspondiente en el mapa
        folium.CircleMarker(
            location=[location.latitude, location.longitude],
            radius=8,
            popup=folium.Popup(popup_html, max_width=300),
            color=color_hex,
            fill=True,
            fill_color=color_hex,
            fill_opacity=0.7
        ).add_to(m)

# Desplegar el mapa interactivo en la pantalla web
st_folium(m, width=1200, height=650)

# Tabla de consulta rápida secundaria debajo del mapa
st.subheader("📋 Resumen de datos cargados")
st.dataframe(df, use_container_width=True)
