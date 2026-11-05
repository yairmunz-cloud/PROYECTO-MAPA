import streamlit as st
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
    TZ_MX = ZoneInfo("America/Mexico_City")
except:
    TZ_MX = None

def now_mx():
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
    return datetime.utcnow() - timedelta(hours=6)

import pandas as pd
from datetime import datetime
import re
import time
import base64

st.set_page_config(page_title="REPORTES Y CONSULTAS SUCURSALES SEGUROS ATLAS", layout="wide", page_icon="🏢", initial_sidebar_state="expanded")

# --- FIX 1: HOJA PRINCIPAL UNIFICADA ---
SHEET_PRINCIPAL = "BDSUCURSALES"
ID_CORRECTO_SHEETS = "196gIWN8Sfk0_ZC-WHbL0FDw-BRwK4XnCkS14gAaN9UE"

# FIX FINAL v7: URL del usuario
USER_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTu5PSwbG4i6ywzNnt4H4hKiwyGygA7r_JBIeO6afIIlhIbrS3DmvNRj8isD-J7iu8OrEBYPCL8vc32/pub?output=csv"


# --- FIX CRITICO PARA RESETEAR FILTRO SIN ERROR DE STREAMLIT ---
if st.session_state.get('reset_filtro_pendiente'):
    st.session_state['filtro_activo_sel'] = "-- Ver todas las sucursales --"
    st.session_state['last_filtro_activo_sel'] = "-- Ver todas las sucursales --"
    st.session_state['reset_filtro_pendiente'] = False

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
        ["🗺 Mapa Reportes", "📈 Analítica Dashboard"], 
        index=0 if "Mapa" in st.session_state['pagina'] or "Reportes" in st.session_state['pagina'] else 1, 
        key="menu_pagina_v42",
        label_visibility="collapsed"
    )
    if "Mapa" in pagina:
        st.session_state['pagina'] = "🏠 Reportes"
    else:
        st.session_state['pagina'] = "📊 Dashboard Analítica"

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
                creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
                client = gspread.authorize(creds)
                sheet_id = None
                try: sheet_id = st.secrets.get("sheet_id")
                except: pass
                if not sheet_id:
                    try: sheet_id = st.secrets.get("GOOGLE_SHEET_ID")
                    except: pass
                if not sheet_id:
                    try: sheet_id = st.secrets["SHEET_ID"]
                    except: pass
                if not sheet_id:
                    try: sheet_id = SHEET_ID
                    except:
                        try: sheet_id = SHEET_ID_PRUEBAS = st.secrets.get("sheet_id", "196glWN8Sfk0_ZC-WHbL0FDw-BRwK4XnCkS14gAaN9UE")
                        except: sheet_id = None
                if not sheet_id:
                    st.error("No se encontró sheet_id en secrets")
                    return None
                sh = client.open_by_key(sheet_id)
                for name in ["HISTORIAL_REPORTES","BDSUCURSALES2","BDSUCURSALES"]:
                    try:
                        ws = sh.worksheet(name)
                        vals = ws.get_all_values()
                        if vals and len(vals)>1:
                            headers = [h.strip().upper() for h in vals[0]]
                            df_tmp = pd.DataFrame(vals[1:], columns=headers)
                            if len(headers) < 8: continue
                            df_hist = df_tmp
                            break
                    except: continue
        except Exception as e:
            st.error(f"Error cargando historial: {e}")
        return df_hist
    df_hist = cargar_historial_dashboard()
    if df_hist is None or df_hist.empty:
        st.warning("No se encontró HISTORIAL_REPORTES.")
        st.stop()
    df_hist.columns = [c.strip().upper() for c in df_hist.columns]
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
        st.markdown(f"""<div style="background:white; padding:18px; border-radius:12px; border-left:5px solid #0f172a; box-shadow:0 2px 8px rgba(0,0,0,0.06); height:110px;"><div style="font-size:13px; color:#64748b; font-weight:600;">📋 Total eventos</div><div style="font-size:32px; font-weight:800; color:#0f172a; margin-top:4px;">{total_ev}</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div style="background:white; padding:18px; border-radius:12px; border-left:5px solid #ef4444; box-shadow:0 2px 8px rgba(0,0,0,0.06); height:110px;"><div style="font-size:13px; color:#64748b; font-weight:600;">🏆 Sucursal con más eventos</div><div style="font-size:18px; font-weight:800; color:#0f172a; margin-top:4px; white-space:normal; word-break:break-word; line-height:1.2;">{top_suc}</div><div style="font-size:12px; color:#16a34a; background:#dcfce7; display:inline-block; padding:2px 8px; border-radius:99px; margin-top:4px;">↗ {top_suc_num} eventos</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div style="background:white; padding:18px; border-radius:12px; border-left:5px solid #3b82f6; box-shadow:0 2px 8px rgba(0,0,0,0.06); height:110px;"><div style="font-size:13px; color:#64748b; font-weight:600;">🗺 Estado con más fallas</div><div style="font-size:22px; font-weight:800; color:#0f172a; margin-top:4px; white-space:normal; word-break:break-word;">{top_edo}</div><div style="font-size:12px; color:#64748b; margin-top:4px;">{top_edo_num} eventos</div></div>""", unsafe_allow_html=True)
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        anios = sorted(df_hist['ANO'].dropna().unique().tolist()) if 'ANO' in df_hist.columns else []
        sel_anio = st.selectbox("Filtrar por AÑO:", ["Todos"] + anios)
    with col_f2:
        estados = sorted(df_hist['ESTADO'].dropna().unique().tolist()) if 'ESTADO' in df_hist.columns else []
        sel_estado = st.selectbox("Filtrar por ESTADO:", ["Todos"] + estados)
    with col_f3:
        meses = sorted(df_hist['MES'].dropna().unique().tolist()) if 'MES' in df_hist.columns else []
        sel_mes = st.selectbox("Filtrar por MES:", ["Todos"] + meses)
    df_f = df_hist.copy()
    if sel_anio != "Todos" and 'ANO' in df_f.columns: df_f = df_f[df_f['ANO']==sel_anio]
    if sel_estado != "Todos" and 'ESTADO' in df_f.columns: df_f = df_f[df_f['ESTADO']==sel_estado]
    if sel_mes != "Todos" and 'MES' in df_f.columns: df_f = df_f[df_f['MES']==sel_mes]
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🏆 Top 10 Sucursales con más fallas")
        if 'SUCURSAL' in df_f.columns:
            top10 = df_f['SUCURSAL'].value_counts().head(10).reset_index()
            top10.columns = ['SUCURSAL','REPORTES']
            chart = alt.Chart(top10).mark_bar(color='#ef4444').encode(x='REPORTES:Q', y=alt.Y('SUCURSAL:N', sort='-x'), tooltip=['SUCURSAL','REPORTES']).properties(height=400)
            st.altair_chart(chart, width='stretch')
    with c2:
        st.subheader("📅 Reportes por Mes / Año")
        if 'MES' in df_f.columns and 'ANO' in df_f.columns:
            df_f['MES_ANO'] = df_f['ANO'].astype(str) + "-" + df_f['MES'].astype(str).str.zfill(2)
            por_mes = df_f.groupby('MES_ANO').size().reset_index(name='REPORTES').sort_values('MES_ANO')
            chart2 = alt.Chart(por_mes).mark_line(point=True, color='#0f172a').encode(x='MES_ANO:N', y='REPORTES:Q', tooltip=['MES_ANO','REPORTES']).properties(height=400)
            st.altair_chart(chart2, width='stretch')
    st.stop()

