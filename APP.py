import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# Configuración de pantalla
st.set_page_config(page_title="Mapa de Reportes", layout="wide")
st.title("📍 Monitoreo de Sucursales Telmex en la República Mexicana")
st.markdown("Los marcadores cambian de amarillo a rojo según los días transcurridos desde el reporte.")

# 1. BASE DE DATOS REAL DE TUS SUCURSALES (Para asegurar que cargue de inmediato)
@st.cache_data
def obtener_datos_sucursales():
    # Hemos estructurado tu lista exacta rellenando los estados vacíos
    datos = [
        {"ESTADO": "AGUASCALIENTES", "SUCURSAL": "AGUASCALIENTES", "TEL": "449-918-5090"},
        {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "MEXICALI", "TEL": "686-554-8832"},
        {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "TIJUANA", "TEL": "664-684-1622"},
        {"ESTADO": "BAJA CALIFORNIA SUR", "SUCURSAL": "LA PAZ", "TEL": "612-122-1012"},
        {"ESTADO": "BAJA CALIFORNIA SUR", "SUCURSAL": "LOS CABOS", "TEL": "Sin Teléfono"},
        {"ESTADO": "CAMPECHE", "SUCURSAL": "CD. DEL CARMEN", "TEL": "938-118-1584"},
        {"ESTADO": "COAHUILA", "SUCURSAL": "SALTILLO", "TEL": "844-430-8817"},
        {"ESTADO": "COAHUILA", "SUCURSAL": "TORREON", "TEL": "871-713-4406"},
        {"ESTADO": "COLIMA", "SUCURSAL": "COLIMA", "TEL": "312-330-6772"},
        {"ESTADO": "CHIAPAS", "SUCURSAL": "TUXTLA GUTIERREZ", "TEL": "961-612-6887"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CHIHUAHUA", "TEL": "614-433-4947"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CD. CUAUTEMOC", "TEL": "625-587-7003"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "DELICIAS", "TEL": "639-688-1517"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CD. JUAREZ", "TEL": "656-611-3923"},
        {"ESTADO": "CDMX", "SUCURSAL": "METRO SUR", "TEL": "555-689-7402"},
        {"ESTADO": "CDMX", "SUCURSAL": "BALBUENA", "TEL": "Sin Teléfono"},
        {"ESTADO": "CDMX", "SUCURSAL": "AZCAPOTZALCO", "TEL": "555-353-4859"},
        {"ESTADO": "CDMX", "SUCURSAL": "METROPOLITANA", "TEL": "559-177-5011"},
        {"ESTADO": "CDMX", "SUCURSAL": "TAXQUEÑA", "TEL": "555-086-0047"},
        {"ESTADO": "CDMX", "SUCURSAL": "MATRIZ", "TEL": "559-177-5000"},
        {"ESTADO": "CDMX", "SUCURSAL": "CENTRO HISTORICO", "TEL": "555-521-8224"},
        {"ESTADO": "CDMX", "SUCURSAL": "CORDOBA", "TEL": "551-102-2050"},
        {"ESTADO": "CDMX", "SUCURSAL": "LINDAVISTA", "TEL": "Sin Teléfono"},
        {"ESTADO": "CDMX", "SUCURSAL": "LA VIGA", "TEL": "Sin Teléfono"},
        {"ESTADO": "CDMX", "SUCURSAL": "POLANCO", "TEL": "Sin Teléfono"},
        {"ESTADO": "CDMX", "SUCURSAL": "COAPA", "TEL": "555-920-3849"},
        {"ESTADO": "CDMX", "SUCURSAL": "AEROPUERTO", "TEL": "Sin Teléfono"},
        {"ESTADO": "CDMX", "SUCURSAL": "XOCHIMILCO", "TEL": "552-345-7579"},
        {"ESTADO": "DURANGO", "SUCURSAL": "DURANGO", "TEL": "618-836-0043"},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "CELAYA", "TEL": "461-615-1632"},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "IRAPUATO", "TEL": "462-624-0501"},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "LEON", "TEL": "477-718-0465"},
        {"ESTADO": "GUERRERO", "SUCURSAL": "ACAPULCO", "TEL": "744-484-1566"},
        {"ESTADO": "HIDALGO", "SUCURSAL": "PACHUCA", "TEL": "771-719-6773"},
        {"ESTADO": "JALISCO", "SUCURSAL": "GUADALAJARA", "TEL": "333-827-1396"},
        {"ESTADO": "JALISCO", "SUCURSAL": "PUERTO VALLARTA", "TEL": "322-225-5474"},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "CUAUTITLAN", "TEL": "Sin Teléfono"},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "METEPEC", "TEL": "722-223-4999"},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "SATELITE", "TEL": "555-572-1252"},
        {"ESTADO": "MICHOACAN", "SUCURSAL": "MORELIA", "TEL": "443-324-6829"},
        {"ESTADO": "MORELOS", "SUCURSAL": "CUERNAVACA", "TEL": "777-314-1524"},
        {"ESTADO": "NAYARIT", "SUCURSAL": "TEPIC", "TEL": "311-129-4378"},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "MONTERREY", "TEL": "818-340-2780"},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "ALLENDE", "TEL": "826-268-6768"},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "MONTERREY METROPOLITANA", "TEL": "Sin Teléfono"},
        {"ESTADO": "OAXACA", "SUCURSAL": "OAXACA", "TEL": "951-132-5693"},
        {"ESTADO": "PUEBLA", "SUCURSAL": "PUEBLA", "TEL": "222-240-0611"},
        {"ESTADO": "QUERETARO", "SUCURSAL": "QUERETARO", "TEL": "442-220-7777"},
        {"ESTADO": "QUINTANA ROO", "SUCURSAL": "CANCUN", "TEL": "998-883-9243"},
        {"ESTADO": "QUINTANA ROO", "SUCURSAL": "PLAYA DEL CARMEN", "TEL": "984-879-4340"},
        {"ESTADO": "SAN LUIS POTOSI", "SUCURSAL": "SAN LUIS POTOSI", "TEL": "444-812-0187"},
        {"ESTADO": "SINALOA", "SUCURSAL": "CULIACAN", "TEL": "667-714-8714"},
        {"ESTADO": "SINALOA", "SUCURSAL": "MAZATLAN", "TEL": "669-118-4250"},
        {"ESTADO": "SINALOA", "SUCURSAL": "LOS MOCHIS", "TEL": "Sin Teléfono"},
        {"ESTADO": "SONORA", "SUCURSAL": "CD. OBREGON", "TEL": "644-414-8984"},
        {"ESTADO": "SONORA", "SUCURSAL": "HERMOSILLO", "TEL": "662-217-1136"},
        {"ESTADO": "SONORA", "SUCURSAL": "NOGALES", "TEL": "631-314-8491"},
        {"ESTADO": "TABASCO", "SUCURSAL": "VILLA HERMOSA", "TEL": "993-316-5612"},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "MATAMOROS", "TEL": "868-149-1299"},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "REYNOSA", "TEL": "899-925-5141"},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "TAMPICO", "TEL": "833-224-7515"},
        {"ESTADO": "TLAXCALA", "SUCURSAL": "TLAXCALA", "TEL": "246-466-3206"},
        {"ESTADO": "VERACRUZ", "SUCURSAL": "COATZACOALCOS", "TEL": "921-217-7656"},
        {"ESTADO": "VERACRUZ", "SUCURSAL": "VERACRUZ", "TEL": "229-931-7320"},
        {"ESTADO": "VERACRUZ", "SUCURSAL": "XALAPA", "TEL": "228-141-6166"},
        {"ESTADO": "YUCATAN", "SUCURSAL": "MERIDA", "TEL": "999-923-4017"},
        {"ESTADO": "ZACATECAS", "SUCURSAL": "ZACATECAS", "TEL": "492-925-3987"}
    ]
    df = pd.DataFrame(datos)
    
    # SIMULACIÓN DE REPORTES PARA LA VISTA PREVIA (Cambia esto cuando conectes tu Google Sheets)
    # Aquí puedes simular reportes agregando datos de prueba:
    df["No. REPORTE"] = None
    df["FECHA DE REPORTE"] = None
    
    # Casos de prueba simulados para comprobar los colores del degradado:
    df.loc[df["SUCURSAL"] == "AGUASCALIENTES", ["No. REPORTE", "FECHA DE REPORTE"]] = ["REP-101", "2026-10-24"]  # Amarillo (2 días)
    df.loc[df["SUCURSAL"] == "TIJUANA", ["No. REPORTE", "FECHA DE REPORTE"]] = ["REP-102", "2026-10-20"]         # Naranja (6 días)
    df.loc[df["SUCURSAL"] == "CD. JUAREZ", ["No. REPORTE", "FECHA DE REPORTE"]] = ["REP-103", "2026-10-10"]      # Rojo Intenso (16 días)
    
    return df

