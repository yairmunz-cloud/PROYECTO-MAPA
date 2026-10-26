import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
from geopy.geocoders import Nominatim

# Configuración de pantalla para diseño de tablero ejecutivo amplio
st.set_page_config(page_title="Monitoreo de Sucursales", layout="wide")

# 1. BASE DE DATOS MAESTRA DE SUCURSALES (CON ESTADOS RELLENADOS)
@st.cache_data
def obtener_datos_sucursales():
    datos = [
        {"ESTADO": "AGUASCALIENTES", "SUCURSAL": "AGUASCALIENTES", "TEL": "449-918-5090 / 449-918-5092 / 449-918-5077 / 449-918-5082"},
        {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "MEXICALI", "TEL": "686-554-8832 / 686-554-8119 / 686-554-8539"},
        {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "TIJUANA", "TEL": "664-684-1622 / 664-634-1504 / 664-634-1535"},
        {"ESTADO": "BAJA CALIFORNIA SUR", "SUCURSAL": "LA PAZ", "TEL": "612-122-1012 / 612-123-5072 / 612-128-4929"},
        {"ESTADO": "BAJA CALIFORNIA SUR", "SUCURSAL": "LOS CABOS", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "CAMPECHE", "SUCURSAL": "CD. DEL CARMEN", "TEL": "938-118-1584 / 938-286-4995 / 938-383-2639"},
        {"ESTADO": "COAHUILA", "SUCURSAL": "SALTILLO", "TEL": "844-430-8817 / 844-430-8818 / 844-430-8819"},
        {"ESTADO": "COAHUILA", "SUCURSAL": "TORREON", "TEL": "871-713-4406 / 871-713-4979 / 871-713-4910 / 871-713-4410"},
        {"ESTADO": "COLIMA", "SUCURSAL": "COLIMA", "TEL": "312-330-6772 / 312-330-7029 / 312-314-0519"},
        {"ESTADO": "CHIAPAS", "SUCURSAL": "TUXTLA GUTIERREZ", "TEL": "961-612-6887 / 961-612-6933 / 961-612-6906"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CHIHUAHUA", "TEL": "614-433-4947 / 614-433-4948 / 614-433-4749"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CD. CUAUTEMOC", "TEL": "625-587-7003 / 625-587-7416 / 625-587-7407"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "DELICIAS", "TEL": "639-688-1517"},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CD. JUAREZ", "TEL": "656-611-3923 / 656-611-0352 / 656-613-8234"},
        {"ESTADO": "CDMX", "SUCURSAL": "METRO SUR", "TEL": "555-689-7402 / 555-698-1669"},
        {"ESTADO": "CDMX", "SUCURSAL": "BALBUENA", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "CDMX", "SUCURSAL": "AZCAPOTZALCO", "TEL": "555-353-4859"},
        {"ESTADO": "CDMX", "SUCURSAL": "METROPOLITANA", "TEL": "559-177-5011"},
        {"ESTADO": "CDMX", "SUCURSAL": "TAXQUEÑA", "TEL": "555-086-0047"},
        {"ESTADO": "CDMX", "SUCURSAL": "MATRIZ", "TEL": "559-177-5000"},
        {"ESTADO": "CDMX", "SUCURSAL": "CENTRO HISTORICO", "TEL": "555-521-8224"},
        {"ESTADO": "CDMX", "SUCURSAL": "CORDOBA", "TEL": "551-102-2050 / 555-080-0095"},
        {"ESTADO": "CDMX", "SUCURSAL": "LINDAVISTA", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "CDMX", "SUCURSAL": "LA VIGA", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "CDMX", "SUCURSAL": "POLANCO", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "CDMX", "SUCURSAL": "COAPA", "TEL": "555-920-3849 / 555-920-3829 / 555-528-5487"},
        {"ESTADO": "CDMX", "SUCURSAL": "AEROPUERTO", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "CDMX", "SUCURSAL": "XOCHIMILCO", "TEL": "552-345-7579"},
        {"ESTADO": "DURANGO", "SUCURSAL": "DURANGO", "TEL": "618-836-0043 / 618-836-0066 / 618-818-1464"},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "CELAYA", "TEL": "461-615-1632 / 461-615-6880 / 461-614-9447"},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "IRAPUATO", "TEL": "462-624-0501 / 462-624-0565 / 462-624-1381"},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "LEON", "TEL": "477-718-0465 / 477-718-0468 / 477-717-2102"},
        {"ESTADO": "GUERRERO", "SUCURSAL": "ACAPULCO", "TEL": "744-484-1566 / 744-484-1729"},
        {"ESTADO": "HIDALGO", "SUCURSAL": "PACHUCA", "TEL": "771-719-6773 / 771-719-7292"},
        {"ESTADO": "JALISCO", "SUCURSAL": "GUADALAJARA", "TEL": "333-827-1396 / 333-826-1965 / 333-825-6388"},
        {"ESTADO": "JALISCO", "SUCURSAL": "PUERTO VALLARTA", "TEL": "322-225-5474 / 322-225-9725"},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "CUAUTITLAN", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "METEPEC", "TEL": "722-223-4999 / 722-212-4520"},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "SATELITE", "TEL": "555-572-1252 / 555-572-1293 / 555-393-9493"},
        {"ESTADO": "MICHOACAN", "SUCURSAL": "MORELIA", "TEL": "443-324-6829 / 443-315-9160"},
        {"ESTADO": "MORELOS", "SUCURSAL": "CUERNAVACA", "TEL": "777-314-1524 / 777-314-1275"},
        {"ESTADO": "NAYARIT", "SUCURSAL": "TEPIC", "TEL": "311-129-4378 / 311-129-3458"},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "MONTERREY", "TEL": "818-340-2780"},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "ALLENDE", "TEL": "826-268-6768"},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "MONTERREY METROPOLITANA", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "OAXACA", "SUCURSAL": "OAXACA", "TEL": "951-132-5693 / 951-132-6879"},
        {"ESTADO": "PUEBLA", "SUCURSAL": "PUEBLA", "TEL": "222-240-0611 / 222-240-0775 / 222-237-6093"},
        {"ESTADO": "QUERETARO", "SUCURSAL": "QUERETARO", "TEL": "442-220-7777 / 442-226-3173"},
        {"ESTADO": "QUINTANA ROO", "SUCURSAL": "CANCUN", "TEL": "998-883-9243 / 998-883-9519"},
        {"ESTADO": "QUINTANA ROO", "SUCURSAL": "PLAYA DEL CARMEN", "TEL": "984-879-4340 / 984-879-3885"},
        {"ESTADO": "SAN LUIS POTOSI", "SUCURSAL": "SAN LUIS POTOSI", "TEL": "444-812-0187 / 444-833-3993"},
        {"ESTADO": "SINALOA", "SUCURSAL": "CULIACAN", "TEL": "667-714-8714 / 667-761-2460"},
        {"ESTADO": "SINALOA", "SUCURSAL": "MAZATLAN", "TEL": "669-118-4250 / 669-118-4257"},
        {"ESTADO": "SINALOA", "SUCURSAL": "LOS MOCHIS", "TEL": "Sin Teléfono Registrado"},
        {"ESTADO": "SONORA", "SUCURSAL": "CD. OBREGON", "TEL": "644-414-8984 / 664-414-8638"},
        {"ESTADO": "SONORA", "SUCURSAL": "HERMOSILLO", "TEL": "662-217-1136 / 662-213-4943"},
        {"ESTADO": "SONORA", "SUCURSAL": "NOGALES", "TEL": "631-314-8491 / 631-314-9886"},
        {"ESTADO": "TABASCO", "SUCURSAL": "VILLA HERMOSA", "TEL": "993-316-5612 / 993-316-5595"},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "MATAMOROS", "TEL": "868-149-1299 / 868-812-1676"},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "REYNOSA", "TEL": "899-925-5141 / 899-925-5140"},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "TAMPICO", "TEL": "833-224-7515 / 833-224-7517"},
        {"ESTADO": "TLAXCALA", "SUCURSAL": "TLAXCALA", "TEL": "246-466-3206 / 246-466-0539"},
        {"ESTADO": "VERACRUZ", "SUCURSAL": "COATZACOALCOS", "TEL": "921-217-7656 / 921-217-7723"},
        {"ESTADO": "VERACRUZ", "SUCURSAL": "VERACRUZ", "TEL": "229-931-7320 / 229-931-6748"},
        {"ESTADO": "VERACRUZ", "SUCURSAL": "XALAPA", "TEL": "228-141-6166"},
        {"ESTADO": "YUCATAN", "SUCURSAL": "MERIDA", "TEL": "999-923-4017 / 999-923-3885 / 999-923-1763"},
        {"ESTADO": "ZACATECAS", "SUCURSAL": "ZACATECAS", "TEL": "492-925-3987 / 492-922-1236"}
    ]
    df = pd.DataFrame(datos)
    
    # DATOS DE PRUEBA SIMULADOS
    df["No. REPORTE"] = None
    df["FECHA DE REPORTE"] = None
    
    # Casos simulados de prueba para validar tus nuevos rangos:
    df.loc[df["SUCURSAL"] == "AGUASCALIENTES", ["No. REPORTE", "FECHA DE REPORTE"]] = ["1", "2026-10-24"]       # Amarillo (2 días, rango 1-3)
    df.loc[df["SUCURSAL"] == "TIJUANA", ["No. REPORTE", "FECHA DE REPORTE"]] = ["REP-102", "2026-10-22"]       # Naranja (4 días, rango 3-5)
    df.loc[df["SUCURSAL"] == "CD. JUAREZ", ["No. REPORTE", "FECHA DE REPORTE"]] = ["REP-103", "2026-10-15"]    # Rojo (11 días, rango 6+)
    df.loc[df["SUCURSAL"] == "MEXICALI", ["No. REPORTE", "FECHA DE REPORTE"]] = ["0", None]                    # Sin reporte
    df.loc[df["SUCURSAL"] == "SALTILLO", ["No. REPORTE", "FECHA DE REPORTE"]] = ["sin reporte", None]          # Sin reporte
    
    return df

