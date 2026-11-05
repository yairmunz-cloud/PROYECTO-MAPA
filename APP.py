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
def split_multi_val(v):
    if pd.isna(v): return []
    s = str(v).strip()
    if not s or s.lower() in ["nan","none",""]: return []
    import re as _re
    if "|" in s: parts = _re.split(r"\s*\|\s*", s)
    else: parts = [s]
    cleaned = [p.strip() for p in parts if p.strip() and p.strip().lower() not in ["nan","none",""]]
    return cleaned
def join_multi_val(lst):
    cleaned = [str(x).strip() for x in lst if str(x).strip()]
    return " | ".join(cleaned)
def dias_desde(fecha_str):
    if not fecha_str or str(fecha_str).lower() in ['nan','none','']: return None, "Sin fecha"
    dt = pd.to_datetime(fecha_str, errors='coerce', dayfirst=True)
    if pd.isna(dt): return None, "Fecha invalida"
    now_naive = now_mx()
    try: now_naive = now_naive.replace(tzinfo=None)
    except: pass
    try:
        if hasattr(dt, 'to_pydatetime'): dt = dt.to_pydatetime()
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None: dt = dt.replace(tzinfo=None)
    except: pass
    diff = (now_naive - dt).days
    if diff < 0: return diff, "Fecha futura"
    if diff == 0: return diff, "Hoy"
    elif diff == 1: return diff, "1 dia"
    elif diff <= 2: return diff, f"{diff} dias"
    elif diff <= 5: return diff, f"{diff} dias"
    else: return diff, f"{diff} dias - Critico"
def split_tels(raw):
    if pd.isna(raw) or str(raw).lower() in ['nan','none','']: return []
    s = str(raw).strip()
    s = re.sub(r'(\d{3})(\d{3}-\d{3}-\d{4})', r'\1,\2', s)
    s = re.sub(r'(\d{4})(\d{3}-)', r'\1,\2', s)
    partes = re.split(r'[\n,;/\s]+', s)
    tels = []
    for p in partes:
        p = p.strip()
        if not p or p.lower()=='nan': continue
        if re.match(r'^\d{3}-\d{3}-\d{4}$', p): tels.append(p)
        elif re.match(r'^\d{10}$', p): tels.append(f"{p[:3]}-{p[3:6]}-{p[6:]}")
        elif '-' in p and len(p)>=7: tels.append(p)
    if not tels:
        raw_tels = [t.strip() for t in re.split(r'[\n,;/]+', str(raw)) if t.strip() and t.strip().lower()!='nan']
        for item in raw_tels:
            encontrados = re.findall(r'\d{3}[-\s]?\d{3}[-\s]?\d{4}|\d{10}', item)
            if encontrados:
                for e in encontrados:
                    e = e.replace(' ', '-')
                    if len(e)==10 and '-' not in e: e = f"{e[:3]}-{e[3:6]}-{e[6:]}"
                    tels.append(e)
            else: tels.append(item)
    seen=set(); uniq=[]
    for t in tels:
        if t not in seen: seen.add(t); uniq.append(t)
    return uniq

import hashlib, hmac
def _hash_pwd(p): return hashlib.sha256(p.encode()).hexdigest()
def sanitize_sheets_input(v, max_len=500):
    if v is None: return ""
    s=str(v).strip()
    if len(s)>max_len: s=s[:max_len]
    if s and s[0] in ("=","+","-","@"): s="'"+s
    return s
USUARIOS = {}
def check_login(user, pwd):
    try:
        if "users" not in st.secrets: return False
        attempts = st.session_state.get('login_attempts',0)
        if attempts >= 5:
            last = st.session_state.get('last_failed_login')
            if last:
                try:
                    diff = (now_mx().replace(tzinfo=None) - last.replace(tzinfo=None)).total_seconds()/60
                    if diff < 10: return False
                    else: st.session_state['login_attempts']=0
                except: pass
        users_secret = st.secrets["users"]
        if user not in users_secret:
            st.session_state['login_attempts']=st.session_state.get('login_attempts',0)+1
            st.session_state['last_failed_login']=now_mx().replace(tzinfo=None)
            import time as _t; _t.sleep(0.8)
            return False
        stored=str(users_secret[user]).strip()
        pwd_input=str(pwd).strip()
        ok=False
        if len(stored)==64 and all(c in "0123456789abcdefABCDEF" for c in stored):
            ok=_hash_pwd(pwd_input)==stored.lower()
        else:
            ok=hmac.compare_digest(stored,pwd_input)
        if ok:
            st.session_state['login_attempts']=0
            st.session_state['last_activity']=now_mx().replace(tzinfo=None)
        else:
            st.session_state['login_attempts']=st.session_state.get('login_attempts',0)+1
            st.session_state['last_failed_login']=now_mx().replace(tzinfo=None)
        return ok
    except: return False
def log_acceso(usuario, accion="Login"):
    now = now_mx(); fecha = now.strftime("%d/%m/%Y"); hora = now.strftime("%H:%M:%S")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            try:
                sh = client.open_by_key(ID_CORRECTO_SHEETS)
            except:
                sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
                sh = client.open_by_key(sheet_id)
            try: ws = sh.worksheet("LOG_ACCESOS")
            except:
                ws = sh.add_worksheet(title="LOG_ACCESOS", rows=1000, cols=10)
                ws.append_row(["FECHA", "HORA", "USUARIO", "ACCION", "DETALLE"])
            ws.append_row([fecha, hora, usuario, accion, "Acceso desde app"])
    except: pass
def log_reporte_historial(usuario, estado, sucursal, no_reporte, fecha_reporte, tel="", observaciones=""):
    now = now_mx(); fecha_reg = now.strftime("%d/%m/%Y"); hora_reg = now.strftime("%H:%M:%S")
    mes = now.strftime("%m"); anio = now.strftime("%Y"); dia = now.strftime("%d")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            try: ws = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=5000, cols=15)
                ws.append_row(["FECHA_REGISTRO", "HORA_REGISTRO", "DIA", "MES", "ANIO", "USUARIO", "ESTADO", "SUCURSAL", "NO_REPORTE", "FECHA_REPORTE", "TEL", "OBSERVACIONES"])
            ws.append_row([fecha_reg, hora_reg, dia, mes, anio, usuario, estado, sucursal, no_reporte, fecha_reporte, tel, observaciones])
            return True
    except: return False
    return True
