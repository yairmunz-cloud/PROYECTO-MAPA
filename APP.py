import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA ANCHA Y BLINDAJE CSS ULTRA-COMPACTO
st.set_page_config(page_title="Tablero BDSUCRSALES", layout="wide")

st.markdown("""
<style>
    /* Forzar compresión absoluta de márgenes en toda la pantalla con espacio para el título */
    .block-container { padding-top: 2rem !important; padding-bottom: 0rem !important; margin-top: 0px !important; }
    h1 { font-size: 1.8rem !important; padding-top: 5px !important; margin-top: 0px !important; margin-bottom: 12px !important; color: #0f172a !important; }
    h3 { font-size: 1.1rem !important; margin-top: 2px !important; margin-bottom: 2px !important; }
    h4 { font-size: 1.0rem !important; margin-top: 2px !important; margin-bottom: 2px !important; }
    hr { margin-top: 4px !important; margin-bottom: 4px !important; padding: 0px !important; }
    
    /* Espacio super reducido para los selectores de Streamlit */
    div[data-testid="stSelectbox"] { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    
    /* Tarjetas compactas Glassmorphism optimizadas para una sola hoja */
    .glass-card {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(6px);
        border-radius: 8px;
        padding: 12px;
        border: 1px solid rgba(0, 0, 0, 0.12);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        margin-top: 6px;
        margin-bottom: 6px;
        display: block !important;
    }
    
    /* Contenedor en línea para alinear Nombre y Estatus */
    .card-header {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 6px;
        border-bottom: 1px solid rgba(0,0,0,0.06);
        padding-bottom: 6px;
    }
    
    .suc-title { font-size: 1.0rem !important; font-weight: bold; color: #1e293b; }
    .tel-container { margin-top: 6px; display: block !important; }
    .tel-item { font-size: 0.85rem !important; margin: 3px 0 !important; color: #334155; line-height: 1.2 !important; font-weight: 500; }
    
    /* Semáforos de alertas ultra-pequeños adaptados para modo horizontal */
    .badge-inline {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
        display: inline-block;
    }
    .badge-normal { background: rgba(46,204,113,0.15); border: 1px solid #2ecc71; color: #1e7e34; }
    .badge-yellow { background: rgba(241,196,15,0.15); border: 1px solid #f1c40f; color: #9a7d0a; }
    .badge-orange { background: rgba(230,126,34,0.15); border: 1px solid #e67e22; color: #b75306; }
    .badge-red { background: rgba(231,76,60,0.15); border: 1px solid #e74c3c; color: #a93226; }
</style>
""", unsafe_allow_html=True)

# 2. FUNCIÓN CONECTADA EN VIVO A GOOGLE SHEETS
def cargar_datos_desde_sheets():
    url_maestra = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90/pub?output=csv"
    df_sheets = pd.read_csv(url_maestra)
    df_sheets.columns = df_sheets.columns.str.strip().str.upper()
    return df_sheets

try:
    df = cargar_datos_desde_sheets()
except Exception as e:
    st.error(f"Error crítico: {e}")
    st.stop()

# --- RECONOCEDOR DE COLUMNAS MEJORADO Y SEGURO ---
col_est = next((c for c in df.columns if 'ESTADO' in c or 'EDO' in c), df.columns)
col_suc = next((c for c in df.columns if 'SUCURSAL' in c or 'SUC' in c or 'SITIO' in c), df.columns)
col_tel = next((c for c in df.columns if 'TELMEX' in c or 'TEL' in c or 'LINEA' in c), df.columns)

col_rep = None
for col in df.columns:
    if "NO. REPORTE" in col or "NO REPORTE" in col or col == "REPORTE":
        col_rep = col
        break
if not col_rep:
    col_rep = next((c for c in df.columns if "REP" in c and "FEC" not in c), None)

col_fec = next((c for c in df.columns if "FECHA" in c or "FEC" in c), None)

# Limpieza absoluta de textos en las columnas clave para evitar fallas de comparación
df[col_est] = df[col_est].ffill().astype(str).str.strip()
df[col_suc] = df[col_suc].astype(str).str.strip()

# Helper lógico de reportes activos
def tiene_reporte_activo(valor_reporte):
    if pd.isna(valor_reporte):
        return False
    val = str(valor_reporte).strip().lower()
    if val in ["", "0", "0.0", "sin reporte", "none", "nan", "vacio"]:
        return False
    return True

# Helper para limpiar los decimales .0 de los IDs de reporte
def limpiar_reporte_id(valor_reporte):
    texto = str(valor_reporte).strip()
    if texto.endswith('.0'):
        return texto[:-2]
    return texto

# --- LISTA GLOBAL DE ESTADOS ---
lista_estados = sorted(df[col_est].dropna().unique())

# --- VARIABLES DE CONTROL EN SESSION STATE ---
if "selector_estado_maestro" not in st.session_state:
    st.session_state["selector_estado_maestro"] = lista_estados if lista_estados else ""

if "sucursal_filtrada" not in st.session_state:
    st.session_state["sucursal_filtrada"] = None