df = obtener_datos_sucursales()

# 2. CACHÉ DE COORDENADAS PARA EVITAR TIEMPOS DE ESPERA
@st.cache_data
def buscar_coordenadas(sucursal, estado):
    geolocator = Nominatim(user_agent="mexico_branch_final_version_v3")
    try:
        direccion = f"{sucursal}, {estado}, Mexico"
        location = geolocator.geocode(direccion, timeout=10)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return None, None

# 3. COMPROBADOR LÓGICO DE REPORTE ACTIVO (Regra: vacio, 0 o 'sin reporte' es inactivo)
def tiene_reporte_activo(valor_reporte):
    if pd.isna(valor_reporte):
        return False
    val = str(valor_reporte).strip().lower()
    if val in ["", "0", "sin reporte", "none", "nan", "vacio"]:
        return False
    return True

# 4. CÁLCULO DE COLORES POR RANGOS ESTABLECIDOS
def calcular_color(valor_reporte, fecha_str):
    if not tiene_reporte_activo(valor_reporte):
        return "#1E90FF"  # Azul estándar (Operación Normal)
        
    if pd.isna(fecha_str) or not fecha_str:
        return "#FFD700"  # Amarillo de respaldo si falta la fecha
        
    try:
        fecha_rep = pd.to_datetime(fecha_str)
        hoy = datetime.now()
        dias = (hoy - fecha_rep).days
        
        if dias <= 3:
            return "#FFD700"  # Amarillo (1 a 3 días)
        elif dias <= 5:
            return "#FF8C00"  # Naranja (3 a 5 días)
        else:
            return "#FF0000"  # Rojo (6 días en adelante)
    except:
        return "#FFD700"

# --- DISEÑO DE LA BARRA LATERAL IZQUIERDA ---
with st.sidebar:
    st.header("🔍 Selecciona un Estado")
    st.markdown("Filtra por ubicación para desplegar los teléfonos y estatus al instante.")
    
    # Desplegable 1: Estados
    lista_estados = sorted(df['ESTADO'].unique())
    estado_seleccionado = st.selectbox(
        "1. Selecciona el Estado:",
        options=lista_estados,
        index=0
    )
    
    # Filtrar según el estado seleccionado
    df_filtrado_estado = df[df['ESTADO'] == estado_seleccionado]