df = obtener_datos_sucursales()

# 2. BUSCADOR AUTOMÁTICO DE COORDENADAS (Geocodificación con caché)
@st.cache_data
def buscar_coordenadas(sucursal, estado):
    geolocator = Nominatim(user_agent="mexico_branch_monitor_v2")
    try:
        # Buscamos combinando Sucursal, Estado y País para no fallar
        direccion = f"{sucursal}, {estado}, Mexico"
        location = geolocator.geocode(direccion, timeout=10)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

# 3. LÓGICA DE COLORES DEGRADADOS (Amarillo -> Rojo)
def calcular_color(fecha_str):
    if pd.isna(fecha_str) or not fecha_str:
        return "#1E90FF"  # Azul para sucursales sin reporte
    
    try:
        fecha_rep = pd.to_datetime(fecha_str)
        hoy = datetime.now()
        dias = (hoy - fecha_rep).days
        
        if dias <= 3:
            return "#FFD700"  # Amarillo limpio (0-3 días)
        
        # Degradado dinámico hacia el Rojo (Se vuelve totalmente rojo al llegar a 15 días)
        factor = min((dias - 3) / 12, 1.0)
        g = int(215 * (1 - factor))
        return f"#ff{g:02x}00"
    except:
        return "#FFD700"

# Crear mapa centrado en el centro geográfico de México
m = folium.Map(location=[23.6345, -102.5528], zoom_start=5)