def log_eliminacion_historial(usuario, estado, sucursal, no_reporte, fecha_reporte, observaciones=""):
    now = now_mx(); fecha_reg = now.strftime("%d/%m/%Y"); hora_reg = now.strftime("%H:%M:%S")
    mes = now.strftime("%m"); anio = now.strftime("%Y"); dia = now.strftime("%d")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            try: ws = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=5000, cols=15)
                ws.append_row(["FECHA_REGISTRO", "HORA_REGISTRO", "DIA", "MES", "ANIO", "USUARIO", "ESTADO", "SUCURSAL", "NO_REPORTE", "FECHA_REPORTE", "TEL", "OBSERVACIONES"])
            ws.append_row([fecha_reg, hora_reg, dia, mes, anio, usuario, estado, sucursal, f"ELIMINADO-{no_reporte}", fecha_reporte, "", f"ELIMINACION: {observaciones}"])
            return True
    except: return False
    return True

def eliminar_reporte_hoja1(estado, sucursal, no_reporte_actual, indice_a_borrar=None):
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            import unicodedata
            def clean_norm(s):
                s = str(s).strip()
                if not s: return ""
                s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                s = s.upper()
                s = re.sub(r'\s+', ' ', s)
                return s.strip()
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            # FIX: SIEMPRE BDSUCURSALES2
            try:
                ws_main = sh.worksheet(SHEET_PRINCIPAL)
            except:
                ws_main = sh.worksheet("BDSUCURSALES")
            headers = ws_main.row_values(1)
            headers_upper = [h.strip().upper() for h in headers]
            def find_idx(kws):
                for i, h in enumerate(headers_upper):
                    for kw in kws:
                        if kw in h: return i+1
                return None
            col_est_idx = find_idx(['ESTADO','EDO'])
            col_suc_idx = find_idx(['SUCURSAL','SUC','SITIO'])
            col_rep_idx = find_idx(['NO. REPORTE','NO REPORTE','REPORTE'])
            col_fec_idx = find_idx(['FECHA DE REPORTE','FECHA REPORTE','FECHA','FEC'])
            col_falla_idx = find_idx(['FALLA','OBSERVACIONES','OBS','COMENTARIO'])
            col_tel_falla_idx = find_idx(['LINEAS CON FALLA','LINEA CON FALLA','TEL FALLA','LINEA FALLA','LINEA REPORTADA'])
            all_vals = ws_main.get_all_values()
            row_found = None
            last_estado = ""
            for idx_row in range(1, len(all_vals)):
                row = all_vals[idx_row]
                try:
                    est_cell_raw = row[col_est_idx-1] if col_est_idx and col_est_idx-1 < len(row) else ""
                    suc_cell_raw = row[col_suc_idx-1] if col_suc_idx and col_suc_idx-1 < len(row) else ""
                    if est_cell_raw and str(est_cell_raw).strip(): last_estado = est_cell_raw
                    est_cell = last_estado if last_estado else est_cell_raw
                    if not est_cell or not suc_cell_raw: continue
                    if clean_norm(est_cell) == clean_norm(estado) and clean_norm(suc_cell_raw) == clean_norm(sucursal):
                        row_found = idx_row+1
                        break
                except: continue
            if not row_found:
                return False, f"No se encontro: {estado} / {sucursal}"
            cur_rep = all_vals[row_found-1][col_rep_idx-1] if col_rep_idx and col_rep_idx-1 < len(all_vals[row_found-1]) else ""
            cur_fec = all_vals[row_found-1][col_fec_idx-1] if col_fec_idx and col_fec_idx-1 < len(all_vals[row_found-1]) else ""
            cur_falla = all_vals[row_found-1][col_falla_idx-1] if col_falla_idx and col_falla_idx-1 < len(all_vals[row_found-1]) else ""
            cur_tel_falla = all_vals[row_found-1][col_tel_falla_idx-1] if col_tel_falla_idx and col_tel_falla_idx-1 < len(all_vals[row_found-1]) else ""
            reps = split_multi_val(cur_rep)
            fecs = split_multi_val(cur_fec)
            fallas = split_multi_val(cur_falla)
            tel_fallas = split_multi_val(cur_tel_falla)
            if indice_a_borrar is None:
                try: indice_a_borrar = next(i for i,r in enumerate(reps) if str(r).strip()==str(no_reporte_actual).strip())
                except: indice_a_borrar = 0 if reps else None
            if indice_a_borrar is not None and 0 <= indice_a_borrar < len(reps):
                reps.pop(indice_a_borrar)
                if indice_a_borrar < len(fecs): fecs.pop(indice_a_borrar)
                if indice_a_borrar < len(fallas): fallas.pop(indice_a_borrar)
                if indice_a_borrar < len(tel_fallas): tel_fallas.pop(indice_a_borrar)
                if reps:
                    ws_main.update_cell(row_found, col_rep_idx, join_multi_val(reps))
                    if col_fec_idx: ws_main.update_cell(row_found, col_fec_idx, join_multi_val(fecs))
                    if col_falla_idx: ws_main.update_cell(row_found, col_falla_idx, join_multi_val(fallas))
                    if col_tel_falla_idx: ws_main.update_cell(row_found, col_tel_falla_idx, join_multi_val(tel_fallas))
                else:
                    ws_main.update_cell(row_found, col_rep_idx, "")
                    if col_fec_idx: ws_main.update_cell(row_found, col_fec_idx, "")
                    if col_falla_idx: ws_main.update_cell(row_found, col_falla_idx, "")
                    if col_tel_falla_idx: ws_main.update_cell(row_found, col_tel_falla_idx, "")
                return True, row_found
            else: return False, "Indice no encontrado"
        else: return True, "Modo demo"
    except Exception as e: return False, str(e)

lista_estados = sorted(df[COL_EST].dropna().unique()) if COL_EST in df.columns else []
df_reportes = df[df[COL_REP].apply(tiene_reporte)] if COL_REP and COL_REP in df.columns else pd.DataFrame()

for k in ['admin_auth','show_login','show_add_form','current_user','batch_reportes','show_close_login','show_close_confirm','close_target','close_auth','close_user','last_logged_suc','last_visita_log','visitas_demo','filtro_activo_sel','show_delete_login','show_delete_confirm','delete_target','delete_auth','show_case_pdf']:
    if k not in st.session_state:
        st.session_state[k] = False if 'auth' in k or 'show' in k else ([] if 'batch' in k or 'visitas' in k or 'demo' in k else None)
if 'visitas_demo' not in st.session_state: st.session_state['visitas_demo']=[]
if 'batch_reportes' not in st.session_state: st.session_state['batch_reportes']=[]
if 'filtro_activo_sel' not in st.session_state: st.session_state['filtro_activo_sel']="-- Ver todas las sucursales --"
if 'show_case_pdf' not in st.session_state: st.session_state['show_case_pdf']=False