if st.session_state.get('pagina') != "🏠 Reportes":
    st.stop()

B64_ATLAS_LOGO = ""
b64_logo = B64_ATLAS_LOGO
try:
    for logo_path in ["logo_atlas.png", "image_c93c8b.png", "atlas_logo.png"]:
        try:
            with open(logo_path, "rb") as f:
                b64_logo = base64.b64encode(f.read()).decode()
                break
        except: continue
except: pass

st.markdown("""
<style>
    html, body { font-family: Inter, sans-serif; }
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .glass { background: rgba(255,255,255,0.95) !important; border-radius: 18px; padding: 20px 22px; box-shadow: 0 8px 32px rgba(15,23,42,0.08); border: 1px solid white; }
    .glass-dark { background: rgba(15,23,42,0.88) !important; color: white; border-radius: 18px; padding: 16px 18px; }
    .badge { display:inline-flex; padding:7px 14px; border-radius:100px; font-size:0.82rem; font-weight:800; letter-spacing:0.3px; }
    .badge-ok { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
    .badge-warn { background:#fef9c3; color:#854d0e; border:1px solid #fde68a; }
    .badge-orange { background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; }
    .badge-red { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }
    .filter-pill { background: white; border: 1px solid #e2e8f0; border-radius: 50px !important; padding: 10px 18px 12px 18px !important; }
    .filter-label { font-size:0.72rem !important; font-weight:800 !important; color:#64748b !important; letter-spacing:0.8px; text-transform:uppercase; margin-bottom:2px; }
    .rep-box { background:#f1f5f9; border:1px solid #e2e8f0; border-radius:8px; padding:4px 10px; font-weight:700; font-size:0.85rem; display:inline-flex; gap:6px; align-items:center; }
</style>
""", unsafe_allow_html=True)

