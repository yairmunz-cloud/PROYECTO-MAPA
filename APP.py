import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA ANCHA Y ESTILOS COMPACTOS (Glassmorphism)
st.set_page_config(page_title="Tablero BDSUCRSALES", layout="wide")

st.markdown("""
<style>
    /* Forzar que el contenedor principal use menos espacio superior */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 0rem !important; }
    
    /* Tarjetas compactas con efecto cristal traslúcido */
    .glass-card {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 14px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 10px;
        height: 100%;
    }
    
    /* Tamaños de texto ajustados para evitar scroll */
    .suc-title { font-size: 1.1rem !important; font-weight: bold; margin-bottom: 4px; color: #1e293b; }
    .tel-item { font-size: 0.9rem !important; margin: 2px 0; color: #475569; }
    
    /* Semáforos de alertas compactos */
    .badge-normal { padding: 6px; background: rgba(46,204,113,0.12); border-left: 4px solid #2ecc71; border-radius: 4px; color: #27ae60; font-size: 0.85rem; font-weight: bold; }
    .badge-yellow { padding: 6px; background: rgba(241,196,15,0.12); border-left: 4px solid #f1c40f; border-radius: 4px; color: #b7950b; font-size: 0.85rem; font-weight: bold; }
    .badge-orange { padding: 6px; background: rgba(230,126,34,0.12); border-left: 5px solid #e67e22; border-radius: 4px; color: #d35400; font-weight: bold; }
    .badge-red { padding: 6px; background: rgba(231,76,60,0.12); border-left: 5px solid #e74c3c; border-radius: 4px; color: #c0392b; font-size: 0.85rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS
def cargar_datos_desde_sheets():
    url_maestra = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90/pub?output=csv"
    df_sheets = pd.read_csv(url_maestra)
    
    # Estandarizamos los encabezados quitando espacios y forzando mayúsculas
    df_sheets.columns = df_sheets.columns.str.strip().str.upper()
    return df_sheets

try:
    df = cargar_datos_desde_sheets()
except Exception as e:
    st.error(f"Error crítico al conectar con Google Sheets: {e}")
    st.stop()

# --- DETECTOR ESTRICTO DE COLUMNAS PARA EVITAR CRUCES ---
col_est = 'ESTADO' if 'ESTADO' in df.columns else df.columns[0]
col_suc = 'SUCURSAL' if 'SUCURSAL' in df.columns else df.columns[1]
col_tel = 'LINEA TELMEX' if 'LINEA TELMEX' in df.columns else df.columns[2]

# Buscador de la columna No. REPORTE evitando confundirse con la Fecha
col_rep = None
for col in df.columns:
    if "NO. REPORTE" in col or "NO REPORTE" in col or col == "REPORTE":
        col_rep = col
        break
if not col_rep:
    for col in df.columns:
        if "REP" in col and "FEC" not in col:
            col_rep = col
            break

# Buscador de la columna Fecha de Reporte
col_fec = None
for col in df.columns:
    if "FECHA" in col or "FEC" in col:
        col_fec = col
        break

# Rellenar estados por celdas combinadas vacías
df[col_est] = df[col_est].ffill()

# Helper lógico de reportes activos
def tiene_reporte_activo(valor_reporte):
    if pd.isna(valor_reporte):
        return False
    val = str(valor_reporte).strip().lower()
    if val in ["", "0", "sin reporte", "none", "nan", "vacio"]:
        return False
    return True

# --- INICIALIZAR CANDADO DE MEMORIA PERMANENTE ---
lista_estados = sorted(df[col_est].dropna().unique())

# Si es la primera vez que se abre la app, ponemos por defecto el primer estado de la lista
if "candado_estado" not in st.session_state:
    st.session_state["candado_estado"] = lista_estados[0]

# --- FILA SUPERIOR: MURO DE ALERTAS RÁPIDAS (BOTONES) ---
st.markdown("### ⚠️ Sucursales con Reporte Activo (Clic para acceso rápido)")

df_con_reporte = df[df[col_rep].apply(tiene_reporte_activo)]

if not df_con_reporte.empty:
    columnas_botones = st.columns(min(len(df_con_reporte), 7))
    for i, (_, fila_rep) in enumerate(df_con_reporte.iterrows()):
        col_idx = i % 7
        with columnas_botones[col_idx]:
            # Guardamos de forma limpia los valores en variables
            boton_sucursal = str(fila_rep[col_suc])
            boton_estado = str(fila_rep[col_est])
            
            if st.button(f"🚨 {boton_sucursal}", key=f"btn_{boton_sucursal}_{i}", use_container_width=True):
                # AL DAR CLIC: Forzamos al candado de memoria a tomar el estado de esta sucursal
                st.session_state["candado_estado"] = boton_estado
                st.rerun()
else:
    st.success("🟢 No se registran reportes activos en ninguna sucursal de la República Mexicana.")

st.markdown("---")

# --- FILA MEDIA: BUSCADOR COMPACTO MODIFICADO ---
try:
    default_index = lista_estados.index(st.session_state["candado_estado"])
except ValueError:
    default_index = 0
    
col_buscador, _ = st.columns([1, 2]) # Hace el buscador visualmente más pequeño en la pantalla
with col_buscador:
    # El selector lee y escribe directamente sobre el candado de memoria permanente
    estado_actual = st.selectbox(
        "🔍 Filtrar por Estado:",
        options=lista_estados,
        index=default_index,
        key="selector_estado_maestro"
    )
    st.session_state["candado_estado"] = estado_actual

# --- FILA INFERIOR: CUADRÍCULA DE SUCURSALES (3 COLUMNAS MÁXIMO) ---
df_resultado = df[df[col_est] == st.session_state["candado_estado"]]

st.markdown(f"#### 📍 Monitoreo: {st.session_state['candado_estado']} ({len(df_resultado)} Sucursales)")

columnas_grilla = st.columns(3)

for idx, (_, fila) in enumerate(df_resultado.iterrows()):
    col_destino = idx % 3
    
    with columnas_grilla[col_destino]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="suc-title">🏢 {fila[col_suc]}</div>', unsafe_allow_html=True)
        
        # 1. Despliegue de Líneas Telefónicas
        tel_raw = str(fila[col_tel]).strip()
        if tel_raw == "" or tel_raw.lower() in ["nan", "none", "sin telefono"]:
            st.markdown('<div class="tel-item"><i>Sin líneas asignadas</i></div>', unsafe_allow_html=True)
        else:
            lista_tels = tel_raw.replace("\r", "").replace(" / ", "\n").split("\n")
            for t in lista_tels:
                if t.strip():
                    st.markdown(f'<div class="tel-item">• {t.strip()}</div>', unsafe_allow_html=True)
        
        # 2. Despliegue de Estatus de Incidencias y Semáforos
        rep_raw = str(fila[col_rep]).strip()
        
        if not tiene_reporte_activo(rep_raw):
            st.markdown('<div class="badge-normal">🟢 Operando Normal (Sin Incidencias)</div>', unsafe_allow_html=True)
        else:
            rep_actual = str(fila[col_rep]).strip()
            fecha_raw = str(fila[col_fec]).strip() if col_fec and col_fec in df.columns else ""
            
            if fecha_raw == "" or fecha_raw.lower() in ["nan", "none", "vacia"]:
                st.markdown(f'<div class="badge-yellow">🟡 Reporte: {rep_actual}<br>Levantamiento pendiente</div>', unsafe_allow_html=True)
            else:
                try:
                    fecha_dt = pd.to_datetime(fecha_raw, errors='coerce')
                    if pd.isna(fecha_dt):
                        st.markdown(f'<div class="badge-yellow">🟡 Reporte: {rep_actual}<br>Fecha con formato incorrecto</div>', unsafe_allow_html=True)
                    else:
                        dias_atraso = (datetime.now() - fecha_dt).days
                        
                        # Clasificación de alertas compactas por rangos de días en la tarjeta
                        if dias_atraso <= 3:
                            st.markdown(f'<div class="badge-yellow">🟡 Alerta Inicial ({dias_atraso} días)<br>No. Reporte: {rep_actual} | {fecha_dt.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
                        elif dias_atraso <= 5:
                            st.markdown(f'<div class="badge-orange">🟠 Alerta Intermedia ({dias_atraso} días)<br>No. Reporte: {rep_actual} | {fecha_dt.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="badge-red">🔴 Alerta Crítica ({dias_atraso} días)<br>No. Reporte: {rep_actual} | {fecha_dt.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
                except:
                    st.markdown(f'<div class="badge-yellow">🟡 Reporte: {rep_actual}<br>Error al calcular fecha</div>', unsafe_allow_html=True)
                    
        st.markdown('</div>', unsafe_allow_html=True)