opciones_activas = []
mapa_activos = {}
mapa_activos_global = {}
from collections import defaultdict
grupo_sucursal = defaultdict(list)
grupo_info = {}
total_reps_global = 0
if not df_reportes.empty:
    for _, row in df_reportes.iterrows():
        rep_raw_full = str(row.get(COL_REP, "")).strip()
        reps_full = split_multi_val(rep_raw_full)
        if not reps_full and tiene_reporte(rep_raw_full): reps_full = [rep_raw_full]
        estado_val = str(row.get(COL_EST,"")).strip()
        suc_val = str(row.get(COL_SUC,"")).strip()
        key = (estado_val, suc_val)
        for rep in reps_full:
            if tiene_reporte(rep):
                grupo_sucursal[key].append(rep)
                total_reps_global += 1
        if key not in grupo_info: grupo_info[key] = row
    for (estado_val, suc_val), reps_list in grupo_sucursal.items():
        row_base = grupo_info[(estado_val, suc_val)]
        count = len(reps_list)
        fec_raw = str(row_base.get(COL_FEC, "")).strip()
        fecs = split_multi_val(fec_raw)
        max_dias = 0; txt_badge = "Hoy"
        for f in (fecs if fecs else [fec_raw]):
            d, txt = dias_desde(f) if f else (None, "Sin fecha")
            if d is not None and d > max_dias: max_dias = d; txt_badge = txt
        if count == 1: label = f"{estado_val} - {suc_val} | REP: {reps_list[0]} | {txt_badge}"
        else: label = f"{estado_val} - {suc_val} | {count} REPORTES | {txt_badge} ({count} activos)"
        opciones_activas.append(label)
        mapa_activos[label] = {"estado": estado_val, "sucursal": suc_val, "count": count, "reps": reps_list, "row": row_base}
    opciones_activas = sorted(opciones_activas)
    mapa_activos_global = mapa_activos
else: total_reps_global = 0
opciones_con_todos = ["-- Ver todas las sucursales --"] + opciones_activas

