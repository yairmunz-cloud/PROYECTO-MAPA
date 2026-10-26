import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Consulta BDSUCRSALES", layout="wide")
st.title("🏢 Consulta de Sucursales y Líneas Telefónicas")
st.markdown("Los datos se leen directamente en tiempo real desde el archivo **BDSUCRSALES** en Google Sheets.")

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS
@st.cache_data(ttl=600)  # El mapa se refresca solo cada 10 minutos si haces cambios en el Excel
def cargar_datos_desde_sheets():
    # PEGA AQUÍ TU LINK LARGO DE GOOGLE SHEETS QUE TERMINA EN output=csv
    "url_maestra = https://docs.google.com/spreadsheets/d/e/2PACX-1vQbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90/pub?output=csv"
    
    # Lectura automática de la nube
    df_sheets = pd.read_csv(url_maestra)
    
    # Corrección por si tu Excel tiene filas de Estado vacías (celdas combinadas)
    if 'ESTADO' in df_sheets.columns:
        df_sheets['ESTADO'] = df_sheets['ESTADO'].ffill()
        
    return df_sheets

# Control para evitar caídas de página si aún no se pega el enlace real
try:
    df = cargar_datos_desde_sheets()
    st.success("🔄 Conexión exitosa con la base de datos BDSUCRSALES.")
except:
    st.warning("⚠️ Esperando conexión con el enlace de Google Sheets. Mostrando datos de respaldo locales.")
    # Datos de respaldo por si el link no está listo
    df = pd.DataFrame([
        {"ESTADO": "CDMX", "SUCURSAL": "MATRIZ", "LINEA TELMEX": "559-177-5000 / 555-521-8224"},
        {"ESTADO": "BAJA CALIFORNIA NORTE", "SUCURSAL": "TIJUANA", "LINEA TELMEX": "664-684-1622 / 664-634-1504"}
    ])

st.markdown("---")

# 3. INTERFAZ: BARRA DE BÚSQUEDA POR ESTADO
if 'ESTADO' in df.columns:
    lista_estados = sorted(df['ESTADO'].dropna().unique())
    estado_seleccionado = st.selectbox(
        "🔍 Selecciona un Estado para consultar sus sucursales:",
        options=lista_estados,
        index=0
    )
    
    st.markdown("---")
    
    # 4. FILTRADO Y DESPLIEGUE EN PANTALLA
    # Buscamos en el archivo de Google Sheets las filas del estado elegido
    df_resultado = df[df['ESTADO'] == estado_seleccionado]
    
    st.subheader(f"📍 Sucursales operando en: {estado_seleccionado}")
    
    # Buscamos cuál es el nombre real de tu columna de teléfonos en el Sheets
    col_tel = 'LINEA TELMEX' if 'LINEA TELMEX' in df.columns else df.columns[2]
    col_suc = 'SUCURSAL' if 'SUCURSAL' in df.columns else df.columns[1]
    
    # Recorremos la lista completa hacia abajo
    for idx, fila in df_resultado.iterrows():
        with st.container():
            st.markdown(f"### 🏢 Sucursal: {fila[col_suc]}")
            st.markdown("**📞 Números Telefónicos:**")
            
            # Formateamos los números Telmex en renglones limpios hacia abajo
            telefonos = str(fila[col_tel]).replace("\n", " / ")
            for tel in telefonos.split(" / "):
                if tel.strip():
                    st.markdown(f"• {tel.strip()}")
            st.markdown("---")
else:
    st.error("No se encontró la columna 'ESTADO' en tu archivo de Google Sheets. Verifica los encabezados de tu Excel.")
