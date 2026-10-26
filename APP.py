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

# 1. BASE DE DATOS MAESTRA CON COORDENADAS INTEGRADAS Y REVISADAS
@st.cache_data
def obtener_datos_sucursales():
    datos = [
        {"ESTADO": "AGUASCALIENTES", "SUCURSAL": "AGUASCALIENTES", "TEL": "449-918-5090 / 449-918-5092 / 449-918-5077 / 449-918-5082", "LAT": 21.8823, "LON": -102.2826},
        {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "MEXICALI", "TEL": "686-554-8832 / 686-554-8119 / 686-554-8539", "LAT": 32.6245, "LON": -115.4522},
        {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "TIJUANA", "TEL": "664-684-1622 / 664-634-1504 / 664-634-1535", "LAT": 32.5149, "LON": -117.0382},
        {"ESTADO": "BAJA CALIFORNIA SUR", "SUCURSAL": "LA PAZ", "TEL": "612-122-1012 / 612-123-5072 / 612-128-4929", "LAT": 24.1426, "LON": -110.3128},
        {"ESTADO": "BAJA CALIFORNIA SUR", "SUCURSAL": "LOS CABOS", "TEL": "Sin Teléfono Registrado", "LAT": 22.8905, "LON": -109.9167},
        {"ESTADO": "CAMPECHE", "SUCURSAL": "CD. DEL CARMEN", "TEL": "938-118-1584 / 938-286-4995 / 938-383-2639", "LAT": 18.6353, "LON": -91.8315},
        {"ESTADO": "COAHUILA", "SUCURSAL": "SALTILLO", "TEL": "844-430-8817 / 844-430-8818 / 844-430-8819", "LAT": 25.4338, "LON": -101.0053},
        {"ESTADO": "COAHUILA", "SUCURSAL": "TORREON", "TEL": "871-713-4406 / 871-713-4979 / 871-713-4910 / 871-713-4410", "LAT": 25.5439, "LON": -103.4190},
        {"ESTADO": "COLIMA", "SUCURSAL": "COLIMA", "TEL": "312-330-6772 / 312-330-7029 / 312-314-0519", "LAT": 19.2433, "LON": -103.7247},
        {"ESTADO": "CHIAPAS", "SUCURSAL": "TUXTLA GUTIERREZ", "TEL": "961-612-6887 / 961-612-6933 / 961-612-6906", "LAT": 16.7569, "LON": -93.1292},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CHIHUAHUA", "TEL": "614-433-4947 / 614-433-4948 / 614-433-4749", "LAT": 28.6330, "LON": -106.0691},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CD. CUAUTEMOC", "TEL": "625-587-7003 / 625-587-7416 / 625-587-7407", "LAT": 28.4061, "LON": -106.8664},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "DELICIAS", "TEL": "639-688-1517", "LAT": 28.1942, "LON": -105.4716},
        {"ESTADO": "CHIHUAHUA", "SUCURSAL": "CD. JUAREZ", "TEL": "656-611-3923 / 656-611-0352 / 656-613-8234", "LAT": 31.6904, "LON": -106.4245},
        {"ESTADO": "CDMX", "SUCURSAL": "METRO SUR", "TEL": "555-689-7402 / 555-698-1669", "LAT": 19.3528, "LON": -99.1678},
        {"ESTADO": "CDMX", "SUCURSAL": "BALBUENA", "TEL": "Sin Teléfono Registrado", "LAT": 19.4247, "LON": -99.1025},
        {"ESTADO": "CDMX", "SUCURSAL": "AZCAPOTZALCO", "TEL": "555-353-4859", "LAT": 19.4862, "LON": -99.1853},
        {"ESTADO": "CDMX", "SUCURSAL": "METROPOLITANA", "TEL": "559-177-5011", "LAT": 19.4312, "LON": -99.1415},
        {"ESTADO": "CDMX", "SUCURSAL": "TAXQUEÑA", "TEL": "555-086-0047", "LAT": 19.3458, "LON": -99.1432},
        {"ESTADO": "CDMX", "SUCURSAL": "MATRIZ", "TEL": "559-177-5000", "LAT": 19.4326, "LON": -99.1332},
        {"ESTADO": "CDMX", "SUCURSAL": "CENTRO HISTORICO", "TEL": "555-521-8224", "LAT": 19.4342, "LON": -99.1385},
        {"ESTADO": "CDMX", "SUCURSAL": "CORDOBA", "TEL": "551-102-2050 / 555-080-0095", "LAT": 19.4201, "LON": -99.1611},
        {"ESTADO": "CDMX", "SUCURSAL": "LINDAVISTA", "TEL": "Sin Teléfono Registrado", "LAT": 19.4912, "LON": -99.1215},
        {"ESTADO": "CDMX", "SUCURSAL": "LA VIGA", "TEL": "Sin Teléfono Registrado", "LAT": 19.3812, "LON": -99.1245},
        {"ESTADO": "CDMX", "SUCURSAL": "POLANCO", "TEL": "Sin Teléfono Registrado", "LAT": 19.4342, "LON": -99.1958},
        {"ESTADO": "CDMX", "SUCURSAL": "COAPA", "TEL": "555-920-3849 / 555-920-3829 / 555-528-5487", "LAT": 19.2988, "LON": -99.1212},
        {"ESTADO": "CDMX", "SUCURSAL": "AEROPUERTO", "TEL": "Sin Teléfono Registrado", "LAT": 19.4362, "LON": -99.0815},
        {"ESTADO": "CDMX", "SUCURSAL": "XOCHIMILCO", "TEL": "552-345-7579", "LAT": 19.2632, "LON": -99.1021},
        {"ESTADO": "DURANGO", "SUCURSAL": "DURANGO", "TEL": "618-836-0043 / 618-836-0066 / 618-818-1464", "LAT": 24.0277, "LON": -104.6532},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "CELAYA", "TEL": "461-615-1632 / 461-615-6880 / 461-614-9447", "LAT": 20.5218, "LON": -100.8140},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "IRAPUATO", "TEL": "462-624-0501 / 462-624-0565 / 462-624-1381", "LAT": 20.6742, "LON": -101.3545},
        {"ESTADO": "GUANAJUATO", "SUCURSAL": "LEON", "TEL": "477-718-0465 / 477-718-0468 / 477-717-2102", "LAT": 21.1226, "LON": -101.6807},
        {"ESTADO": "GUERRERO", "SUCURSAL": "ACAPULCO", "TEL": "744-484-1566 / 744-484-1729", "LAT": 16.8531, "LON": -99.8237},
        {"ESTADO": "HIDALGO", "SUCURSAL": "PACHUCA", "TEL": "771-719-6773 / 771-719-7292", "LAT": 20.1011, "LON": -98.7591},
        {"ESTADO": "JALISCO", "SUCURSAL": "GUADALAJARA", "TEL": "333-827-1396 / 333-826-1965 / 333-825-6388", "LAT": 20.6597, "LON": -103.3496},
        {"ESTADO": "JALISCO", "SUCURSAL": "PUERTO VALLARTA", "TEL": "322-225-5474 / 322-225-9725", "LAT": 20.6534, "LON": -105.2253},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "CUAUTITLAN", "TEL": "Sin Teléfono Registrado", "LAT": 19.6698, "LON": -99.1764},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "METEPEC", "TEL": "722-223-4999 / 722-212-4520", "LAT": 19.2555, "LON": -99.6048},
        {"ESTADO": "EDO. MEXICO", "SUCURSAL": "SATELITE", "TEL": "555-572-1252 / 555-572-1293 / 555-393-9493", "LAT": 19.5115, "LON": -99.2312},
        {"ESTADO": "MICHOACAN", "SUCURSAL": "MORELIA", "TEL": "443-324-6829 / 443-315-9160", "LAT": 19.7060, "LON": -101.1950},
        {"ESTADO": "MORELOS", "SUCURSAL": "CUERNAVACA", "TEL": "777-314-1524 / 777-314-1275", "LAT": 18.9242, "LON": -99.2216},
        {"ESTADO": "NAYARIT", "SUCURSAL": "TEPIC", "TEL": "311-129-4378 / 311-129-3458", "LAT": 21.5039, "LON": -104.8946},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "MONTERREY", "TEL": "818-340-2780", "LAT": 25.6866, "LON": -100.3161},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "ALLENDE", "TEL": "826-268-6768", "LAT": 25.2811, "LON": -100.0212},
        {"ESTADO": "NUEVO LEON", "SUCURSAL": "MONTERREY METROPOLITANA", "TEL": "Sin Teléfono Registrado", "LAT": 25.6714, "LON": -100.3090},
        {"ESTADO": "OAXACA", "SUCURSAL": "OAXACA", "TEL": "951-132-5693 / 951-132-6879", "LAT": 17.0732, "LON": -96.7266},
        {"ESTADO": "PUEBLA", "SUCURSAL": "PUEBLA", "TEL": "222-240-0611 / 222-240-0775 / 222-237-6093", "LAT": 19.0414, "LON": -98.2063},
        {"ESTADO": "QUERETARO", "SUCURSAL": "QUERETARO", "TEL": "442-220-7777 / 442-226-3173", "LAT": 20.5888, "LON": -100.3899},
        {"ESTADO": "QUINTANA ROO", "SUCURSAL": "CANCUN", "TEL": "998-883-9243 / 998-883-9519", "LAT": 21.1619, "LON": -86.8515},
        {"ESTADO": "QUINTANA ROO", "SUCURSAL": "PLAYA DEL CARMEN", "TEL": "984-879-4340 / 984-879-3885", "LAT": 20.6296, "LON": -87.0739},
        {"ESTADO": "SAN LUIS POTOSI", "SUCURSAL": "SAN LUIS POTOSI", "TEL": "444-812-0187 / 444-833-3993", "LAT": 22.1565, "LON": -100.9855},
        {"ESTADO": "SINALOA", "SUCURSAL": "CULIACAN", "TEL": "667-714-8714 / 667-761-2460", "LAT": 24.8054, "LON": -107.3940},
        {"ESTADO": "SINALOA", "SUCURSAL": "MAZATLAN", "TEL": "669-118-4250 / 669-118-4257", "LAT": 23.2494, "LON": -106.4111},
        {"ESTADO": "SINALOA", "SUCURSAL": "LOS MOCHIS", "TEL": "Sin Teléfono Registrado", "LAT": 25.7904, "LON": -108.9858},
        {"ESTADO": "SONORA", "SUCURSAL": "CD. OBREGON", "TEL": "644-414-8984 / 664-414-8638", "LAT": 27.4828, "LON": -109.9304},
        {"ESTADO": "SONORA", "SUCURSAL": "HERMOSILLO", "TEL": "662-217-1136 / 662-213-4943", "LAT": 29.0729, "LON": -110.9559},
        {"ESTADO": "SONORA", "SUCURSAL": "NOGALES", "TEL": "631-314-8491 / 631-314-9886", "LAT": 31.3012, "LON": -110.9381},
        {"ESTADO": "TABASCO", "SUCURSAL": "VILLA HERMOSA", "TEL": "993-316-5612 / 993-316-5595", "LAT": 17.9892, "LON": -92.9475},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "MATAMOROS", "TEL": "868-149-1299 / 868-812-1676", "LAT": 25.8690, "LON": -97.5027},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "REYNOSA", "TEL": "899-925-5141 / 899-925-5140", "LAT": 26.0806, "LON": -98.2883},
        {"ESTADO": "TAMAULIPAS", "SUCURSAL": "TAMPICO", "TEL": "833-224-7515 / 833-224-7517", "LAT": 22.2562, "LON": -97.8659},