st.info("🗺️ Ubicando sucursales en el mapa de México de manera automática...")

# Dibujar las sucursales reales
for idx, fila in df.iterrows():
    suc = fila['SUCURSAL']
    est = fila['ESTADO']
    tel = fila['TEL']
    rep = fila['No. REPORTE']
    fec = fila['FECHA DE REPORTE']
    
    lat, lon = buscar_coordenadas(suc, est)
    
    # Si encuentra el lugar en el mapa, dibuja el marcador
    if lat and lon:
        color = calcular_color(fec)
        
        popup_text = f"""
        <div style='font-family: Arial; font-size: 13px;'>
            <b>Sucursal:</b> {suc}<br>
            <b>Estado:</b> {est}<br>
            <b>Línea Telmex:</b> {tel}<br>
        """
        if rep:
            popup_text += f"<hr style='margin:5px 0;'><span style='color:red;'><b>⚠️ Reporte:</b> {rep}</span><br><b>Fecha:</b> {fec}"
        popup_text += "</div>"
        
        folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            popup=folium.Popup(popup_text, max_width=250),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8
        ).add_to(m)

# Mostrar mapa en Streamlit
st_folium(m, width="100%", height=600)

# Tabla de consulta en la parte inferior
st.subheader("📋 Base de Datos de Monitoreo")
st.dataframe(df, use_container_width=True)
