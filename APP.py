import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA ANCHA Y BLINDAJE CSS ULTRA-COMPACTO
st.set_page_config(page_title="Tablero BDSUCRSALES", layout="wide")

st.markdown("""
<style>
    /* Forzar compresión absoluta de márgenes en toda la pantalla */
    .block-container { padding-top: 0.5rem !important; padding-bottom: 0rem !important; margin-top: 0px !important; }
    h1 { font-size: 1.6rem !important; padding-top: 0px !important; margin-top: 0px !important; margin-bottom: 5px !important; }
    h3 { font-size: 1.1rem !important; margin-top: 2px !important; margin-bottom: 2px !important; }
    h4 { font-size: 1.0rem !important; margin-top: 2px !important; margin-bottom: 2px !important; }
    hr { margin-top: 4px !important; margin-bottom: 4px !important; padding: 0px !important; }
    
    /* Espacio super reducido para los selectores de Streamlit */
    div[data-testid="stSelectbox"] { margin-bottom: 0px !important; padding-bottom: 0px !important; }
    
    /* Tarjetas compactas Glassmorphism optimizadas para una sola hoja */
    .glass-card {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(6px);
        border-radius: 8px;
        padding: 10px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
        margin-top: 4px;
        margin-bottom: 4px;
    }
    
    .suc-title { font-size: 0.95rem !important; font-weight: bold; margin-bottom: 2px; color: #1e293b; }
    .tel-item { font-size: 0.8rem !important; margin: 1px 0 !important; color: #475569; line-height: 1.1 !important; }
    
    /* Semáforos de alertas ultra-pequeños */
    .badge-normal { padding: 4px 6px; background: rgba(46,204,113,0.12); border-left: 3px solid #2ecc71; border-radius: 3px; color: #27ae60; font-size: 0.75rem; font-weight: bold; margin-top: 4px; }
    .badge-yellow { padding: 4px 6px; background: rgba(241,196,15,0.12); border-left: 3px solid #f1c40f; border-radius: 3px; color: #b7950b; font-size: 0.75rem; font-weight: bold; margin-top: 4px; }
    .badge-orange { padding: 4px 6px; background: rgba(230,126,34,0.12); border-left: 3px solid #e67e22; border-radius: 3px; color: #d35400; font-size: 0.75rem; font-weight: bold; margin-top: 4px; }
    .badge-red { padding: 4px 6px; background: rgba(231,76,60,0.12); border-left: 3px solid #e74c3c; border-radius: 3px; color: #c0392b; font-size: 0.75rem; font-weight: bold; margin-top: 4px; }
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

# --- RECONOCEDOR DE COLUMNAS FLEXIBLE ---
col_est = 'ESTADO' if 'ESTADO' in df.columns else df.columns
col_suc = 'SUCURSAL' if 'SUCURSAL' in df.columns else df.columns
col_tel = 'LINEA TELMEX' if 'LINEA TELMEX' in df.columns else df.columns

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

col_fec = None
for col in df.columns:
    if "FECHA" in col or "FEC" in col:
        col_fec = col
        break

# Rellenar estados combinados vacíos
df[col_est] = df[col_est].ffill()

# Helper lógico de reportes activos
def tiene_reporte_activo(valor_reporte):
    if pd.isna(valor_reporte):
        return False
    val = str(valor_reporte).strip().lower()
    if val in ["", "0", "sin reporte", "none", "nan", "vacio"]:
        return False
    return True

# --- LISTA GLOBAL DE ESTADOS ---
lista_estados = sorted(df[col_est].dropna().unique())

# SOLUCIÓN DE NAVEGACIÓN: Inicializamos la clave del selectbox con el primer estado si no existe
if "selector_estado_maestro" not in st.session_state:
    st.session_state["selector_estado_maestro"] = lista_estados if lista_estados else ""

# --- FILA 1: FILTRO POR ESTADO COMPACTO ---
col_buscador, _ = st.columns() # Reducir ancho del input a 1/3
st.title("🏢 Consulta de Sucursales y Líneas Telefónicas")
with col_buscador:
    # Vinculado directamente a st.session_state["selector_estado_maestro"] para obligar el cambio
    estado_actual = st.selectbox(
        "🔍 Filtrar por Estado:",
        options=lista_estados,
        key="selector_estado_maestro"
    )

st.markdown("<hr>", unsafe_allow_html=True)

# --- FILA 2: ACCESOS RÁPIDOS POR ALERTA ACTIVA ---
st.markdown("### ⚠️ Sucursales con Reporte Activo (Clic para cambiar de Estado)")

df_con_reporte = df[df[col_rep].apply(tiene_reporte_activo)]

if not df_con_reporte.empty:
    # Grilla de botones pequeños (hasta 8 en una sola fila)
    columnas_botones = st.columns(min(len(df_con_reporte), 8))
    for i, (_, fila_rep) in enumerate(df_con_reporte.iterrows()):
        col_idx = i % 8
        with columnas_botones[col_idx]:
            btn_suc = str(fila_rep[col_suc])
            btn_est = str(fila_rep[col_est])
            
            # SOLUCIÓN AL CLIC: El botón altera directamente la clave asignada al selectbox y recarga
            if st.button(f"🚨 {btn_suc}", key=f"btn_{btn_suc}_{i}", use_container_width=True):
                st.session_state["selector_estado_maestro"] = btn_est
                st.rerun()
else:
    st.success("🟢 Sin reportes activos en la República Mexicana.")

st.markdown("<hr>", unsafe_allow_html=True)

# --- FILA 3: CUADRÍCULA DE TARJETAS EN 3 COLUMNAS MÁXIMO ---
df_resultado = df[df[col_est] == st.session_state["selector_estado_maestro"]]

st.markdown(f"#### 📍 Monitoreo: {st.session_state['selector_estado_maestro']} ({len(df_resultado)} Sucursales)")

columnas_grilla = st.columns(3)

for idx, (_, fila) in enumerate(df_resultado.iterrows()):
    col_destino = idx % 3
    
    with columnas_grilla[col_destino]:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="suc-title">🏢 {fila[col_suc]}</div>', unsafe_allow_html=True)
        
        # Despliegue de Teléfonos
        tel_raw = str(fila[col_tel]).strip()
        if tel_raw == "" or tel_raw.lower() in ["nan", "none", "sin telefono"]:
            st.markdown('<div class="tel-item"><i>Sin líneas registradas</i></div>', unsafe_allow_html=True)
        else:
            lista_tels = tel_raw.replace("\r", "").replace(" / ", "\n").split("\n")
            for t in lista_tels:
                if t.strip():
                    st.markdown(f'<div class="tel-item">• {t.strip()}</div>', unsafe_allow_html=True)
        
        # Despliegue de Alertas y su Número de Reporte correspondiente
        rep_raw = str(fila[col_rep]).strip()
        
        if not tiene_reporte_activo(rep_raw):
            st.markdown('<div class="badge-normal">🟢 Operando Normal (Sin Incidencias)</div>', unsafe_allow_html=True)
        else:
            rep_actual = str(fila[col_rep]).strip()
            fecha_raw = str(fila[col_fec]).strip() if col_fec and col_fec in df.columns else ""
            
            if fecha_raw == "" or fecha_raw.lower() in ["nan", "none", "vacia"]:
                st.markdown(f'<div class="badge-yellow">🟡 Rep: {rep_actual} | Fecha pendiente</div>', unsafe_allow_html=True)
            else:
                try:
                    fecha_dt = pd.to_datetime(fecha_raw, errors='coerce')
                    if pd.isna(fecha_dt):
                        st.markdown(f'<div class="badge-yellow">🟡 Rep: {rep_actual} | Formato de fecha inválido</div>', unsafe_allow_html=True)
                    else:
                        dias_atraso = (datetime.now() - fecha_dt).days
                        
                        # Alertas compactas mostrando de forma exitosa el Número del Reporte
                        if dias_atraso <= 3:
                            st.markdown(f'<div class="badge-yellow">🟡 Rango 1-3 ({dias_atraso}d) - Rep: {rep_actual} ({fecha_dt.strftime("%m-%d")})</div>', unsafe_allow_html=True)
                        elif dias_atraso <= 5:
                            st.markdown(f'<div class="badge-orange">🟠 Rango 3-5 ({dias_atraso}d) - Rep: {rep_actual} ({fecha_dt.strftime("%m-%d")})</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="badge-red">🔴 Rango 6+ ({dias_atraso}d) - Rep: {rep_actual} ({fecha_dt.strftime("%m-%d")})</div>', unsafe_allow_html=True)
                except:
                    st.markdown(f'<div class="badge-yellow">🟡 Rep: {rep_actual} | Error matemático fecha</div>', unsafe_allow_html=True)
                    
        st.markdown('</div>', unsafe_allow_html=True)