# --- FUNCIONES CALLBACK DE NAVEGACIÓN ---
def cambiar_estado_callback(nuevo_estado, nueva_sucursal):
    st.session_state["selector_estado_maestro"] = nuevo_estado.strip()
    st.session_state["sucursal_filtrada"] = nueva_sucursal.strip()

def limpiar_filtro_sucursal_callback():
    st.session_state["sucursal_filtrada"] = None

# --- FILA 1: FILTRO POR ESTADO COMPACTO ---
st.title("🏢 Consulta de Sucursales y Líneas Telefónicas")

# CORRECCIÓN EN ESTA LÍNEA: Se asignan las proporciones explícitas de espacio para evitar el TypeError
col_buscador, col_espacio_libre = st.columns([1, 2])
with col_buscador:
    idx_actual = 0
    if st.session_state["selector_estado_maestro"] in lista_estados:
        idx_actual = lista_estados.index(st.session_state["selector_estado_maestro"])

    estado_actual = st.selectbox(
        "🔍 Filtrar por Estado:",
        options=lista_estados,
        index=idx_actual,
        key="selector_estado_maestro",
        on_change=limpiar_filtro_sucursal_callback
    )

st.markdown("<hr>", unsafe_allow_html=True)

# --- FILA 2: ACCESOS RÁPIDOS POR ALERTA ACTIVA ---
st.markdown("### ⚠️ Sucursales con Reporte Activo (Clic para cambiar de Estado)")

df_con_reporte = df[df[col_rep].apply(tiene_reporte_activo)] if col_rep else pd.DataFrame()

if not df_con_reporte.empty:
    columnas_botones = st.columns(min(len(df_con_reporte), 8))
    for i, (_, fila_rep) in enumerate(df_con_reporte.iterrows()):
        col_idx = i % 8
        with columnas_botones[col_idx]:
            btn_suc = str(fila_rep[col_suc]).strip()
            btn_est = str(fila_rep[col_est]).strip()
            
            st.button(
                f"🚨 {btn_suc}", 
                key=f"btn_{btn_suc}_{i}", 
                use_container_width=True,
                on_click=cambiar_estado_callback,
                args=(btn_est, btn_suc)
            )
else:
    st.success("🟢 Sin reportes activos en la República Mexicana.")

st.markdown("<hr>", unsafe_allow_html=True)

# --- FILA 3: CUADRÍCULA DE TARJETAS ---
df_resultado = df[df[col_est] == st.session_state["selector_estado_maestro"]]

if st.session_state["sucursal_filtrada"] is not None:
    df_resultado = df_resultado[df_resultado[col_suc] == st.session_state["sucursal_filtrada"]]
    texto_monitoreo = f"#### 📍 Monitoreo Exclusivo Alerta: {st.session_state['sucursal_filtrada']} ({st.session_state['selector_estado_maestro']})"
else:
    texto_monitoreo = f"#### 📍 Monitoreo: {st.session_state['selector_estado_maestro']} ({len(df_resultado)} Sucursales)"

st.markdown(texto_monitoreo, unsafe_allow_html=True)

if not df_resultado.empty:
    columnas_grilla = st.columns(3)
    
    for idx, (_, fila) in enumerate(df_resultado.iterrows()):
        col_destino = idx % 3
        
        with columnas_grilla[col_destino]:
            badge_html = ""
            if col_rep:
                rep_raw = str(fila[col_rep]).strip()
                if not tiene_reporte_activo(rep_raw):
                    badge_html = '<span class="badge-inline badge-normal">🟢 OK</span>'
                else:
                    rep_actual = limpiar_reporte_id(rep_raw)
                    fecha_raw = str(fila[col_fec]).strip() if col_fec and col_fec in df.columns else ""
                    
                    if fecha_raw == "" or fecha_raw.lower() in ["nan", "none", "vacia"]:
                        badge_html = f'<span class="badge-inline badge-yellow">🟡 Rep: {rep_actual} | Fecha pend.</span>'
                    else:
                        fecha_dt = pd.to_datetime(fecha_raw, errors='coerce', dayfirst=True)
                        if pd.isna(fecha_dt):
                            badge_html = f'<span class="badge-inline badge-yellow">🟡 Rep: {rep_actual} | Formato inválido</span>'
                        else:
                            dias_atraso = (datetime.now() - fecha_dt).days
                            if dias_atraso <= 3:
                                badge_html = f'<span class="badge-inline badge-yellow">🟡 Rep: {rep_actual} | {dias_atraso} días</span>'
                            elif dias_atraso <= 7:
                                badge_html = f'<span class="badge-inline badge-orange">🟠 Rep: {rep_actual} | {dias_atraso} días</span>'
                            else:
                                badge_html = f'<span class="badge-inline badge-red">🔴 Rep: {rep_actual} | {dias_atraso} días</span>'
            else:
                badge_html = '<span class="badge-inline badge-normal">🟢 OK</span>'

            # Construcción segura de la lista de teléfonos como HTML integrado
            telefonos_html = ""
            tel_raw = str(fila[col_tel]).strip()
            if tel_raw == "" or tel_raw.lower() in ["nan", "none", "sin telefono"]:
                telefonos_html = '<div class="tel-item"><i>Sin líneas registradas</i></div>'
            else:
                lista_tels = tel_raw.replace("\r", "").replace(" / ", "\n").split("\n")

