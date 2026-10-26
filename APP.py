import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Consulta BDSUCRSALES", layout="wide")
st.title("🏢 Consulta de Sucursales y Líneas Telefónicas")
st.markdown("Los datos se leen directamente en tiempo real desde tu archivo **BDSUCRSALES** en Google Sheets.")

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS
def cargar_datos_desde_sheets():
    # Enlace publicado directamente en formato CSV (.csv)
    url_maestra = "https://google.com"
    
    # Lectura del archivo en la nube
    df_sheets = pd.read_csv(url_maestra)
    
    # BLINDAJE 1: Limpiamos espacios e igualamos los encabezados a MAYÚSCULAS para evitar caídas
    df_sheets.columns = df_sheets.columns.str.strip().str.upper()
    
    # Rellenar los estados hacia abajo de forma automática (Corrige celdas combinadas vacías)
    if 'ESTADO' in df_sheets.columns:
        df_sheets['ESTADO'] = df_sheets['ESTADO'].ffill()
    
    return df_sheets

# Ejecución forzada de la base de datos
try:
    df = cargar_datos_desde_sheets()
except Exception as e:
    st.error(f"Error crítico al conectar con Google Sheets: {e}")
    st.info("Por favor, asegúrate de que el enlace de la línea 13 sea el correcto y termine en output=csv.")
    st.stop()

st.markdown("---")

# BLINDAJE 2: Verificación estricta de estructura para mitigar pantallas en blanco o con código basura
columnas_validas = ['ESTADO', 'SUCURSAL', 'NO. REPORTE']
errores_encabezado = [col for col in columnas_validas if col not in df.columns]

if not errores_encabezado:
    
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
    
    # Identificar la columna de teléfonos de manera flexible
    col_tel = 'LINEA TELMEX'
    if 'LINEA TELMEX' not in df.columns:
        for col in df.columns:
            if 'TEL' in col or 'LINEA' in col:
                col_tel = col
                break
                
    # Recorremos todas las sucursales de arriba a abajo
    for idx, fila in df_resultado.iterrows():
        with st.container():
            # Dividimos la sección en 2 bloques limpios en paralelo
            col_izq, col_der = st.columns(2)
            
            with col_izq:
                st.markdown(f"### 🏢 Sucursal: {fila['SUCURSAL']}")
                st.markdown("**📞 Líneas Telmex asignadas:**")
                
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
                
                rep_raw = str(fila['NO. REPORTE']).strip().lower()
                
                # REGLA 1: Si la celda está vacía, es 0, o dice sin reporte -> MARGEN VERDE
                if rep_raw == "" or rep_raw in ["nan", "none", "0", "sin reporte", "vacio"]:
                    st.success("🟢 **Sin Reporte Activo**\n\nEsta sucursal opera con normalidad y no registra incidencias.")
                
                # REGLA 2: Si tiene un reporte, calculamos el atraso contra la fecha actual
                else:
                    rep_actual = str(fila['NO. REPORTE']).strip()
                    fecha_raw = str(fila['FECHA DE REPORTE']).strip() if 'FECHA DE REPORTE' in df.columns else ""
                    
                    if fecha_raw == "" or fecha_raw.lower() in ["nan", "none", "vacia"]:
                        st.warning(f"🟡 **Reporte Registrado: {rep_actual}**\n\nFecha de levantamiento pendiente de capturar en Google Sheets.")
                    else:
                        try:
                            # Convertimos la fecha de la celda de forma flexible
                            fecha_rep = pd.to_datetime(fecha_raw, errors='coerce')
                            
                            if pd.isna(fecha_rep):
                                st.warning(f"🟡 **Reporte Registrado: {rep_actual}**\n\nFormato de fecha no válido en el Excel. Escríbela como AAAA-MM-DD.")
                            else:
                                # Restamos la fecha actual menos la fecha del reporte
                                hoy = datetime.now()
                                dias_atraso = (hoy - fecha_rep).days
                                
                                # Clasificación estricta por rangos de días
                                if dias_atraso <= 3:
                                    st.warning(f"🟡 **Alerta Inicial (Atraso: {dias_atraso} días)**\n\n**No. Reporte:** {rep_actual}\n\n**Fecha Levantamiento:** {fecha_rep.strftime('%Y-%m-%d')}")
                                elif dias_atraso <= 5:
                                    st.markdown(f"""
                                    <div style='padding:12px; background-color:rgba(230,126,34,0.15); border-left:5px solid #e67e22; border-radius:4px; color:#d35400; font-weight:bold;'>
                                        <h3>🟠 Alerta Intermedia</h3>
                                        <b>Tiempo transcurrido:</b> {dias_atraso} días de atraso<br><br>
                                        <b>No. Reporte:</b> {rep_actual}<br>
                                        <b>Fecha Levantamiento:</b> {fecha_rep.strftime('%Y-%m-%d')}
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.error(f"🔴 **Alerta Crítica (Atraso: {dias_atraso} días)**\n\n**No. Reporte:** {rep_actual}\n\n**Fecha Levantamiento:** {fecha_rep.strftime('%Y-%m-%d')}")
                        except:
                            st.warning(f"🟡 **Reporte Registrado: {rep_actual}**\n\nVerifica el formato de la fecha en el Excel.")
                            
            st.markdown("---")
else:
    st.error("⚠️ El enlace copiado desde Google Sheets no es correcto.")
    st.info("El sistema está leyendo el código de diseño de la página de Google en lugar de tus datos limpios.")
    st.markdown("""
    **Cómo solucionarlo en 1 minuto:**
    1. Abre tu Google Sheets **BDSUCRSALES**.
    2. Ve a **Archivo** > **Compartir** > **Publicar en la web**.
    3. En el desplegable que dice *Página Web*, cámbialo obligatoriamente por **Valores separados por comas (.csv)**.
    4. Copia ese nuevo enlace y pégalo en la línea 13 de tu GitHub reemplazando el anterior.
    """)

