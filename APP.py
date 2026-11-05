import streamlit as st
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
    TZ_MX = ZoneInfo("America/Mexico_City")
except:
    TZ_MX = None

def now_mx():
    """Retorna datetime en hora CDMX, robusto para Streamlit Cloud (UTC)"""
    try:
        if TZ_MX:
            return datetime.now(TZ_MX)
    except:
        pass
    try:
        import pytz
        tz = pytz.timezone("America/Mexico_City")
        return datetime.now(tz)
    except:
        pass
    # Fallback manual: UTC-6 (CDMX sin horario de verano desde 2022)
    return datetime.utcnow() - timedelta(hours=6)

import pandas as pd
from datetime import datetime
import re
import time
import base64


st.set_page_config(page_title="REPORTES Y CONSULTAS SUCURSALES SEGUROS ATLAS", layout="wide", page_icon="🏢", initial_sidebar_state="expanded")



# --- SIDEBAR MENU PRINCIPAL - V42 GRIS ESTÉTICO FORZADO ---
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = "🏠 Reportes"

with st.sidebar:
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
        }
        section[data-testid="stSidebar"] input[type="radio"] {
            display: none !important;
            visibility: hidden !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 14px !important;
            display: flex !important;
            flex-direction: column !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            background: #ffffff !important;
            border: 1.5px solid #e2e8f0 !important;
            border-radius: 14px !important;
            padding: 18px 20px !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
            transition: all 0.25s ease !important;
            cursor: pointer !important;
            min-height: 52px !important;
            display: flex !important;
            align-items: center !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] > label p {
            font-size: 16px !important;
            font-weight: 500 !important;
            color: #475569 !important;
            line-height: 1.4 !important;
            letter-spacing: 0.15px !important;
            margin: 0 !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background: #f8fafc !important;
            border-color: #94a3b8 !important;
            box-shadow: 0 6px 16px rgba(71,85,105,0.12) !important;
            transform: translateY(-2px) !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked),
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%) !important;
            border-color: #64748b !important;
            box-shadow: 0 6px 20px rgba(71,85,105,0.20) !important;
        }
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p,
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
            color: #1e293b !important;
            font-weight: 650 !important;
            font-size: 16px !important;
        }
        .small-hint {
            font-size: 11.5px !important;
            font-weight: 600 !important;
            color: #94a3b8 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.2px !important;
            margin-bottom: 18px !important;
            margin-left: 4px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="small-hint">selecciona una opción</div>', unsafe_allow_html=True)
    
    pagina = st.radio(
        "navegacion", 
        ["🗺️ Mapa Reportes", "📈 Analítica Dashboard"], 
        index=0 if "Mapa" in st.session_state['pagina'] or "Reportes" in st.session_state['pagina'] else 1, 
        key="menu_pagina_v42",
        label_visibility="collapsed"
    )
    if "Mapa" in pagina:
        st.session_state['pagina'] = "🏠 Reportes"
    else:
        st.session_state['pagina'] = "📊 Dashboard Analítica"

# --- DASHBOARD ANALÍTICA ---
# --- DASHBOARD ANALÍTICA ---
# --- DASHBOARD ANALÍTICA ---
# --- DASHBOARD ANALÍTICA ---
if st.session_state.get('pagina') == "📊 Dashboard Analítica":
    import altair as alt
    
    st.title("📊 Dashboard Analítica - Sucursales")
    st.caption("Análisis de HISTORIAL_REPORTES + BDSUCURSALES | Hora CDMX")
    
    @st.cache_data(ttl=60)
    def cargar_historial_dashboard():
        df_hist = None
        try:
            if "gcp_service_account" in st.secrets:
                import gspread
                from google.oauth2.service_account import Credentials
                creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
                client = gspread.authorize(creds)
                # Buscar sheet_id de forma robusta
                sheet_id = None
                try:
                    sheet_id = st.secrets.get("sheet_id")
                except:
                    pass
                if not sheet_id:
                    try:
                        sheet_id = st.secrets.get("GOOGLE_SHEET_ID")
                    except:
                        pass
                if not sheet_id:
                    try:
                        sheet_id = st.secrets["SHEET_ID"]
                    except:
                        pass
                if not sheet_id:
                    # Fallback a variables globales del archivo original
                    try:
                        sheet_id = SHEET_ID
                    except:
                        try:
                            sheet_id = SHEET_ID_PRUEBAS
                        except:
                            sheet_id = None
                if not sheet_id:
                    st.error("No se encontró sheet_id en secrets (sheet_id, GOOGLE_SHEET_ID, SHEET_ID)")
                    return None
                sh = client.open_by_key(sheet_id)
                for name in ["HISTORIAL_REPORTES","BDSUCURSALES2","BDSUCURSALES"]:
                    try:
                        ws = sh.worksheet(name)
                        vals = ws.get_all_values()
                        if vals and len(vals)>1:
                            headers = [h.strip().upper() for h in vals[0]]
                            df_tmp = pd.DataFrame(vals[1:], columns=headers)
                            if len(headers) < 8:
                                continue
                            df_hist = df_tmp
                            break
                    except Exception as e:
                        continue
        except Exception as e:
            st.error(f"Error cargando historial: {e}")
        return df_hist

    df_hist = cargar_historial_dashboard()
    
    if df_hist is None or df_hist.empty:
        st.warning("No se encontró HISTORIAL_REPORTES.")
        st.stop()
    
    df_hist.columns = [c.strip().upper() for c in df_hist.columns]
    
    # KPIs - FIX: sin truncation, sin usuarios activos, full width
    st.markdown("### 📌 KPIs Generales")
    total_ev = len(df_hist)
    top_suc_count = df_hist['SUCURSAL'].value_counts()
    top_suc = top_suc_count.index[0] if not top_suc_count.empty else 'N/A'
    top_suc_num = int(top_suc_count.iloc[0]) if not top_suc_count.empty else 0
    top_edo_count = df_hist['ESTADO'].value_counts() if 'ESTADO' in df_hist.columns else pd.Series()
    top_edo = top_edo_count.index[0] if not top_edo_count.empty else 'N/A'
    top_edo_num = int(top_edo_count.iloc[0]) if not top_edo_count.empty else 0
    
    k1, k2, k3 = st.columns([1,2,1])
    with k1:
        st.markdown(f"""
        <div style="background:w