SHEET_ID_PRUEBAS = None

def norm(s):
    return str(s).strip().upper().replace("  "," ").replace("\n","").replace("\r","")

# --- FIX 2: CACHE MAS CORTO Y LECTURA UNIFICADA ---
@st.cache_data(ttl=0, show_spinner=False)
def cargar_datos(sheet_id_override=None):
    df_privado = None
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sid = sheet_id_override or ID_CORRECTO_SHEETS or st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            if sid:
                sh = client.open_by_key(sid)
                ws = None
                # FIX: prioriza SHEET_PRINCIPAL y solo acepta si tiene datos
                for name_try in [SHEET_PRINCIPAL, "BDSUCURSALES", "BDSUCURSALESPRO", "Hoja1", "Sheet1"]:
                    try:
                        ws_try = sh.worksheet(name_try)
                        vals_try = ws_try.get_all_values()
                        if vals_try and len(vals_try) > 5:
                            ws = ws_try
                            break
                    except:
                        continue
                if not ws:
                    try:
                        ws = sh.worksheet(SHEET_PRINCIPAL)
                    except:
                        ws = sh.sheet1
                all_vals = ws.get_all_values()
                if all_vals and len(all_vals) > 1:
                    headers = [h.strip().upper() for h in all_vals[0]]
                    rows = all_vals[1:]
                    df_tmp = pd.DataFrame(rows, columns=headers)
                    df_tmp = df_tmp.replace('', pd.NA)
                    df_tmp = df_tmp.dropna(how='all')
                    df_tmp = df_tmp.fillna("")
                    if len(df_tmp) >= 1:
                        df_privado = df_tmp
    except Exception as e:
        pass
    if df_privado is not None and not df_privado.empty and len(df_privado) > 5:
        return df_privado
    try:
        base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTu5PSwbG4i6ywzNnt4H4hKiwyGygA7r_JBIeO6afIIlhIbrS3DmvNRj8isD-J7iu8OrEBYPCL8vc32/pub?output=csv"
        url = f"{base_url}&cb={int(time.time())}"
        df = pd.read_csv(url, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        return df.dropna(how='all').fillna("")
    except:
        if df_privado is not None:
            return df_privado
        return pd.DataFrame(columns=["ESTADO","SUCURSAL","TELMEX","NO. REPORTE","FECHA","OBSERVACIONES"])

def deduplicar_df(df_in):
    try:
        import unicodedata
        def clean_norm(s):
            s = str(s).strip()
            if not s: return ""
            s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            s = s.upper()
            s = re.sub(r'\s+', ' ', s)
            return s.strip()
        if df_in is None or df_in.empty: return df_in
        col_est = None; col_suc = None
        for c in df_in.columns:
            cu = str(c).upper()
            if not col_est and ('ESTADO' in cu or cu == 'EDO'): col_est = c
            if not col_suc and 'SUCURSAL' in cu: col_suc = c
        if not col_est or not col_suc: return df_in
        df_in['_KEY_DEDUP'] = df_in[col_est].apply(clean_norm) + "||" + df_in[col_suc].apply(clean_norm)
        col_rep = None
        for c in df_in.columns:
            if 'REPORTE' in str(c).upper(): col_rep = c; break
        if col_rep:
            df_in['_HAS_REP'] = df_in[col_rep].apply(lambda x: 1 if str(x).strip().lower() not in ["", "0", "0.0", "sin reporte", "none", "nan", "vacio", "s/r"] else 0)
            df_in = df_in.sort_values(by=['_KEY_DEDUP', '_HAS_REP'])
        df_in = df_in.drop_duplicates(subset=['_KEY_DEDUP'], keep='last')
        df_in = df_in.drop(columns=[c for c in ['_KEY_DEDUP', '_HAS_REP'] if c in df_in.columns])
        return df_in
    except: return df_in

df_raw = cargar_datos()

def buscar_col_temp(kws, df_ref):
    for c in df_ref.columns:
        for kw in kws:
            if kw in c: return c
    return None

COL_EST_TMP = buscar_col_temp(['ESTADO','EDO'], df_raw)
COL_SUC_TMP = buscar_col_temp(['SUCURSAL','SUC','SITIO'], df_raw)
if COL_EST_TMP and not df_raw.empty:
    df_raw[COL_EST_TMP] = df_raw[COL_EST_TMP].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
if COL_SUC_TMP and not df_raw.empty:
    df_raw[COL_SUC_TMP] = df_raw[COL_SUC_TMP].astype(str).str.strip()
df = deduplicar_df(df_raw)

def buscar_col(kws):
    for c in df.columns:
        for kw in kws:
            if kw in c: return c
    return None

COL_EST = buscar_col(['ESTADO','EDO'])
COL_SUC = buscar_col(['SUCURSAL','SUC','SITIO'])
COL_TEL = buscar_col(['TELMEX','TEL','LINEA'])
COL_REP = buscar_col(['NO. REPORTE','NO REPORTE','REPORTE'])
COL_FEC = buscar_col(['FECHA','FEC'])
COL_OBS = buscar_col(['OBSERVACIONES','OBS','FALLA','COMENTARIO'])
COL_TEL_FALLA = buscar_col(['LINEAS CON FALLA','LINEA CON FALLA','TEL FALLA','LINEA FALLA','FALLA LINEA','LINEAS FALLA','LINEA REPORTADA'])

if COL_EST and not df.empty:
    df[COL_EST] = df[COL_EST].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
if COL_SUC and not df.empty:
    df[COL_SUC] = df[COL_SUC].astype(str).str.strip()

def tiene_reporte(v):
    if pd.isna(v): return False
    return str(v).strip().lower() not in ["","0","0.0","sin reporte","none","nan","vacio","s/r"]

def split_multi_val(val):
    if val is None: 
        return []
    val = str(val).strip()
    if not val: 
        return []
    # Separadores reales usados
    for sep in [" | ", " |", "| ", "|"]:
        if sep in val:
            return [v.strip() for v in val.split(sep) if v.strip()]
    return [val]

def eliminar_reporte_hoja1(estado, sucursal, reporte_a_borrar, fecha_a_borrar=None, falla_a_borrar=None):
    """Borra SOLO el reporte seleccionado por su numero, deja los demas"""
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
        client = gspread.authorize(creds)
        sheet_id = st.secrets.get("sheet_id", "196glWN8Sfk0_ZC-WHbL0FDw-BRwK4XnCkS14gAaN9UE")
        sh = client.open_by_key(sheet_id)
        
        # Buscar en todas las pestañas posibles
        hojas_buscar = ["BDSUCURSALES", "Copia de BDSUCURSALESPRO", "BDSUCURSALES2", "BDSUCRSALES"]
        ws_found = None
        row_found = None
        df_row = None
        
        for nombre_hoja in hojas_buscar:
            try:
                ws = sh.worksheet(nombre_hoja)
                data = ws.get_all_records()
                if not data:
                    continue
                df = pd.DataFrame(data)
                df.columns = [str(c).strip().upper() for c in df.columns]
                # Buscar fila
                for idx, r in df.iterrows():
                    est = str(r.get("ESTADO","")).strip().upper()
                    suc = str(r.get("SUCURSAL","")).strip().upper()
                    if est == str(estado).strip().upper() and suc == str(sucursal).strip().upper():
                        ws_found = ws
                        row_found = idx + 2  # +1 header, +1 1-indexed
                        df_row = r
                        break
                if ws_found:
                    break
            except Exception:
                continue
        
        if not ws_found:
            return False, f"No se encontro {estado} - {sucursal} en ninguna pestaña"
        
        # Obtener valores actuales de la fila
        # Columnas: 1 ESTADO, 2 SUCURSAL, 3 TELMEX, 4 NO. REPORTE, 5 FECHA, 6 OBSERVACIONES (FALLA), 7 OBSERVACIONES?
        # Segun tu sheet: D=NO.REPORTE, E=FECHA, F=OBSERVACIONES/FALLA
        try:
            rep_actual = ws_found.cell(row_found, 4).value or ""
            fecha_actual = ws_found.cell(row_found, 5).value or ""
            falla_actual = ws_found.cell(row_found, 6).value or ""
            obs_actual = ws_found.cell(row_found, 7).value or "" if ws_found.col_count >= 7 else ""
        except Exception as e:
            return False, f"Error leyendo celdas: {e}"
        
        reportes = split_multi_val(rep_actual)
        fechas = split_multi_val(fecha_actual)
        fallas = split_multi_val(falla_actual)
        obss = split_multi_val(obs_actual)
        
        # Encontrar indice del reporte a borrar (por numero exacto)
        idx_borrar = -1
        reporte_a_borrar_str = str(reporte_a_borrar).strip()
        for i, rep in enumerate(reportes):
            if str(rep).strip() == reporte_a_borrar_str:
                idx_borrar = i
                break
            # Tambien comparar sin espacios
            if str(rep).strip().replace(" ","") == reporte_a_borrar_str.replace(" ",""):
                idx_borrar = i
                break
        
        if idx_borrar == -1:
            # Si no lo encuentra por numero exacto, intentar por fecha+falla si se proporcionan
            if fecha_a_borrar:
                for i, fec in enumerate(fechas):
                    if str(fec).strip() == str(fecha_a_borrar).strip():
                        idx_borrar = i
                        break
            if idx_borrar == -1:
                return False, f"No se encontro el reporte {reporte_a_borrar} en {reportes}"
        
        # Borrar solo ese indice de todas las listas (si existen)
        def borrar_indice(lista, idx):
            if not lista: return []
            if idx < len(lista):
                return [v for j, v in enumerate(lista) if j != idx]
            return lista
        
        nuevos_reportes = borrar_indice(reportes, idx_borrar)
        nuevas_fechas = borrar_indice(fechas, idx_borrar)
        nuevas_fallas = borrar_indice(fallas, idx_borrar)
        nuevas_obss = borrar_indice(obss, idx_borrar)
        
        # Guardar de vuelta (si queda vacio, poner "")
        ws_found.update_cell(row_found, 4, " | ".join(nuevos_reportes) if nuevos_reportes else "")
        ws_found.update_cell(row_found, 5, " | ".join(nuevas_fechas) if nuevas_fechas else "")
        ws_found.update_cell(row_found, 6, " | ".join(nuevas_fallas) if nuevas_fallas else "")
        if ws_found.col_count >= 7:
            ws_found.update_cell(row_found, 7, " | ".join(nuevas_obss) if nuevas_obss else "")
        
        # Guardar en HISTORIAL
        try:
            try:
                ws_hist = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws_hist = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=1000, cols=10)
                ws_hist.append_row(["ESTADO","SUCURSAL","NO. REPORTE","FECHA CIERRE","FALLA","FECHA ORIGINAL","USUARIO"])
            
            from datetime import datetime
            ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
            ws_hist.append_row([
                estado,
                sucursal,
                reporte_a_borrar_str,
                ahora,
                falla_actual if len(fallas)==1 else (fallas[idx_borrar] if idx_borrar < len(fallas) else ""),
                fecha_actual if len(fechas)==1 else (fechas[idx_borrar] if idx_borrar < len(fechas) else ""),
                st.session_state.get("usuario_actual","")
            ])
        except Exception as e_hist:
            print(f"Error historial: {e_hist}")
        
        return True, f"Borrado REP:{reporte_a_borrar_str} en {ws_found.title} fila {row_found}. Quedan {len(nuevos_reportes)} reporte(s)"
        
    except Exception as e:
        import traceback
        return False, f"Error al cerrar: {e}\n{traceback.format_exc()}"
