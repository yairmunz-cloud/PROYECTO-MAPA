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
    .badge-orange { padding: 6px; background: rgba(230,126,34,0.12); border-left: 5px solid #e67e22; border-radius: 4px; color: #d35400; font-size: 0.85rem; font-weight: bold; }
    .badge-red { padding: 6px; background: rgba(231,76,60,0.12); border-left: 5px solid #e74c3c; border-radius: 4px; color: #c0392b; font-size: 0.85rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS
def cargar_datos_desde_sheets():
    url_maestra = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90/pub?output=csv"
    df_sheets = pd.read_csv(url_maestra)
    
    # Limpiamos espacios y estandarizamos temporalmente los encabezados a MAYÚSCULAS
    df_sheets.columns = df_sheets.columns.str.strip().str.upper()
    return df_sheets

try:
    df = cargar_datos_desde_sheets()
except Exception as e:
    st.error(f"Error crítico al conectar con Google Sheets: {e}")
    st.stop()

# --- BLINDAJE AVANZADO: IDENTIFICADOR AUTOMÁTICO DE COLUMNAS FLEXIBLE ---
# Buscamos las columnas reales del Excel basándonos en aproximación de palabras clave
col_est = None
col_suc = None
col_tel = None
col_rep = None
col_fec = None

for col in df.columns:
    if "ESTADO" in col or "EST" in col:
        col_est = col
    elif "SUCURSAL" in col or "SUC" in col:
        col_suc = col
    elif "TEL" in col or "LINEA" in col or "TELMEX" in col:
        col_tel = col
    elif "REP" in col or "INCIDENCIA" in col:
        col_rep = col
    elif "FECHA" in col or "FEC" in col:
        col_fec = col

# Si el identificador automático no encontró alguna columna, asignamos la primera disponible por seguridad
if not col_est: col_est = df.columns[0]
if not col_suc: col_suc = df.columns[1] if len(df.columns) > 1 else df.columns[0]
if not col_tel: col_tel = df.columns[2] if len(df.columns) > 2 else df.columns[0]
if not col_rep: col_rep = df.columns[3] if len(df.columns) > 3 else df.columns[0]
if not col_fec: col_fec = df.columns[4] if len(df.columns) > 4 else df.columns[0]

# Rellenar los estados hacia abajo automáticamente (Corrige celdas combinadas vacías)
df[col_est] = df[col_est].ffill()

# Helper para validar si una sucursal tiene un reporte activo
def tiene_reporte_activo(valor_reporte):
    if pd.isna(valor_reporte):
        return False
    val = str(valor_reporte).strip().lower()
    if val in ["", "0", "sin reporte", "none", "nan", "vacio"]:
        return False
    return True

# --- LÓGICA DE CONTROL DE ESTADOS DE SELECCIÓN ---
if "estado_seleccionado" not in st.session_state:
    lista_inicial = sorted(df[col_est].dropna().unique())
    st.session_state.estado_seleccionado = lista_inicial[0] if lista_inicial else ""

# --- FILA SUPERIOR: MURO DE ALERTAS RÁPIDAS ---
st.markdown("### ⚠️ Sucursales con Reporte Activo (Clic para acceso rápido)")

# Escaneamos la columna identificada de reportes
df_con_reporte = df[df[col_rep].apply(tiene_reporte_activo)]

if not df_con_reporte.empty:
    columnas_botones = st.columns(min(len(df_con_reporte), 7))
    for i, (_, fila_rep) in enumerate(df_con_reporte.iterrows()):
        col_idx = i % 7
        with columnas_botones[col_idx]:
            if st.button(f"🚨 {fila_rep[col_suc]}", key=f"btn_{fila_rep[col_suc]}", use_container_width=True):
                st.session_state.estado_seleccionado = fila_rep[col_est]
                st.rerun()
else:
    st.success("🟢 No se registran reportes activos en ninguna sucursal de la República Mexicana.")

st.markdown("---")

# --- FILA MEDIA: BUSCADOR COMPACTO ---
lista_estados = sorted(df[col_est].dropna().unique())

try:
    default_index = lista_estados.index(st.session_state.estado_seleccionado)
except ValueError:
    default_index = 0
    
col_buscador, _ = st.columns([1, 2]) # Hace el buscador más pequeño usando proporciones de espacio
with col_buscador:
    estado_actual = st.selectbox(
        "🔍 Filtrar por Estado:",
        options=lista_estados,
        index=default_index,
        key="selector_estado_maestro"
    )
    st.session_state.estado_seleccionado = estado_actual

# --- FILA INFERIOR: CUADRÍCULA DE SUCURSALES (3 COLUMNAS) ---
df_resultado = df[df[col_est] == st.session_state.estado_seleccionado]

st.markdown(f"#### 📍 Monitoreo: {st.session_state.estado_seleccionado} ({len(df_resultado)} Sucursales)")

columnas_grilla = st.columns(3)

for idx, (_, fila) in enumerate(df_resultado.iterrows()):
    col_destino = idx % 3
    
    with columnas_grilla[col_destino]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="suc-title">🏢 {fila[col_suc]}</div>', unsafe_allow_html=True)
        
        # Procesar números telefónicos de la columna identificada
        tel_raw = str(fila[col_tel]).strip()
        if tel_raw == "" or tel_raw.lower() in ["nan", "none", "sin telefono"]:
            st.markdown('<div class="tel-item"><i>Sin líneas asignadas</i></div>', unsafe_allow_html=True)
        else:
            # Separación segura por renglones si vienen juntos o con diagonales
            lista_tels = tel_raw.replace("\r", "").replace(" / ", "\n").split("\n")
            for t in lista_tels:
                if t.strip():
                    st.markdown(f'<div class="tel-item">• {t.strip()}</div>', unsafe_allow_html=True)
        
        # Procesar estatus del reporte de la columna identificada
        rep_raw = str(fila[col_rep]).strip().lower()
        
        if not tiene_reporte_activo(rep_raw):
            st.markdown('<div class="badge-normal">🟢 Operando Normal (Sin Incidencias)</div>', unsafe_allow_html=True)
        else:
            rep_actual = str(fila[col_rep]).strip()
            fecha_raw = str(fila[col_fec]).strip() if col_fec in df.columns else ""
            
            if fecha_raw == "" or fecha_raw.lower() in ["nan", "none", "vacia"]:
                st.markdown(f'<div class="badge-yellow">🟡 Reporte: {rep_actual}<br>Levantamiento pendiente</div>', unsafe_allow_html=True)
            else:
                try:
                    fecha_dt = pd.to_datetime(fecha_raw, errors='coerce')
                    if pd.isna(fecha_dt):
                        st.markdown(f'<div class="badge-yellow">🟡 Reporte: {rep_actual}<br>Fecha con formato incorrecto</div>', unsafe_allow_html=True)
                    else:
                        dias_atraso = (datetime.now() - fecha_dt).days
                        if dias_atraso <= 3:
                            st.markdown(f'<div class="badge-yellow">🟡 Alerta Inicial ({dias_atraso} días)<br>Rep: {rep_actual} | {fecha_dt.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
                        elif dias_atraso <= 5:
                            st.markdown(f'<div class="badge-orange">🟠 Alerta Intermedia ({dias_atraso} días)<br>Rep: {rep_actual} | {fecha_dt.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="badge-red">🔴 Alerta Crítica ({dias_atraso} días)<br>Rep: {rep_actual} | {fecha_dt.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
                except:
                    st.markdown(f'<div class="badge-yellow">🟡 Reporte: {rep_actual}<br>Error al calcular fecha</div>', unsafe_allow_html=True)
                    
        st.markdown('</div>', unsafe_allow_html=True)


