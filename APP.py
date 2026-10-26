import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Consulta BDSUCRSALES", layout="wide")
st.title("🏢 Consulta de Sucursales y Líneas Telefónicas")
st.markdown("Los datos se leen directamente en tiempo real desde tu archivo **BDSUCRSALES** en Google Sheets.")

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS
def cargar_datos_desde_sheets():
    # PEGA AQUÍ TU LINK LARGO DE GOOGLE SHEETS QUE TERMINA EN output=csv
    url_maestra = "https://google.com"
    
    # Lectura forzada del archivo en la nube
    df_sheets = pd.read_csv(url_maestra)
    
    # Limpiamos espacios en blanco y convertimos todos los encabezados a MAYÚSCULAS automáticas
    df_sheets.columns = df_sheets.columns.str.strip().str.upper()
    
    # Rellenar los estados hacia abajo automáticamente (Corrige celdas combinadas vacías)
    if 'ESTADO' in df_sheets.columns:
        df_sheets['ESTADO'] = df_sheets['ESTADO'].ffill()
    
    return df_sheets

# Ejecución de la base de datos en la nube
try:
    df = cargar_datos_desde_sheets()
    st.success("🔄 Conexión en vivo y exitosa con el archivo BDSUCRSALES.")
except Exception as e:
    st.error(f"Error crítico al conectar con Google Sheets: {e}")
    st.stop()

st.markdown("---")

# Verificar si las columnas necesarias existen en tu Google Sheets
if 'ESTADO' in df.columns and 'SUCURSAL' in df.columns and 'NO. REPORTE' in df.columns:
    
    # 3. INTERFAZ: BARRA DE BÚSQUEDA POR ESTADO
    lista_estados = sorted(df['ESTADO'].dropna().unique())
    estado_seleccionado = st.selectbox(
        "🔍 Selecciona un Estado para consultar todas sus sucursales:",
        options=lista_estados,
        index=0
    )
    
    st.markdown("---")
    
    # 4. FILTRADO DE LA INFORMACIÓN
    df_resultado = df[df['ESTADO'] == estado_seleccionado]
    
    st.subheader(f"📍 Sucursales registradas en: {estado_seleccionado}")
    
    # Identificar la columna de teléfonos de manera flexible
    col_tel = 'LINEA TELMEX'
    if 'LINEA TELMEX' not in df.columns:
        for col in df.columns:
            if 'TEL' in col or 'LINEA' in col:
                col_tel = col
                break
                
    # Recorremos todas las sucursales del estado seleccionado hacia abajo
    for idx, fila in df_resultado.iterrows():
        with st.container():
            # Creamos dos columnas internas para organizar la pantalla de forma ejecutiva
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                st.markdown(f"### 🏢 Sucursal: {fila['SUCURSAL']}")
                st.markdown("**📞 Líneas Telmex asignadas:**")
                
                # Extraemos y limpiamos los teléfonos de la celda
                tel_raw = str(fila[col_tel]).strip()
                if tel_raw == "" or tel_raw.lower() in ["nan", "none", "sin telefono"]:
                    st.markdown("_Sin teléfono registrado_")
                else:
                    lista_telefonos = tel_raw.replace("\r", "").split("\n")
                    for tel in lista_telefonos:
                        if tel.strip():
                            st.markdown(f"• {tel.strip()}")
            
            with col_der:
                st.markdown("### 📊 Estatus de Incidencia")
                
                # Leemos la celda del reporte limpiando espacios
                rep_raw = str(fila['NO. REPORTE']).strip().lower()
                
                # REGLA 1: Verificar si está vacío, es cero, o dice "sin reporte"
                if rep_raw == "" or rep_raw in ["nan", "none", "0", "sin reporte", "vacio"]:
                    # Indicador con margen verde nativo de Streamlit
                    st.success("🟢 **Sin Reporte Activo**\n\nLa sucursal opera con normalidad.")
                
                # REGLA 2: Si hay un reporte activo, calculamos el atraso con la fecha actual
                else:
                    rep_actual = str(fila['NO. REPORTE']).strip()
                    fecha_raw = str(fila['FECHA DE REPORTE']).strip()
                    
                    if fecha_raw == "" or fecha_raw.lower() in ["nan", "none", "vacia"]:
                        st.warning(f"🟡 **Reporte Registrado: {rep_actual}**\n\nFecha de levantamiento pendiente de capturar en el Excel.")
                    else:
                        try:
                            # Convertimos la fecha de tu Excel de manera flexible
                            # Soporta formatos comunes como AAAA-MM-DD o DD/MM/AAAA
                            fecha_rep = pd.to_datetime(fecha_raw, errors='coerce')
                            
                            if pd.isna(fecha_rep):
                                st.warning(f"🟡 **Reporte Registrado: {rep_actual}**\n\nFormato de fecha no reconocido. Escríbela como AAAA-MM-DD.")
                            else:
                                # Calcular diferencia de días contra hoy
                                hoy = datetime.now()
                                dias_atraso = (hoy - fecha_rep).days
                                
                                # Clasificación estricta de alertas por rangos de días
                                if dias_atraso <= 3:
                                    st.warning(f"🟡 **Alerta Inicial (Atraso: {dias_atraso} días)**\n\n**No. Reporte:** {rep_actual}\n\n**Fecha Levantamiento:** {fecha_rep.strftime('%Y-%m-%d')}")
                                elif dias_atraso <= 5:
                                    # Formato naranja usando un contenedor de advertencia visual extendido
                                    st.markdown(f"""
                                    <div style='padding:12px; background-color:rgba(230,126,34,0.15); border-left:5px solid #e67e22; border-radius:4px; color:#d35400; font-weight:bold;'>
                                        🟠 Alerta Intermedia (Atraso: {dias_retraso} días)<br><br>
                                        No. Reporte: {rep_actual}<br>
                                        Fecha Levantamiento: {fecha_rep.strftime('%Y-%m-%d')}
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.error(f"🔴 **Alerta Crítica (Atraso: {dias_atraso} días)**\n\n**No. Reporte:** {rep_actual}\n\n**Fecha Levantamiento:** {fecha_rep.strftime('%Y-%m-%d')}")
                        except:
                            st.warning(f"🟡 **Reporte Registrado: {rep_actual}**\n\nVerifica que el campo fecha sea válido en el Excel.")
                            
            st.markdown("---")
else:
    st.error("No se encontraron las columnas 'ESTADO', 'SUCURSAL' o 'No. REPORTE' en tu archivo.")
    st.info(f"Columnas detectadas actualmente: {list(df.columns)}")
