import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Consulta BDSUCRSALES", layout="wide")
st.title("🏢 Consulta de Sucursales y Líneas Telefónicas")
st.markdown("Los datos se leen directamente en tiempo real desde tu archivo **BDSUCRSALES** en Google Sheets.")

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS (SIN CACHÉ VIEJA)
def cargar_datos_desde_sheets():
    # Enlace maestro directo en formato CSV
    url_maestra = "https://google.com"
    
    # Lectura forzada del archivo en la nube
    df_sheets = pd.read_csv(url_maestra)
    
    # Rellenar los estados hacia abajo automáticamente (Corrige celdas combinadas vacías)
    df_sheets['ESTADO'] = df_sheets['ESTADO'].ffill()
    
    return df_sheets

# Ejecución directa y obligatoria de la base de datos
try:
    df = cargar_datos_desde_sheets()
    st.success("🔄 Conexión en vivo y exitosa con el archivo BDSUCRSALES.")
except Exception as e:
    st.error(f"Error crítico al conectar con Google Sheets: {e}")
    st.info("Por favor, asegúrate de que el archivo siga publicado en la web en formato CSV.")
    st.stop()

st.markdown("---")

# 3. INTERFAZ: BARRA DE BÚSQUEDA POR ESTADO
lista_estados = sorted(df['ESTADO'].dropna().unique())
estado_seleccionado = st.selectbox(
    "🔍 Selecciona un Estado para consultar todas sus sucursales:",
    options=lista_estados,
    index=0
)

st.markdown("---")

# 4. FILTRADO Y DESPLIEGUE EN PANTALLA
df_resultado = df[df['ESTADO'] == estado_seleccionado]

st.subheader(f"📍 Sucursales registradas en: {estado_seleccionado}")

# Recorremos todas las sucursales del estado seleccionado de arriba a abajo
for idx, fila in df_resultado.iterrows():
    with st.container():
        st.markdown(f"### 🏢 Sucursal: {fila['SUCURSAL']}")
        st.markdown("**📞 Líneas Telmex asignadas:**")
        
        # Extraemos la columna de teléfonos y limpiamos los saltos de línea del Excel
        tel_raw = str(fila['LINEA TELMEX']).strip()
        
        if tel_raw == "" or tel_raw.lower() in ["nan", "none", "sin telefono"]:
            st.markdown("_Sin teléfono registrado_")
        else:
            # Separar los números por renglones limpios si vienen juntos con saltos de línea en la celda
            lista_telefonos = tel_raw.replace("\r", "").split("\n")
            for tel in lista_telefonos:
                if tel.strip():
                    st.markdown(f"• {tel.strip()}")
                    
        st.markdown("---")
