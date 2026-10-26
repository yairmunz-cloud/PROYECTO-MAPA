import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Consulta BDSUCRSALES", layout="wide")
st.title("🏢 Consulta de Sucursales y Líneas Telefónicas")
st.markdown("Los datos se leen directamente en tiempo real desde tu archivo **BDSUCRSALES** en Google Sheets.")

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS
def cargar_datos_desde_sheets():
    # Enlace maestro directo en formato CSV
    url_maestra = "https://google.com"
    
    # Lectura forzada del archivo en la nube
    df_sheets = pd.read_csv(url_maestra)
    
    # BLINDAJE: Limpiamos espacios en blanco y convertimos todos los encabezados a MAYÚSCULAS automáticas
    df_sheets.columns = df_sheets.columns.str.strip().str.upper()
    
    # Rellenar los estados hacia abajo automáticamente (Corrige celdas combinadas vacías)
    if 'ESTADO' in df_sheets.columns:
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

# Verificar si las columnas principales existen tras la conversión a mayúsculas
if 'ESTADO' in df.columns and 'SUCURSAL' in df.columns:
    
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
    
    # Identificar la columna de teléfonos de manera flexible (por si se llama diferente)
    col_tel = 'LINEA TELMEX'
    if 'LINEA TELMEX' not in df.columns:
        # Si no se llama LINEA TELMEX, busca una columna que contenga la palabra TEL o LÍNEA
        for col in df.columns:
            if 'TEL' in col or 'LINEA' in col:
                col_tel = col
                break
    
    # Recorremos todas las sucursales del estado seleccionado de arriba a abajo
    for idx, fila in df_resultado.iterrows():
        with st.container():
            st.markdown(f"### 🏢 Sucursal: {fila['SUCURSAL']}")
            st.markdown("**📞 Líneas Telmex asignadas:**")
            
            # Extraemos los teléfonos de forma segura
            if col_tel in df.columns:
                tel_raw = str(fila[col_tel]).strip()
            else:
                tel_raw = "nan"
            
            if tel_raw == "" or tel_raw.lower() in ["nan", "none", "sin telefono"]:
                st.markdown("_Sin teléfono registrado_")
            else:
                # Separar los números por renglones limpios si vienen juntos con saltos de línea en la celda
                lista_telefonos = tel_raw.replace("\r", "").split("\n")
                for tel in lista_telefonos:
                    if tel.strip():
                        st.markdown(f"• {tel.strip()}")
                        
            st.markdown("---")
else:
    st.error("No se encontraron las columnas necesarias en tu archivo.")
    st.info(f"Las columnas detectadas en tu Google Sheets actualmente son: {list(df.columns)}")
    st.info("Asegúrate de que tu Excel tenga los encabezados escritos en la primera fila (Fila 1).")
