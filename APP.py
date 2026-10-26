import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# Configuración inicial del Tablero de Control Ejecutivo con diseño ancho
st.set_page_config(page_title="Monitoreo de Sucursales", layout="wide")

# --- ESTILOS CSS AVANZADOS: GLASSMORPHISM Y ANIMACIONES ---
st.markdown("""
<style>
    /* Efecto Cristal Traslúcido con Blur (Glassmorphism) */
    .glass-panel {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255, 255, 255, 0.4);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08);
        margin-bottom: 20px;
    }
    
    /* Animación de entrada suave (Fade In) */
    .animated-fade-in {
        animation: fadeInAction 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes fadeInAction {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Estilos de los bloques de alerta en el panel */
    .st-normal { padding: 12px; background: rgba(46,204,113,0.15); border-left: 5px solid #2ecc71; border-radius: 4px; color: #27ae60; font-weight: bold; }
    .st-yellow { padding: 12px; background: rgba(241,196,15,0.15); border-left: 5px solid #f1c40f; border-radius: 4px; color: #b7950b; font-weight: bold; }
    .st-orange { padding: 12px; background: rgba(230,126,34,0.15); border-left: 5px solid #e67e22; border-radius: 4px; color: #d35400; font-weight: bold; }
    .st-red { padding: 12px; background: rgba(231,76,60,0.15); border-left: 5px solid #e74c3c; border-radius: 4px; color: #c0392b; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 1. BASE DE DATOS ESTRUCTURADA DE MANERA SEGURA (CERO RIESGOS DE COMPILACIÓN)
@st.cache_data
def obtener_datos_sucursales():
    estados = [
        "AGUASCALIENTES", "BAJA CALIFORNIA NORTE", "BAJA CALIFORNIA NORTE", "BAJA CALIFORNIA SUR", "BAJA CALIFORNIA SUR",
        "CAMPECHE", "COAHUILA", "COAHUILA", "COLIMA", "CHIAPAS", "CHIHUAHUA", "CHIHUAHUA", "CHIHUAHUA", "CHIHUAHUA",
        "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX", "CDMX",
        "DURANGO", "GUANAJUATO", "GUANAJUATO", "GUANAJUATO", "GUERRERO", "HIDALGO", "JALISCO", "JALISCO",
        "EDO. MEXICO", "EDO. MEXICO", "EDO. MEXICO", "MICHOACAN", "MORELOS", "NAYARIT", "NUEVO LEON", "NUEVO LEON",
        "NUEVO LEON", "OAXACA", "PUEBLA", "QUERETARO", "QUINTANA ROO", "QUINTANA ROO", "SAN LUIS POTOSI",
        "SINALOA", "SINALOA", "SINALOA", "SONORA", "SONORA", "SONORA", "TABASCO", "TAMAULIPAS", "TAMAULIPAS",
        "TAMAULIPAS", "TLAXCALA", "VERACRUZ", "VERACRUZ", "VERACRUZ", "YUCATAN", "ZACATECAS"
    ]
    
    sucursales = [
        "AGUASCALIENTES", "MEXICALI", "TIJUANA", "LA PAZ", "LOS CABOS",
        "CD. DEL CARMEN", "SALTILLO", "TORREON", "COLIMA", "TUXTLA GUTIERREZ", "CHIHUAHUA", "CD. CUAUTEMOC", "DELICIAS", "CD. JUAREZ",
        "METRO SUR", "BALBUENA", "AZCAPOTZALCO", "METROPOLITANA", "TAXQUEÑA", "MATRIZ", "CENTRO HISTORICO", "CORDOBA", "LINDAVISTA", "LA VIGA", "POLANCO", "COAPA", "AEROPUERTO", "XOCHIMILCO",
        "DURANGO", "CELAYA", "IRAPUATO", "LEON", "ACAPULCO", "PACHUCA", "GUADALAJARA", "PUERTO VALLARTA",
        "CUAUTITLAN", "METEPEC", "SATELITE", "MORELIA", "CUERNAVACA", "TEPIC", "MONTERREY", "ALLENDE", "MONTERREY METROPOLITANA",
        "OAXACA", "PUEBLA", "QUERETARO", "CANCUN", "PLAYA DEL CARMEN", "SAN LUIS POTOSI",
        "CULIACAN", "MAZATLAN", "LOS MOCHIS", "CD. OBREGON", "HERMOSILLO", "NOGALES", "VILLA HERMOSA", "MATAMOROS", "REYNOSA", "TAMPICO",
        "TLAXCALA", "COATZACOALCOS", "VERACRUZ", "XALAPA", "MERIDA", "ZACATECAS"
    ]
    
    telefonos = [
        "449-918-5090 / 449-918-5092 / 449-918-5077", "686-554-8832 / 686-554-8119 / 686-554-8539", "664-684-1622 / 664-634-1504", "612-122-1012 / 612-123-5072", "Sin Teléfono Registrado",
        "938-118-1584 / 938-286-4995", "844-430-8817 / 844-430-8818", "871-713-4406 / 871-713-4979", "312-330-6772 / 312-330-7029", "961-612-6887 / 961-612-6933", "614-433-4947 / 614-433-4948", "625-587-7003 / 625-587-7416", "639-688-1517", "656-611-3923 / 656-611-0352",
        "555-689-7402 / 555-698-1669", "Sin Teléfono Registrado", "555-353-4859", "559-177-5011", "555-086-0047", "559-177-5000", "555-521-8224", "551-102-2050 / 555-080-0095", "Sin Teléfono Registrado", "Sin Teléfono Registrado", "Sin Teléfono Registrado", "555-920-3849 / 555-920-3829", "Sin Teléfono Registrado", "552-345-7579",
        "618-836-0043 / 618-836-0066", "461-615-1632 / 461-615-6880", "462-624-0501 / 462-624-0565", "477-718-0465 / 477-718-0468", "744-484-1566 / 744-484-1729", "771-719-6773 / 771-719-7292", "333-827-1396 / 333-826-1965", "322-225-5474 / 322-225-9725",
        "Sin Teléfono Registrado", "722-223-4999 / 722-212-4520", "555-572-1252 / 555-572-1293", "443-324-6829 / 443-315-9160", "777-314-1524 / 777-314-1275", "311-129-4378 / 311-129-3458", "818-340-2780", "826-268-6768", "Sin Teléfono Registrado",
        "951-132-5693 / 951-132-6879", "222-240-0611 / 222-240-0775", "442-220-7777 / 442-226-3173", "998-883-9243 / 998-883-9519", "984-879-4340 / 984-879-3885", "444-812-0187 / 444-833-3993",
        "667-714-8714 / 667-761-2460", "669-118-4250 / 669-118-4257", "Sin Teléfono Registrado", "644-414-8984 / 664-414-8638", "662-217-1136 / 662-213-4943", "631-314-8491 / 631-314-9886", "993-316-5612 / 993-316-5595", "868-149-1299 / 868-812-1676", "899-925-5141 / 899-925-5140", "833-224-7515 / 833-224-7517",
        "246-466-3206 / 246-466-0539", "921-217-7656 / 921-217-7723", "229-931-7320 / 229-931-6748", "228-141-6166", "999-923-4017 / 999-923-3885", "492-925-3987 / 492-922-1236"
    ]
    
    lats = [
        21.8823, 32.6245, 32.5149, 24.1426, 22.8905, 18.6353, 25.4338, 25.5439, 19.2433, 16.7569, 28.6330, 28.4061, 28.1942, 31.6904,
        19.3528, 19.4247, 19.4862, 19.4312, 19.3458, 19.4326, 19.4342, 19.4201, 19.4912, 19.3812, 19.4342, 19.2988, 19.4362, 19.2632,
        24.0277, 20.5218, 20.6742, 21.1226, 16.8531, 20.1011, 20.6597, 20.6534, 19.6698, 19.2555, 19.5115, 19.7060, 18.9242, 21.5039,
        25.6866, 25.2811, 25.6714, 17.0732, 19.0414, 20.5888, 21.1619, 20.6296, 22.1565, 24.8054, 23.2494, 25.7904, 27.4828, 29.0729,
        31.3012, 17.9892, 25.8690, 26.0806, 22.2562, 19.3182, 18.1398, 19.1738, 19.5438, 20.9674, 22.7709
    ]
    
    lons = [
        -102.2826, -115.4522, -117.0382, -110.3128, -109.9167, -91.8315, -101.0053, -103.4190, -103.7247, -93.1292, -106.0691, -106.8664, -105.4716, -106.4245,
        -99.1678, -99.1025, -99.1853, -99.1415, -99.1432, -99.1332, -99.1385, -99.1611, -99.1215, -99.1245, -99.1958, -99.1212, -99.0815, -99.1021,
        -104.6532, -100.8140, -101.3545, -101.6807, -99.8237, -98.7591, -103.3496, -105.2253, -99.1764, -99.6048, -99.2312, -101.1950, -99.2216, -104.8946,
        -100.3161, -100.0212, -100.3090, -96.7266, -98.2063, -100.3899, -86.8515, -87.0739, -100.9855, -107.3940, -106.4111, -108.9858, -109.9304, -110.9559,
        -110.9381, -92.9475, -97.5027, -98.2883, -97.8659, -98.2375, -94.4532, -96.1342, -96.9102, -89.5926, -102.5832
    ]
    
    df_result = pd.DataFrame({
        "ESTADO": estados, "SUCURSAL": sucursales, "TEL": telefonos, "LAT": lats, "LON": lons
    })
    
    df_result["No. REPORTE"] = "0"
    df_result["FECHA DE REPORTE"] = ""
    
    # Casos de prueba simulados
    df_result.loc[df_result["SUCURSAL"] == "AGUASCALIENTES", ["No. REPORTE", "FECHA DE REPORTE"]] = ["1", "2026-10-24"]
    df_result.loc[df_result["SUCURSAL"] == "TIJUANA", ["No. REPORTE", "FECHA DE REPORTE"]] = ["REP-102", "2026-10-22"]
    df_result.loc[df_result["SUCURSAL"] == "CD. JUAREZ", ["No. REPORTE", "FECHA DE REPORTE"]] = ["REP-103", "2026-10-14"]
    df_result.loc[df_result["SUCURSAL"] == "MEXICALI", ["No. REPORTE", "FECHA DE REPORTE"]] = ["0", ""]
    df_result.loc[df_result["SUCURSAL"] == "SALTILLO", ["No. REPORTE", "FECHA DE REPORTE"]] = ["sin reporte", ""]
    return df_result

df = obtener_datos_sucursales()

# 2. VERIFICADOR LÓGICO DE REPORTES ACTIVOS
def tiene_reporte_activo(valor_reporte):
    if pd.isna(valor_reporte):
        return False
    val = str(valor_reporte).strip().lower()
    if val in ["", "0", "sin reporte", "none", "nan", "vacio"]:
        return False
    return True

# 3. CÁLCULO DE COLORES POR RANGOS ESTRICTOS
def calcular_color(valor_reporte, fecha_str):
    if not tiene_reporte_activo(valor_reporte):
        return "#1E90FF"  # Azul
    if pd.isna(fecha_str) or not fecha_str or str(fecha_str).strip() == "":
        return "#FFD700"
    try:
        fecha_rep = pd.to_datetime(fecha_str)
        dias = (datetime.now() - fecha_rep).days
        if dias <= 3:
            return "#FFD700"  # Amarillo
        elif dias <= 5:
            return "#FF8C00"  # Naranja
        else:
            return "#FF0000"  # Rojo
    except:
        return "#FFD700"

# --- DISTRIBUCIÓN DE PANTALLA EN PARALELO (COLUMNAS) ---
col_panel, col_mapa = st.columns([1, 2])  # Proporción: 1/3 panel izquierdo, 2/3 mapa derecho

with col_panel:
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.subheader("🔍 Filtro de Sucursales")
    
    lista_estados = sorted(df['ESTADO'].unique())
    estado_sel = st.selectbox("1. Selecciona el Estado:", options=lista_estados, index=0)
    
    df_filtrado_est = df[df['ESTADO'] == estado_sel]
    lista_sucursales = sorted(df_filtrado_est['SUCURSAL'].unique())
    
    suc_sel = st.selectbox("2. Selecciona la Sucursal:", options=lista_sucursales, index=0)
    st.markdown("---")
    
    subset = df_filtrado_est[df_filtrado_est['SUCURSAL'] == suc_sel]
    
    if not subset.empty:
        # CORRECCIÓN DE EXTRACCIÓN CON .iloc[0]: Convierte las celdas en textos individuales nativos
        suc_nombre = str(subset['SUCURSAL'].iloc[0])