c1, c2 = st.columns([2.2, 1.3])
with c1:
    if b64_logo:
        st.markdown(f"""<div style="display:flex; align-items:center; gap:16px"><div style="width:52px; height:52px; border-radius:14px; overflow:hidden; background:white"><img src="data:image/png;base64,{b64_logo}" style="width:100%; height:100%; object-fit:cover"></div><div style="font-size:1.75rem; font-weight:900; letter-spacing:-0.8px; line-height:1.1">REPORTES Y CONSULTAS<br>SUCURSALES SEGUROS ATLAS</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="font-size:1.75rem; font-weight:900; line-height:1.1">REPORTES Y CONSULTAS<br>SUCURSALES SEGUROS ATLAS</div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("📞 Telefonos CASE NACIONAL", key="btn_case_nacional", type="primary", width='content'):
        st.session_state['show_case_pdf'] = True
    st.markdown("""
    <style>
    div[data-testid="stButton"] button[kind="primary"][id="btn_case_nacional"] {
        background: #1e40af !important; border: 1px solid #1e40af !important; color: white !important; font-weight: 800 !important; border-radius: 10px !important; padding: 8px 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="glass-dark"><div style="display:flex; justify-content:space-between; align-items:center"><div style="display:flex; gap:10px; align-items:center"><div style="width:34px; height:34px; background:rgba(239,68,68,0.25); border-radius:9px; display:flex; align-items:center; justify-content:center">🚨</div><div><div style="font-weight:700">Reportes Activos</div><div style="font-size:0.75rem; opacity:0.7">{total_reps_global} requieren atencion ({len(df_reportes)} sucursales)</div></div></div><div style="font-size:1.6rem; font-weight:900">{total_reps_global}</div></div></div>""", unsafe_allow_html=True)
    if not df_reportes.empty:
        st.markdown(f"""
        <div class="glass" style="margin-top:10px; padding:10px 14px; border-left:4px solid #ef4444; background:white !important; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:6px;">
                    <div style="width:18px; height:18px; background:#ef4444; border-radius:5px; display:flex; align-items:center; justify-content:center; color:white; font-size:10px;">🚨</div>
                    <div style="font-weight:800; font-size:0.68rem; letter-spacing:0.4px; color:#991b1b;">VER SOLO SUCURSALES CON REPORTE ACTIVO</div>
                </div>
                <span class="badge badge-red" style="font-size:0.65rem; padding:3px 8px;">{len(df_reportes)} encontradas</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if "filtro_activo_sel" not in st.session_state or st.session_state["filtro_activo_sel"] not in opciones_con_todos:
            st.session_state["filtro_activo_sel"] = "-- Ver todas las sucursales --"
        sel_activo = st.selectbox("Filtro reporte activo", opciones_con_todos, key="filtro_activo_sel", label_visibility="collapsed", placeholder="🔍 Selecciona sucursal con reporte activo...")
        last_filtro = st.session_state.get('last_filtro_activo_sel', '-- Ver todas las sucursales --')
        if sel_activo != last_filtro:
            st.session_state['last_filtro_activo_sel'] = sel_activo
            if sel_activo != "-- Ver todas las sucursales --":
                info_sel = mapa_activos.get(sel_activo)
                if info_sel:
                    st.session_state['estado_real'] = info_sel['estado']
                    st.session_state['sucursal_real'] = info_sel['sucursal']
                    for k in list(st.session_state.keys()):
                        if k.startswith('sucursal_real_'): del st.session_state[k]
                    st.rerun()
    else:
        st.markdown('<div class="glass" style="margin-top:10px; padding:10px 14px; border-left:4px solid #16a34a; background:white !important; border-radius:12px;"><div style="display:flex; align-items:center; gap:8px;"><div style="width:20px; height:20px; background:#16a34a; border-radius:6px; display:flex; align-items:center; justify-content:center; color:white; font-size:12px;"></div><b style="color:#166534; font-size:0.75rem;">Sin reportes activos</b></div></div>', unsafe_allow_html=True)

if st.session_state.get('show_case_pdf'):
    st.markdown('<div class="glass" style="border:2px solid #1e40af; padding:18px; margin-top:12px; background:white;">', unsafe_allow_html=True)
    st.markdown("### 📞 Telefonos CASE NACIONAL - Soporte Empresarial 24H 365 días")
    c_pdf1, c_pdf2 = st.columns([4,1])
    with c_pdf2:
        if st.button("✖ Cerrar", width='stretch'):
            st.session_state['show_case_pdf'] = False
            st.rerun()
    st.markdown("""
    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; padding:16px 20px;">
        <div style="font-weight:900; color:#1e40af; margin-bottom:12px; font-size:1rem;">☎ DIRECTORIO CASE NACIONAL - SOPORTE 24H 365 DÍAS</div>
        <div style="display:grid; gap:10px;">
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>Red Noroeste (Telnor) - 800 025 9111</b><br><span style="font-size:0.85rem; color:#64748b;">Baja California - San Luis Rio Colorado, Son.</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE Hermosillo - 800 627 3000</b><br><span style="font-size:0.85rem; color:#64748b;">Sonora - Sinaloa - Baja California Sur</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE Chihuahua - 800 147 6500</b><br><span style="font-size:0.85rem; color:#64748b;">Chihuahua - Durango - Torreón, Coah.</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE Monterrey - 800 832 2600</b><br><span style="font-size:0.85rem; color:#64748b;">Nuevo León - Tamaulipas - Coahuila - SLP - Zacatecas</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE Guadalajara - 800 364 0500</b><br><span style="font-size:0.85rem; color:#64748b;">Jalisco - Aguascalientes - Colima - Nayarit - Zacatecas</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE Querétaro - 800 404 0000</b><br><span style="font-size:0.85rem; color:#64748b;">Querétaro - Guanajuato - Michoacán - SLP</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #dc2626;"><b>CASE San Juan - 800 905 2200</b><br><span style="font-size:0.85rem; color:#64748b;">CDMX y zona metropolitana - Edo. de México - Morelos - Guerrero</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE Puebla - 800 226 1500</b><br><span style="font-size:0.85rem; color:#64748b;">Puebla - Tlaxcala - Veracruz - Hidalgo - Edo. de México - Morelos - Guerrero</span></div>
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE Mérida - 800 201 1100</b><br><span style="font-size:0.85rem; color:#64748b;">Yucatán - Quintana Roo - Campeche - Tabasco - Chiapas - Oaxaca - Veracruz</span></div>
        </div>
        <div style="margin-top:14px; padding:10px; background:#1e40af; color:white; border-radius:8px; text-align:center; font-weight:800; font-size:0.85rem;">📧 SOPORTE EMPRESARIAL 24H LOS 365 DÍAS DEL AÑO</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

es_modo_agregar = st.session_state.get('show_add_form', False) and st.session_state.get('admin_auth', False)
default_est_idx = 0
default_suc = None
if 'estado_real' in st.session_state and st.session_state['estado_real'] in lista_estados:
    default_est_idx = lista_estados.index(st.session_state['estado_real'])
    default_suc = st.session_state.get('sucursal_real')

if not es_modo_agregar:
    f1, f2, f3 = st.columns([1.1, 1.8, 0.7], gap="medium")
    with f1:
        st.markdown('<div class="filter-pill"><div class="filter-label">📍 Estado</div>', unsafe_allow_html=True)
        if "estado_real" not in st.session_state or st.session_state["estado_real"] not in lista_estados:
            st.session_state["estado_real"] = lista_estados[default_est_idx] if lista_estados else ""
        estado_actual = st.selectbox("Estado", lista_estados, key="estado_real", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    df_estado = df[df[COL_EST] == estado_actual] if COL_EST else df
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique()) if COL_SUC else []
    with f2:
        st.markdown(f'<div class="filter-pill"><div class="filter-label">🏬 Sucursales • {len(lista_suc)} en {estado_actual}</div>', unsafe_allow_html=True)
        if "sucursal_real" not in st.session_state or st.session_state["sucursal_real"] not in lista_suc:
            if default_suc and default_suc in lista_suc: st.session_state["sucursal_real"] = default_suc
            elif lista_suc: st.session_state["sucursal_real"] = lista_suc[0]
        sucursal_actual = st.selectbox("Sucursales", lista_suc, key="sucursal_real", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        # FIX: no resetear filtro
        pass
    with f3:
        st.markdown('<div class="filter-pill"><div class="filter-label">⚡ Acciones</div>', unsafe_allow_html=True)
        ca1, ca2 = st.columns(2)
        with ca1:
            if st.button("🔄", width='stretch', help="Actualizar"):
                st.cache_data.clear()
                st.rerun()
        with ca2:
            if st.button("➕", width='stretch', help="Agregar reporte"):
                st.session_state['show_login'] = True
                st.session_state['show_add_form'] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.session_state['prev_estado_real'] = st.session_state.get('estado_real')
    st.session_state['prev_sucursal_real'] = st.session_state.get('sucursal_real')
else:
    estado_actual = st.session_state.get('estado_real', lista_estados[0] if lista_estados else "")
    df_estado = df[df[COL_EST] == estado_actual] if COL_EST else df
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique()) if COL_SUC else []
    sucursal_actual = st.session_state.get('sucursal_real', lista_suc[0] if lista_suc else "")

if st.session_state['show_login'] and not st.session_state['admin_auth']:
    st.markdown('<div class="glass" style="border:2px solid #0f172a; padding:24px">', unsafe_allow_html=True)
    st.markdown("### 🔐 Login Administrador")
    u = st.text_input("Usuario", placeholder="Ingresa tu usuario", key="login_user")
    p = st.text_input("Contraseña", type="password", key="login_pwd")
    cl1, cl2 = st.columns(2)
    with cl1:
        if st.button("Ingresar", type="primary", width='stretch'):
            if check_login(u.lower().strip(), p):
                st.session_state['admin_auth'] = True
                st.session_state['current_user'] = u.lower().strip()
                st.session_state['show_login'] = False
                st.session_state['show_add_form'] = True
                log_acceso(u.lower().strip(), "Login exitoso")
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos")
    with cl2:
        if st.button("Cancelar", width='stretch'):
            st.session_state['show_login'] = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state['admin_auth'] and st.session_state['show_add_form']:
    st.markdown('<div class="glass" style="border:2px solid #16a34a; padding:28px">', unsafe_allow_html=True)
    st.markdown(f"### ➕ Agregar Reporte - Usuario: **{st.session_state['current_user']}** - PRUEBAS REALES")
    id_display = SHEET_ID_PRUEBAS[:20] + "..." if SHEET_ID_PRUEBAS else "Cargado desde Streamlit Secrets"
    st.info(f"Hoja pruebas ID: {id_display} | Modo lote: agrega N reportes y al final guarda todo")
    st.markdown("#### 1⃣ Selecciona Estado y Sucursal")
    fc_sel1, fc_sel2 = st.columns(2)
    with fc_sel1:
        est_new = st.selectbox("Estado del reporte", lista_estados, index=lista_estados.index(estado_actual) if estado_actual in lista_estados else 0, key="form_est_outside")
    est_new_clean = str(est_new).strip().upper()
    df_suc_filtro = df[df[COL_EST].str.strip().str.upper() == est_new_clean] if COL_EST else df
    lista_suc_filtro = sorted(df_suc_filtro[COL_SUC].dropna().unique()) if COL_SUC else []
    with fc_sel2:
        opciones_suc = lista_suc_filtro + ["➕ Otra / Nueva sucursal..."]
        idx_def = lista_suc_filtro.index(sucursal_actual) if sucursal_actual in lista_suc_filtro else 0
        suc_sel = st.selectbox(f"Sucursal - {len(lista_suc_filtro)} en {est_new_clean}", opciones_suc, index=idx_def, key=f"form_suc_outside_{est_new_clean}")
    if suc_sel == "➕ Otra / Nueva sucursal...":
        suc_new = st.text_input("Escribe nueva sucursal *", placeholder="Ej: CORDOBA", key="form_suc_new_text")
        lineas_sucursal = []
    else:
        suc_new = suc_sel
        fila_suc = df_suc_filtro[df_suc_filtro[COL_SUC] == suc_new] if COL_SUC else pd.DataFrame()
        if not fila_suc.empty: lineas_sucursal = split_tels(fila_suc.iloc[0].get(COL_TEL, ""))
        else: lineas_sucursal = []
    st.markdown("---")
    st.markdown("#### 2⃣ Lineas con falla")
    if lineas_sucursal:
        cols_lineas = st.columns(2)
        seleccionadas = []
        for i, linea in enumerate(lineas_sucursal):
            with cols_lineas[i % 2]:
                if st.checkbox(f"{linea}", key=f"chk_linea_{est_new}_{suc_new}_{i}"): seleccionadas.append(linea)
        if seleccionadas: st.info(f"Con falla: {', '.join(seleccionadas)}")
        tel_extra = st.text_input("¿Otra linea no listada? (opcional)", placeholder="551-999-8888", key="tel_extra_outside")
        if tel_extra: seleccionadas.append(tel_extra)
        tel_final = ", ".join(seleccionadas)
    else:
        st.info("Sin lineas registradas o sucursal nueva")
        tel_final = st.text_input("Lineas con falla", placeholder="551-102-2050", key="tel_new_suc_outside")
        seleccionadas = [tel_final] if tel_final else []
    st.markdown("---")
    st.markdown("#### 3⃣ Datos del reporte")
    st.markdown(f"**Resumen:** Estado: {est_new} | Sucursal: {suc_new} | Lineas: {tel_final if tel_final else 'Ninguna'}")
    with st.form("form_reporte_final", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1: rep_new = st.text_input("No. Reporte *", placeholder="45163", key="form_rep_final")
        with fc2: fec_new = st.date_input("Fecha Reporte", value=now_mx().date(), max_value=now_mx().date(), key="form_fec_final")
        obs_new = st.text_area("📝 Observaciones / Falla reportada *", placeholder="Ej: falla, sin linea, ruido...", height=90, key="form_obs_final")
        st.markdown("---")
        c1f, c2f = st.columns([0.7, 1.3])
        with c1f: btn_close = st.form_submit_button("Cerrar formulario", width='stretch')
        with c2f: btn_add = st.form_submit_button("➕ AGREGAR REPORTE A LA LISTA", type="primary", width='stretch')
        if btn_close:
            log_acceso(st.session_state['current_user'], "Cerro formulario y logout")
            st.session_state['admin_auth'] = False
            st.session_state['show_add_form'] = False
            st.session_state['show_login'] = False
            st.session_state['current_user'] = None
            st.session_state['batch_reportes'] = []
            st.rerun()
        if btn_add:
            rep_new_clean = str(rep_new).strip()
            try: reportes_activos_existentes = [str(r).strip() for r in df[COL_REP].dropna().tolist() if tiene_reporte(r)] if COL_REP in df.columns else []
            except: reportes_activos_existentes = []
            try: reportes_en_cola = [str(r['no_reporte']).strip() for r in st.session_state.get('batch_reportes', [])]
            except: reportes_en_cola = []
            if not rep_new_clean: st.error("No. Reporte obligatorio")
            elif not rep_new_clean.isdigit(): st.error("❌ Solo numeros")
            elif not suc_new: st.error("Sucursal obligatoria")
            elif not tel_final: st.error("Selecciona al menos una linea")
            elif not obs_new: st.error("Observaciones obligatoria")
            elif fec_new > now_mx().date(): st.error("❌ Fecha futura no permitida")
            else:
                nuevo = {"estado": est_new, "sucursal": suc_new, "tel": tel_final, "no_reporte": rep_new_clean, "fecha_reporte": fec_new.strftime("%d/%m/%Y"), "obs": obs_new}
                st.session_state['batch_reportes'].append(nuevo)
                st.success(f"✅ Reporte {rep_new_clean} agregado - Total: {len(st.session_state['batch_reportes'])}")
                st.session_state['clear_after_add'] = True
                st.rerun()
    if st.session_state.get('clear_after_add'):
        for k in list(st.session_state.keys()):
            if k.startswith("chk_linea_"): del st.session_state[k]
        for k in ["form_rep_final", "form_obs_final", "tel_extra_outside", "tel_new_suc_outside"]:
            if k in st.session_state:
                try: del st.session_state[k]
                except: pass
        st.session_state['clear_after_add'] = False
        st.rerun()
    if st.session_state['batch_reportes']:
        st.markdown("---")
        st.markdown(f"#### 📋 Reportes en cola ({len(st.session_state['batch_reportes'])}) - Aun no guardados")
        for idx, r in enumerate(st.session_state['batch_reportes']):
            col_r1, col_r2 = st.columns([5,1])
            with col_r1:
                st.markdown(f"<div style='background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #16a34a; padding:10px 14px; border-radius:10px; margin-bottom:8px'><b>{idx+1}. {r['sucursal']} ({r['estado']})</b> - REP: {r['no_reporte']} - Lineas: {r['tel']}<br><small>{r['obs'][:100]}</small></div>", unsafe_allow_html=True)
            with col_r2:
                if st.button("❌", key=f"del_batch_{idx}_{r['no_reporte']}"):
                    st.session_state['batch_reportes'].pop(idx)
                    st.rerun()
        st.markdown("---")
        c_save1, c_save2 = st.columns([0.5, 1.5])
        with c_save1:
            if st.button("🗑 Limpiar lista", width='stretch'):
                st.session_state['batch_reportes'] = []
                st.rerun()
        with c_save2:
            if st.button(f"💾 GUARDAR LOS {len(st.session_state['batch_reportes'])} REPORTES EN GOOGLE SHEETS (PRUEBA REAL)", type="primary", width='stretch'):
                try:
                    guardados = 0
                    if "gcp_service_account" in st.secrets:
                        import gspread
                        from google.oauth2.service_account import Credentials
                        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
                        client = gspread.authorize(creds)
                        try:
                            sh = client.open_by_key(ID_CORRECTO_SHEETS)
                        except:
                            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
                            sh = client.open_by_key(sheet_id)
                        # FIX: SIEMPRE BDSUCURSALES2
                        try: ws_main = sh.worksheet(SHEET_PRINCIPAL)
                        except: ws_main = sh.worksheet("BDSUCURSALES")
                        headers = ws_main.row_values(1)
                        headers_upper = [h.strip().upper() for h in headers]
                        def find_idx(kws):
                            for i, h in enumerate(headers_upper):
                                for kw in kws:
                                    if kw in h: return i+1
                            return None
                        col_est_idx = find_idx(['ESTADO','EDO'])
                        col_suc_idx = find_idx(['SUCURSAL','SUC','SITIO'])
                        col_rep_idx = find_idx(['NO. REPORTE','NO REPORTE','REPORTE'])
                        col_fec_idx = find_idx(['FECHA DE REPORTE','FECHA REPORTE','FECHA','FEC'])
                        col_falla_idx = find_idx(['FALLA','OBSERVACIONES','OBS','COMENTARIO'])
                        col_tel_idx = find_idx(['TELMEX','TEL','LINEA'])
                        # FIX: detectar columna LINEAS CON FALLA
                        col_tel_falla_idx = None
                        try:
                            header = [h.strip().upper() for h in ws_main.row_values(1)]
                            for idx_h, h in enumerate(header):
                                if any(k in h for k in ['LINEAS CON FALLA','LINEA CON FALLA','TEL FALLA','LINEA FALLA','LINEA REPORTADA']):
                                    col_tel_falla_idx = idx_h+1
                                    break
                        except: pass
                        all_vals = ws_main.get_all_values()
                        for r in st.session_state['batch_reportes']:
                            row_found = None
                            last_estado_g = ""
                            import unicodedata
                            def clean_norm_g(s):
                                s = str(s).strip()
                                if not s: return ""
                                s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                                s = s.upper()
                                s = re.sub(r'\s+', ' ', s)
                                return s.strip()
                            for idx_row in range(1, len(all_vals)):
                                row = all_vals[idx_row]
                                try:
                                    est_raw = row[col_est_idx-1] if col_est_idx and col_est_idx-1 < len(row) else ""
                                    suc_raw = row[col_suc_idx-1] if col_suc_idx and col_suc_idx-1 < len(row) else ""
                                    if est_raw and str(est_raw).strip(): last_estado_g = est_raw
                                    est_cell = last_estado_g if last_estado_g else est_raw
                                    if clean_norm_g(est_cell) == clean_norm_g(r['estado']) and clean_norm_g(suc_raw) == clean_norm_g(r['sucursal']):
                                        row_found = idx_row+1
                                        break
                                except: continue
                            if row_found:
                                cur_rep = all_vals[row_found-1][col_rep_idx-1] if col_rep_idx and col_rep_idx-1 < len(all_vals[row_found-1]) else ""
                                cur_fec = all_vals[row_found-1][col_fec_idx-1] if col_fec_idx and col_fec_idx-1 < len(all_vals[row_found-1]) else ""
                                cur_falla = all_vals[row_found-1][col_falla_idx-1] if col_falla_idx and col_falla_idx-1 < len(all_vals[row_found-1]) else ""
                                cur_tel_falla = all_vals[row_found-1][col_tel_falla_idx-1] if col_tel_falla_idx and col_tel_falla_idx-1 < len(all_vals[row_found-1]) else ""
                                ex_reps = split_multi_val(cur_rep)
                                ex_fecs = split_multi_val(cur_fec)
                                ex_fallas = split_multi_val(cur_falla)
                                ex_tel_falla = split_multi_val(cur_tel_falla)
                                ex_reps.append(r['no_reporte']); ex_fecs.append(r['fecha_reporte'])
                                ex_fallas.append(sanitize_sheets_input(r['obs'],500)); ex_tel_falla.append(sanitize_sheets_input(r.get('tel',''),200))
                                if col_rep_idx: ws_main.update_cell(row_found, col_rep_idx, join_multi_val(ex_reps))
                                if col_fec_idx: ws_main.update_cell(row_found, col_fec_idx, join_multi_val(ex_fecs))
                                if col_falla_idx: ws_main.update_cell(row_found, col_falla_idx, join_multi_val(ex_fallas))
                                if col_tel_falla_idx: ws_main.update_cell(row_found, col_tel_falla_idx, join_multi_val(ex_tel_falla))
                                # Actualizar cache local
                            else:
                                # FIX: NUEVA SUCURSAL CON LINEAS CON FALLA
                                new_row = [""] * len(headers)
                                if col_est_idx: new_row[col_est_idx-1] = r['estado']
                                if col_suc_idx: new_row[col_suc_idx-1] = r['sucursal']
                                if col_tel_idx: new_row[col_tel_idx-1] = r['tel']
                                if col_rep_idx: new_row[col_rep_idx-1] = r['no_reporte']
                                if col_fec_idx: new_row[col_fec_idx-1] = r['fecha_reporte']
                                if col_falla_idx: new_row[col_falla_idx-1] = r['obs']
                                if col_tel_falla_idx: new_row[col_tel_falla_idx-1] = r['tel']
                                ws_main.append_row(new_row, value_input_option='USER_ENTERED')
                                all_vals.append(new_row)
                            log_reporte_historial(st.session_state['current_user'], r['estado'], r['sucursal'], r['no_reporte'], r['fecha_reporte'], r['tel'], r['obs'])
                            guardados += 1
                        log_acceso(st.session_state['current_user'], f"Guardo lote PRUEBA {guardados} reportes")
                        st.success(f"✅ {guardados} reportes guardados en {SHEET_PRINCIPAL}")
                        st.session_state['batch_reportes'] = []
                        # FIX 3: LIMPIAR CACHE Y RESETEAR BOX REPORTES ACTIVOS SIN ERROR
                        st.cache_data.clear()
                        st.session_state['reset_filtro_pendiente'] = True
                        st.balloons()
                        time.sleep(1.5)
                        st.session_state['admin_auth'] = False
                        st.session_state['show_add_form'] = False
                        st.session_state['show_login'] = False
                        st.session_state['current_user'] = None
                        st.rerun()
                    else:
                        for r in st.session_state['batch_reportes']:
                            log_reporte_historial(st.session_state['current_user'], r['estado'], r['sucursal'], r['no_reporte'], r['fecha_reporte'], r['tel'], r['obs'])
                            guardados += 1
                        st.success(f"✅ DEMO: {guardados} reportes guardados en memoria")
                        st.balloons()
                        time.sleep(1)
                        st.session_state['batch_reportes'] = []
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)

# DETALLE
if not st.session_state.get('show_add_form', False):
    if 'estado_real' in st.session_state and 'sucursal_real' in st.session_state and COL_EST and COL_SUC:
        estado_sel = st.session_state['estado_real']
        suc_sel = st.session_state['sucursal_real']
        if estado_sel in df[COL_EST].values:
            df_filtro = df[(df[COL_EST] == estado_sel) & (df[COL_SUC] == suc_sel)]
            if not df_filtro.empty:
                for _, row in df_filtro.iterrows():
                    rep_raw = str(row.get(COL_REP, "")).strip() if COL_REP else ""
                    fec_raw = str(row.get(COL_FEC, "")).strip() if COL_FEC else ""
                    obs_raw = str(row.get(COL_OBS, "")).strip() if COL_OBS else ""
                    tel_raw = row.get(COL_TEL, "") if COL_TEL else ""
                    tel_falla_raw = str(row.get(COL_TEL_FALLA, "")).strip() if 'COL_TEL_FALLA' in locals() and COL_TEL_FALLA and COL_TEL_FALLA in row else ""
                    tels = split_tels(tel_raw)
                    reps_list = split_multi_val(rep_raw)
                    fecs_list = split_multi_val(fec_raw)
                    obs_list = split_multi_val(obs_raw)
                    tel_falla_list = split_multi_val(tel_falla_raw) if tel_falla_raw else []
                    if not reps_list or not any(tiene_reporte(r) for r in reps_list):
                        st.markdown(f"""<div class="glass" style="padding:20px; border-left:5px solid #16a34a; background: rgba(240,253,244,0.5) !important;"><div style="display:flex; justify-content:space-between;"><div><div style="font-size:1.2rem; font-weight:900;">{suc_sel}</div><div style="display:flex; gap:8px; margin-top:8px;"><span class="rep-box" style="background:#0f172a; color:white;">📍 {estado_sel}</span><span class="rep-box" style="background:#f0fdf4; color:#166534;">✅ Sin REP</span></div></div><span class="badge badge-ok">Sin reporte</span></div></div>""", unsafe_allow_html=True)
                    else:
                        todas_fallas_union = set()
                        for tf in tel_falla_list:
                            for part in str(tf).split(','): 
                                p = part.strip()
                                if p: todas_fallas_union.add(p.strip())
                        for idx_rep, rep in enumerate(reps_list):
                            fec = fecs_list[idx_rep] if idx_rep < len(fecs_list) else (fecs_list[0] if fecs_list else "")
                            obs = obs_list[idx_rep] if idx_rep < len(obs_list) else (obs_list[0] if obs_list else obs_raw)
                            tel_falla_cur = tel_falla_list[idx_rep] if idx_rep < len(tel_falla_list) else (tel_falla_list[0] if tel_falla_list else "")
                            dias, txt_dias = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin reporte")
                            if not tiene_reporte(rep): badge_html = '<span class="badge badge-ok">Sin reporte</span>'; border_color="#16a34a"; border_bg="rgba(240,253,244,0.5)"
                            else:
                                if dias is None: badge_html = f'<span class="badge badge-warn">{txt_dias}</span>'; border_color="#f59e0b"; border_bg="rgba(254,249,195,0.5)"
                                elif dias <= 2: badge_html = f'<span class="badge badge-warn">{dias} dias</span>'; border_color="#f59e0b"; border_bg="rgba(254,249,195,0.5)"
                                elif dias <= 5: badge_html = f'<span class="badge badge-orange">{dias} dias</span>'; border_color="#f97316"; border_bg="rgba(255,237,213,0.5)"
                                else: badge_html = f'<span class="badge badge-red">{txt_dias}</span>'; border_color="#ef4444"; border_bg="rgba(254,242,242,0.5)"
                            rep_display = f'<span class="rep-box">🗂 REP: {rep} ({idx_rep+1}/{len(reps_list)})</span>' if len(reps_list)>1 else f'<span class="rep-box">🗂 REP: {rep}</span>'
                            fecha_display = f'<span class="rep-box">📅 Fecha: {fec}</span>' if fec else '<span class="rep-box">📅 Fecha: N/A</span>'
                            estado_display = f'<span class="rep-box" style="background:#0f172a; color:white;">📍 {estado_sel}</span>'
                            tel_falla_display = f'<div style="margin-top:8px; padding:8px 10px; background:#fef2f2; border:1px solid #fecaca; border-radius:8px;"><div style="font-size:0.68rem; font-weight:800; color:#b91c1c;">🚨 LINEAS CON FALLA: {tel_falla_cur if tel_falla_cur else "No especificadas"}</div></div>' if tel_falla_cur else ""
                            st.markdown(f"""<div class="glass" style="padding:20px; border-left:5px solid {border_color}; background: {border_bg} !important; margin-bottom:12px;"><div style="display:flex; justify-content:space-between;"><div><div style="font-size:1.2rem; font-weight:900;">{suc_sel} - REPORTE {idx_rep+1}/{len(reps_list)}</div><div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">{estado_display}{rep_display}{fecha_display}</div>{tel_falla_display}</div><div>{badge_html}</div></div><div style="margin-top:14px; display:flex; gap:12px;"><div style="flex:2; padding:12px 14px; background:#f8fafc; border:1px solid #f1f5f9; border-radius:10px;"><div style="font-size:0.70rem; font-weight:800; color:#64748b;">📝 FALLA REPORTADA</div><div style="color:#1e293b; font-size:0.92rem;">{obs if obs and obs.lower()!='nan' else 'Sin observaciones'}</div></div></div></div>""", unsafe_allow_html=True)
                            c_btn1, c_btn2 = st.columns([2.2, 0.8])
                            with c_btn1: st.markdown("<div style='font-size:0.70rem; color:#64748b; padding-top:8px;'>💡 Al cerrar se limpiará solo este REPORTE de BDSUCURSALES. Se guardará log en HISTORIAL_REPORTES.</div>", unsafe_allow_html=True)
                            with c_btn2:
                                if st.button(f"✅ CERRAR REPORTE {rep}", key=f"btn_cerrar_{estado_sel}_{suc_sel}_{idx_rep}_{rep}", type="primary", width='stretch'):
                                    st.session_state['delete_target'] = {"estado": estado_sel, "sucursal": suc_sel, "rep": rep, "fec": fec, "obs": obs, "tel": tel_raw, "indice": idx_rep}
                                    if not st.session_state.get('admin_auth'):
                                        st.session_state['show_delete_login'] = True
                                        st.session_state['show_delete_confirm'] = False
                                    else:
                                        st.session_state['show_delete_confirm'] = True
                                        st.session_state['show_delete_login'] = False
                                    st.rerun()
                        if tels:
                            resumen_fallas = ", ".join(sorted(todas_fallas_union)) if todas_fallas_union else "N/A"
                            st.markdown(f"<div style='margin-top:18px; margin-bottom:10px; padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; display:flex; justify-content:space-between;'><div style='font-weight:700; font-size:0.85rem;'>☎ LINEAS TELEFONICAS • {len(tels)} numeros</div><div style='font-size:0.75rem; color:#b91c1c; font-weight:600;'>🔴 En falla: {resumen_fallas}</div></div>", unsafe_allow_html=True)
                            cols = st.columns(2)
                            for i, t in enumerate(tels):
                                is_falla = t.strip() in todas_fallas_union
                                with cols[i % 2]:
                                    if is_falla:
                                        st.markdown(f"""<div style="background:#fef2f2; border:2px solid #ef4444; border-radius:12px; padding:10px 14px; display:flex; gap:10px; margin-bottom:10px;"><div style="width:28px; height:28px; background:#ef4444; border-radius:8px; display:flex; align-items:center; justify-content:center; color:white;">🚨</div><div><div style="font-size:0.65rem; font-weight:700; color:#b91c1c;">LINEA CON FALLA</div><div style="font-weight:700; font-size:0.95rem; color:#991b1b;">{t}</div></div></div>""", unsafe_allow_html=True)
                                    else:
                                        st.markdown(f"""<div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:10px 14px; display:flex; gap:10px; margin-bottom:10px;"><div style="width:28px; height:28px; background:#e2e8f0; border-radius:8px; display:flex; align-items:center; justify-content:center;">📞</div><div style="font-weight:600; font-size:0.9rem;">{t}</div></div>""", unsafe_allow_html=True)

if st.session_state.get('show_delete_login') and not st.session_state.get('admin_auth'):
    st.markdown('<div class="glass" style="border:2px solid #dc2626; padding:24px; margin-top:16px; background:rgba(254,242,242,0.95) !important;">', unsafe_allow_html=True)
    st.markdown("### 🔒 Login para CERRAR REPORTE")
    target = st.session_state.get('delete_target', {})
    st.markdown(f"""<div style="background:#fef2f2; border:1px solid #fecaca; border-left:5px solid #dc2626; padding:12px 16px; border-radius:8px; margin:10px 0;"><b style="color:#991b1b;">⚠ ADVERTENCIA: Vas a CERRAR un reporte activo</b><br><b>Sucursal:</b> {target.get('sucursal','')} - {target.get('estado','')}<br><b>No. REPORTE:</b> {target.get('rep','')}<br></div>""", unsafe_allow_html=True)
    u_del = st.text_input("Usuario Administrador", key="delete_login_user", placeholder="Ingresa tu usuario")
    p_del = st.text_input("Contraseña", type="password", key="delete_login_pwd", placeholder="Ingresa tu contraseña")
    cd1, cd2 = st.columns(2)
    with cd1:
        if st.button("❌ Cancelar", key="cancel_delete_login", width='stretch'):
            st.session_state['show_delete_login'] = False
            st.session_state['delete_target'] = None
            st.rerun()
    with cd2:
        if st.button("🔐 Ingresar y Continuar", key="confirm_delete_login", type="primary", width='stretch'):
            if check_login(u_del, p_del):
                st.session_state['admin_auth'] = True
                st.session_state['current_user'] = u_del
                st.session_state['show_delete_login'] = False
                st.session_state['show_delete_confirm'] = True
                log_acceso(u_del, f"Login para CERRAR REPORTE {target.get('rep','')} {target.get('sucursal','')}")
                st.rerun()
            else: st.error("Usuario o contraseña incorrectos")
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.get('show_delete_confirm'):
    target = st.session_state.get('delete_target', {})
    if target:
        st.markdown('<div class="glass" style="border:2px solid #ef4444; background:rgba(254,242,242,0.8) !important; padding:24px; margin-top:16px;">', unsafe_allow_html=True)
        st.markdown(f"### ✅ Confirmar Cierre de Reporte")
        st.markdown(f"""<div style="background:white; border:1px solid #fecaca; border-left:5px solid #ef4444; padding:16px; border-radius:10px; margin:12px 0;"><b>Estado:</b> {target.get('estado')}<br><b>Sucursal:</b> {target.get('sucursal')}<br><b>No. REPORTE:</b> {target.get('rep')}<br><b>Fecha:</b> {target.get('fec')}<br><b>Falla:</b> {target.get('obs','')[:250]}<br><br><div style="background:#fef2f2; border:1px solid #fecaca; padding:12px; border-radius:8px;"><b style="color:#b91c1c;">⚠ ADVERTENCIA - ACCIÓN EN {SHEET_PRINCIPAL}</b><br><div style="font-size:0.85rem; color:#7f1d1d; margin-top:6px;">Se limpiará NO. REPORTE, FECHA y FALLA en {SHEET_PRINCIPAL} y se guardará cierre en HISTORIAL_REPORTES</div></div></div>""", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("❌ No, Cancelar", key="cancel_delete_final", width='stretch'):
                st.session_state['show_delete_confirm'] = False
                st.session_state['delete_target'] = None
                st.session_state['show_delete_login'] = False
                st.rerun()
        with cc2:
            if st.button("✅ Sí, CERRAR REPORTE", key="confirm_delete_final", type="primary", width='stretch'):
                try:
                    with st.spinner(f"Cerrando reporte en {SHEET_PRINCIPAL}..."):
                        ok, msg = eliminar_reporte_hoja1(target['estado'], target['sucursal'], target['rep'], target.get('indice', None))
                        if ok:
                            log_eliminacion_historial(st.session_state.get('current_user','sistema'), target['estado'], target['sucursal'], target['rep'], target['fec'], target['obs'])
                            log_acceso(st.session_state.get('current_user','sistema'), f"CERRO REPORTE {target['rep']} {target['sucursal']} - {target['estado']}")
                            st.success(f"✅ Reporte {target['rep']} CERRADO correctamente en {SHEET_PRINCIPAL}.")
                            st.balloons()
                            time.sleep(1.5)
                            st.session_state['show_delete_confirm'] = False
                            st.session_state['delete_target'] = None
                            st.session_state['show_delete_login'] = False
                            # FIX: limpiar cache y resetear box SIN ERROR
                            st.cache_data.clear()
                            st.session_state['reset_filtro_pendiente'] = True
                            st.rerun()
                        else: st.error(f"Error al cerrar: {msg}")
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)
