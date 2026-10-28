import streamlit as st
import pandas as pd
from datetime import datetime
import re
import time
import base64

# LOGO
try:
    with open("image_af8068.png", "rb") as f:
        b64_logo = base64.b64encode(f.read()).decode()
except:
    try:
        with open("/mnt/data/image_af8068.png", "rb") as f:
            b64_logo = base64.b64encode(f.read()).decode()
    except:
        b64_logo = ""

st.set_page_config(page_title="SUCURSALES - PRUEBAS REALES", layout="wide", page_icon="🏢")

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

SHEET_ID_PRUEBAS = "12uBzVEE5ZqO7V6OIKSlCTB7BdSQWk_3sn12LhFdMWg4"

def norm(s):
    return str(s).strip().upper().replace("  "," ").replace("\n","").replace("\r","")

@st.cache_data(ttl=20, show_spinner=False)
def cargar_datos(sheet_id_override=None):
    df_privado = None
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
            client = gspread.authorize(creds)
            sid = sheet_id_override or st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            if sid:
                sh = client.open_by_key(sid)
                try:
                    ws = sh.worksheet("BDSUCURSALES")
                except:
                    try:
                        ws = sh.worksheet("BDSUCURSALES2")
                    except:
                        ws = sh.sheet1
                data = ws.get_all_records()
                if data and len(data) > 0:
                    df_tmp = pd.DataFrame(data)
                    df_tmp.columns = df_tmp.columns.str.strip().str.upper()
                    df_tmp = df_tmp.dropna(how='all')
                    if len(df_tmp) >= 1:
                        df_privado = df_tmp
    except:
        pass
    if df_privado is not None and not df_privado.empty and len(df_privado) > 5:
        return df_privado
    try:
        base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTySrWdMEtPBo7u4r6df8shaedXk8783RUOdOPsjLwIh1xz4nLHdAdaheYFMB1-CLI2XtzpzLa7SQXm/pub?output=csv"
        url = f"{base_url}&cb={int(time.time())}"
        df = pd.read_csv(url, dtype=str)
        df.columns = df.columns.str.strip().str.upper()
        return df.dropna(how='all')
    except Exception as e:
        if df_privado is not None:
            return df_privado
        return pd.DataFrame(columns=["ESTADO","SUCURSAL","TELMEX","NO. REPORTE","FECHA","OBSERVACIONES"])

df = cargar_datos()

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

if COL_EST and not df.empty:
    df[COL_EST] = df[COL_EST].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
if COL_SUC and not df.empty:
    df[COL_SUC] = df[COL_SUC].astype(str).str.strip()

def tiene_reporte(v):
    if pd.isna(v): return False
    return str(v).strip().lower() not in ["","0","0.0","sin reporte","none","nan","vacio","s/r"]

def dias_desde(fecha_str):
    if not fecha_str or str(fecha_str).lower() in ['nan','none','']: return None, "Sin fecha"
    dt = pd.to_datetime(fecha_str, errors='coerce', dayfirst=True)
    if pd.isna(dt): return None, "Fecha invalida"
    diff = (datetime.now() - dt).days
    if diff < 0:
        return diff, "Fecha futura"
    if diff == 0:
        return diff, "Hoy"
    elif diff == 1:
        return diff, "1 dia"
    elif diff <= 2:
        return diff, f"{diff} dias"
    elif diff <= 5:
        return diff, f"{diff} dias"
    else:
        return diff, f"{diff} dias - Critico"

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
        if re.match(r'^\d{3}-\d{3}-\d{4}$', p):
            tels.append(p)
        elif re.match(r'^\d{10}$', p):
            tels.append(f"{p[:3]}-{p[3:6]}-{p[6:]}")
        elif '-' in p and len(p)>=7:
            tels.append(p)
    if not tels:
        raw_tels = [t.strip() for t in re.split(r'[\n,;/]+', str(raw)) if t.strip() and t.strip().lower()!='nan']
        for item in raw_tels:
            encontrados = re.findall(r'\d{3}[-\s]?\d{3}[-\s]?\d{4}|\d{10}', item)
            if encontrados:
                for e in encontrados:
                    e = e.replace(' ', '-')
                    if len(e)==10 and '-' not in e:
                        e = f"{e[:3]}-{e[3:6]}-{e[6:]}"
                    tels.append(e)
            else:
                tels.append(item)
    seen=set(); uniq=[]
    for t in tels:
        if t not in seen:
            seen.add(t); uniq.append(t)
    return uniq

USUARIOS = {"yair": "AtlasY", "francisco": "AtlasF"}

def check_login(user, pwd):
    try:
        if "users" in st.secrets:
            users_secret = st.secrets["users"]
            return user in users_secret and users_secret[user] == pwd
        else:
            return USUARIOS.get(user) == pwd
    except:
        return USUARIOS.get(user) == pwd

def log_acceso(usuario, accion="Login"):
    now = datetime.now()
    fecha = now.strftime("%d/%m/%Y")
    hora = now.strftime("%H:%M:%S")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("LOG_ACCESOS")
            except:
                ws = sh.add_worksheet(title="LOG_ACCESOS", rows=1000, cols=10)
                ws.append_row(["FECHA", "HORA", "USUARIO", "ACCION", "DETALLE"])
            ws.append_row([fecha, hora, usuario, accion, "Acceso desde app"])
    except:
        pass

def log_reporte_historial(usuario, estado, sucursal, no_reporte, fecha_reporte, tel="", observaciones=""):
    now = datetime.now()
    fecha_reg = now.strftime("%d/%m/%Y")
    hora_reg = now.strftime("%H:%M:%S")
    mes = now.strftime("%m")
    anio = now.strftime("%Y")
    dia = now.strftime("%d")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=5000, cols=15)
                ws.append_row(["FECHA_REGISTRO", "HORA_REGISTRO", "DIA", "MES", "ANIO", "USUARIO", "ESTADO", "SUCURSAL", "NO_REPORTE", "FECHA_REPORTE", "TEL", "OBSERVACIONES"])
            ws.append_row([fecha_reg, hora_reg, dia, mes, anio, usuario, estado, sucursal, no_reporte, fecha_reporte, tel, observaciones])
            return True
    except Exception as e:
        return False
    return True

lista_estados = sorted(df[COL_EST].dropna().unique()) if COL_EST in df.columns else []
df_reportes = df[df[COL_REP].apply(tiene_reporte)] if COL_REP and COL_REP in df.columns else pd.DataFrame()

for k in ['admin_auth','show_login','show_add_form','current_user','batch_reportes','show_close_login','show_close_confirm','close_target','close_auth','close_user','last_logged_suc','last_visita_log','visitas_demo','filtro_activo_sel']:
    if k not in st.session_state:
        st.session_state[k] = False if 'auth' in k or 'show' in k else ([] if 'batch' in k or 'visitas' in k or 'demo' in k else None)
if 'visitas_demo' not in st.session_state: st.session_state['visitas_demo']=[]
if 'batch_reportes' not in st.session_state: st.session_state['batch_reportes']=[]
if 'filtro_activo_sel' not in st.session_state: st.session_state['filtro_activo_sel']="-- Ver todas las sucursales --"

# --- PREPARAR OPCIONES REPORTES ACTIVOS (para header) ---
opciones_activas = []
mapa_activos = {}
mapa_activos_global = {}
if not df_reportes.empty:
    for _, row in df_reportes.iterrows():
        estado = str(row.get(COL_EST, "")).strip()
        suc = str(row.get(COL_SUC, "")).strip()
        rep = str(row.get(COL_REP, "")).strip()
        fec = str(row.get(COL_FEC, "")).strip()
        dias, txt_dias = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin fecha")
        label = f"{suc} - {estado} | REP: {rep} | {txt_dias}"
        opciones_activas.append(label)
        mapa_activos[label] = {"estado": estado, "sucursal": suc, "row": row}
    opciones_activas = sorted(opciones_activas)
    mapa_activos_global = mapa_activos
opciones_con_todos = ["-- Ver todas las sucursales --"] + opciones_activas

# HEADER - c1 titulo, c2 reportes + filtro del mismo tamaño
c1, c2 = st.columns([2.2, 1.3])
with c1:
    if b64_logo:
        st.markdown(f"""<div style="display:flex; align-items:center; gap:16px"><div style="width:52px; height:52px; border-radius:14px; overflow:hidden; background:white"><img src="data:image/png;base64,{b64_logo}" style="width:100%; height:100%; object-fit:cover"></div><div style="font-size:2rem; font-weight:900; letter-spacing:-0.8px">SUCURSALES - PRUEBAS</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="font-size:2rem; font-weight:900;">SUCURSALES - PRUEBAS</div>""", unsafe_allow_html=True)
with c2:
    # Recuadro negro Reportes Activos
    st.markdown(f"""<div class="glass-dark"><div style="display:flex; justify-content:space-between; align-items:center"><div style="display:flex; gap:10px; align-items:center"><div style="width:34px; height:34px; background:rgba(239,68,68,0.25); border-radius:9px; display:flex; align-items:center; justify-content:center">🚨</div><div><div style="font-weight:700">Reportes Activos</div><div style="font-size:0.75rem; opacity:0.7">{len(df_reportes)} requieren atencion</div></div></div><div style="font-size:1.6rem; font-weight:900">{len(df_reportes)}</div></div></div>""", unsafe_allow_html=True)

    # FILTRO - mismo tamaño que recuadro negro, justo debajo, sin boton Limpiar
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
        default_idx_activo = 0
        if st.session_state.get('filtro_activo_sel') in opciones_con_todos:
            default_idx_activo = opciones_con_todos.index(st.session_state['filtro_activo_sel'])

        # Selectbox 100% automatico - mismo ancho que recuadro negro, sin boton Limpiar
        sel_activo = st.selectbox(
            "Filtro reporte activo",
            opciones_con_todos,
            index=default_idx_activo,
            key="filtro_activo_sel",
            label_visibility="collapsed",
            placeholder="🔍 Selecciona sucursal con reporte activo..."
        )

        # Auto-navegación inmediata - SIN BOTON
        if sel_activo != "-- Ver todas las sucursales --":
            info_sel = mapa_activos.get(sel_activo)
            if info_sel:
                if st.session_state.get('estado_real') != info_sel['estado'] or st.session_state.get('sucursal_real') != info_sel['sucursal']:
                    st.session_state['estado_real'] = info_sel['estado']
                    st.session_state['sucursal_real'] = info_sel['sucursal']
                    st.rerun()
    else:
        st.markdown('<div class="glass" style="margin-top:10px; padding:10px 14px; border-left:4px solid #16a34a; background:white !important; border-radius:12px;"><div style="display:flex; align-items:center; gap:8px;"><div style="width:20px; height:20px; background:#16a34a; border-radius:6px; display:flex; align-items:center; justify-content:center; color:white; font-size:12px;">✅</div><b style="color:#166534; font-size:0.75rem;">Sin reportes activos</b></div></div>', unsafe_allow_html=True)

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
        estado_actual = st.selectbox("Estado", lista_estados, index=default_est_idx, key="estado_real", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    df_estado = df[df[COL_EST] == estado_actual] if COL_EST else df
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique()) if COL_SUC else []
    with f2:
        st.markdown(f'<div class="filter-pill"><div class="filter-label">🏬 Sucursales • {len(lista_suc)} en {estado_actual}</div>', unsafe_allow_html=True)
        idx_suc = lista_suc.index(default_suc) if default_suc and default_suc in lista_suc else 0
        sucursal_actual = st.selectbox("Sucursales", lista_suc, index=idx_suc, key="sucursal_real", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with f3:
        st.markdown('<div class="filter-pill"><div class="filter-label">⚡ Acciones</div>', unsafe_allow_html=True)
        ca1, ca2 = st.columns(2)
        with ca1:
            if st.button("🔄", use_container_width=True, help="Actualizar"):
                st.cache_data.clear()
                st.rerun()
        with ca2:
            if st.button("➕", use_container_width=True, help="Agregar reporte"):
                st.session_state['show_login'] = True
                st.session_state['show_add_form'] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    estado_actual = st.session_state.get('estado_real', lista_estados[0] if lista_estados else "")
    df_estado = df[df[COL_EST] == estado_actual] if COL_EST else df
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique()) if COL_SUC else []
    sucursal_actual = st.session_state.get('sucursal_real', lista_suc[0] if lista_suc else "")

# LOGIN
if st.session_state['show_login'] and not st.session_state['admin_auth']:
    st.markdown('<div class="glass" style="border:2px solid #0f172a; padding:24px">', unsafe_allow_html=True)
    st.markdown("### 🔐 Login Administrador")
    u = st.text_input("Usuario", placeholder="Ingresa tu usuario", key="login_user")
    p = st.text_input("Contraseña", type="password", key="login_pwd")
    cl1, cl2 = st.columns(2)
    with cl1:
        if st.button("Ingresar", type="primary", use_container_width=True):
            if check_login(u.lower().strip(), p):
                st.session_state['admin_auth'] = True
                st.session_state['current_user'] = u.lower().strip()
                st.session_state['show_login'] = False
                st.session_state['show_add_form'] = True
                log_acceso(u.lower().strip(), "Login exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    with cl2:
        if st.button("Cancelar", use_container_width=True):
            st.session_state['show_login'] = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# FORMULARIO
if st.session_state['admin_auth'] and st.session_state['show_add_form']:
    st.markdown('<div class="glass" style="border:2px solid #16a34a; padding:28px">', unsafe_allow_html=True)
    st.markdown(f"### ➕ Agregar Reporte - Usuario: **{st.session_state['current_user']}** - PRUEBAS REALES")
    st.info(f"Hoja pruebas ID: {SHEET_ID_PRUEBAS[:20]}... | Modo lote: agrega N reportes y al final guarda todo")
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
        if not fila_suc.empty:
            lineas_sucursal = split_tels(fila_suc.iloc[0].get(COL_TEL, ""))
        else:
            lineas_sucursal = []
    st.markdown("---")
    st.markdown("#### 2⃣ Lineas con falla")
    if lineas_sucursal:
        cols_lineas = st.columns(2)
        seleccionadas = []
        for i, linea in enumerate(lineas_sucursal):
            with cols_lineas[i % 2]:
                if st.checkbox(f"{linea}", key=f"chk_linea_{est_new}_{suc_new}_{i}"):
                    seleccionadas.append(linea)
        if seleccionadas:
            st.info(f"Con falla: {', '.join(seleccionadas)}")
        tel_extra = st.text_input("¿Otra linea no listada? (opcional)", placeholder="551-999-8888", key="tel_extra_outside")
        if tel_extra:
            seleccionadas.append(tel_extra)
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
        with fc1:
            rep_new = st.text_input("No. Reporte *", placeholder="45163", key="form_rep_final")
        with fc2:
            fec_new = st.date_input("Fecha Reporte", value=datetime.now().date(), max_value=datetime.now().date(), key="form_fec_final")
        obs_new = st.text_area("📝 Observaciones / Falla reportada *", placeholder="Ej: falla, sin linea, ruido...", height=90, key="form_obs_final")
        st.markdown("---")
        c1f, c2f = st.columns([0.7, 1.3])
        with c1f:
            btn_close = st.form_submit_button("Cerrar formulario", use_container_width=True)
        with c2f:
            btn_add = st.form_submit_button("➕ AGREGAR REPORTE A LA LISTA", type="primary", use_container_width=True)
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
            try:
                reportes_activos_existentes = [str(r).strip() for r in df[COL_REP].dropna().tolist() if tiene_reporte(r)] if COL_REP in df.columns else []
            except:
                reportes_activos_existentes = []
            try:
                reportes_en_cola = [str(r['no_reporte']).strip() for r in st.session_state.get('batch_reportes', [])]
            except:
                reportes_en_cola = []
            if not rep_new_clean:
                st.error("No. Reporte obligatorio")
            elif not rep_new_clean.isdigit():
                st.error("❌ Solo numeros")
            elif rep_new_clean in reportes_activos_existentes:
                st.error(f"❌ El reporte {rep_new_clean} ya existe como ACTIVO")
            elif rep_new_clean in reportes_en_cola:
                st.error(f"❌ Ya esta en la cola")
            elif not suc_new:
                st.error("Sucursal obligatoria")
            elif not tel_final:
                st.error("Selecciona al menos una linea")
            elif not obs_new:
                st.error("Observaciones obligatoria")
            elif fec_new > datetime.now().date():
                st.error("❌ Fecha futura no permitida")
            else:
                nuevo = {"estado": est_new, "sucursal": suc_new, "tel": tel_final, "no_reporte": rep_new_clean, "fecha_reporte": fec_new.strftime("%d/%m/%Y"), "obs": obs_new}
                st.session_state['batch_reportes'].append(nuevo)
                st.success(f"✅ Reporte {rep_new_clean} agregado - Total: {len(st.session_state['batch_reportes'])}")
                st.session_state['clear_after_add'] = True
                st.rerun()
    if st.session_state.get('clear_after_add'):
        for k in list(st.session_state.keys()):
            if k.startswith("chk_linea_"):
                del st.session_state[k]
        for k in ["form_rep_final", "form_obs_final", "tel_extra_outside", "tel_new_suc_outside"]:
            if k in st.session_state:
                try:
                    del st.session_state[k]
                except:
                    pass
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
            if st.button("🗑 Limpiar lista", use_container_width=True):
                st.session_state['batch_reportes'] = []
                st.rerun()
        with c_save2:
            if st.button(f"💾 GUARDAR LOS {len(st.session_state['batch_reportes'])} REPORTES EN GOOGLE SHEETS (PRUEBA REAL)", type="primary", use_container_width=True):
                try:
                    guardados = 0
                    if "gcp_service_account" in st.secrets:
                        import gspread
                        from google.oauth2.service_account import Credentials
                        import unicodedata
                        def clean_norm(s):
                            s = str(s).strip()
                            if not s:
                                return ""
                            s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                            s = s.upper()
                            s = re.sub(r'\s+', ' ', s)
                            return s.strip()
                        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
                        client = gspread.authorize(creds)
                        sheet_id = st.secrets.get("sheet_id", SHEET_ID_PRUEBAS)
                        sh = client.open_by_key(sheet_id)
                        # Priorizar BDSUCURSALES2 como pediste
                        ws_main = None
                        for name_try in ["BDSUCURSALES2", "BDSUCURSALES"]:
                            try:
                                ws_main = sh.worksheet(name_try)
                                break
                            except:
                                continue
                        if not ws_main:
                            ws_main = sh.sheet1
                        headers = ws_main.row_values(1)
                        headers_upper = [h.strip().upper() for h in headers]
                        def find_idx(kws):
                            for i, h in enumerate(headers_upper):
                                for kw in kws:
                                    if kw in h:
                                        return i+1
                            return None
                        col_est_idx = find_idx(['ESTADO','EDO']) or 1
                        col_suc_idx = find_idx(['SUCURSAL','SUC','SITIO']) or 2
                        col_rep_idx = find_idx(['NO. REPORTE','NO REPORTE','REPORTE'])
                        col_fec_idx = find_idx(['FECHA DE REPORTE','FECHA REPORTE','FECHA','FEC'])
                        col_falla_idx = find_idx(['FALLA','OBSERVACIONES','OBS','COMENTARIO'])
                        col_tel_idx = find_idx(['TELMEX','TEL','LINEA'])
                        all_vals = ws_main.get_all_values()
                        for r in st.session_state['batch_reportes']:
                            row_found = None
                            estado_clean = clean_norm(r['estado'])
                            sucursal_clean = clean_norm(r['sucursal'])
                            # Paso 1: match exacto ESTADO+SUCURSAL normalizado
                            for idx_row in range(1, len(all_vals)):
                                row = all_vals[idx_row]
                                if len(row) < max(col_est_idx, col_suc_idx):
                                    continue
                                try:
                                    est_cell = row[col_est_idx-1] if col_est_idx-1 < len(row) else ""
                                    suc_cell = row[col_suc_idx-1] if col_suc_idx-1 < len(row) else ""
                                    if clean_norm(est_cell) == estado_clean and clean_norm(suc_cell) == sucursal_clean:
                                        row_found = idx_row+1
                                        break
                                except:
                                    continue
                            # Paso 2: solo SUCURSAL
                            if not row_found:
                                for idx_row in range(1, len(all_vals)):
                                    row = all_vals[idx_row]
                                    if len(row) < col_suc_idx:
                                        continue
                                    try:
                                        suc_cell = row[col_suc_idx-1] if col_suc_idx-1 < len(row) else ""
                                        if clean_norm(suc_cell) == sucursal_clean:
                                            row_found = idx_row+1
                                            break
                                    except:
                                        continue
                            # Paso 3: contiene
                            if not row_found:
                                for idx_row in range(1, len(all_vals)):
                                    row = all_vals[idx_row]
                                    if len(row) < col_suc_idx:
                                        continue
                                    try:
                                        suc_cell = row[col_suc_idx-1] if col_suc_idx-1 < len(row) else ""
                                        if sucursal_clean in clean_norm(suc_cell) or clean_norm(suc_cell) in sucursal_clean:
                                            row_found = idx_row+1
                                            break
                                    except:
                                        continue
                            if row_found:
                                # Como pediste: borrar lo que este dentro y reemplazar por datos del formulario
                                # Limpia primero y luego escribe nuevo valor en las 3 casillas
                                if col_rep_idx:
                                    ws_main.update_cell(row_found, col_rep_idx, "")
                                    ws_main.update_cell(row_found, col_rep_idx, r['no_reporte'])
                                if col_fec_idx:
                                    ws_main.update_cell(row_found, col_fec_idx, "")
                                    ws_main.update_cell(row_found, col_fec_idx, r['fecha_reporte'])
                                if col_falla_idx:
                                    ws_main.update_cell(row_found, col_falla_idx, "")
                                    ws_main.update_cell(row_found, col_falla_idx, r['obs'])
                            else:
                                # Si no encuentra, NO crear fila duplicada - mostrar error en log pero igual guardar en historial
                                # Para evitar duplicado TIJUANA verde+rojo que viste
                                st.warning(f"⚠️ No se encontró {r['sucursal']} - {r['estado']} en {ws_main.title}, se omite para evitar duplicado. Headers: {headers[:4]}")
                                # Opcional: si quieres que aun asi cree fila, descomenta lo de abajo
                                # new_row = [""] * len(headers)
                                # if col_est_idx: new_row[col_est_idx-1] = r['estado']
                                # if col_suc_idx: new_row[col_suc_idx-1] = r['sucursal']
                                # if col_tel_idx: new_row[col_tel_idx-1] = r['tel']
                                # if col_rep_idx: new_row[col_rep_idx-1] = r['no_reporte']
                                # if col_fec_idx: new_row[col_fec_idx-1] = r['fecha_reporte']
                                # if col_falla_idx: new_row[col_falla_idx-1] = r['obs']
                                # ws_main.append_row(new_row)
                                # all_vals.append(new_row)
                            log_reporte_historial(st.session_state['current_user'], r['estado'], r['sucursal'], r['no_reporte'], r['fecha_reporte'], r['tel'], r['obs'])
                            guardados += 1
                        log_acceso(st.session_state['current_user'], f"Guardo lote PRUEBA {guardados} reportes - Reemplazo Hoja1 + Append Historial")
                        st.success(f"✅ {guardados} reportes guardados: Hoja1 REEMPLAZADA y HISTORIAL agregado - Cerrando sesion...")
                        st.session_state['batch_reportes'] = []
                        st.cache_data.clear()
                        st.balloons()
                        time.sleep(2)
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

# --- DETALLE CON FORMATO MEJORADO DE REPORTE Y FECHA + DIAS TRANSCURRIDOS ---
if not st.session_state.get('show_add_form', False):
    if 'estado_real' in st.session_state and 'sucursal_real' in st.session_state and COL_EST and COL_SUC:
        estado_sel = st.session_state['estado_real']
        suc_sel = st.session_state['sucursal_real']
        if estado_sel in df[COL_EST].values:
            df_filtro = df[(df[COL_EST] == estado_sel) & (df[COL_SUC] == suc_sel)]
            if not df_filtro.empty:
                for _, row in df_filtro.iterrows():
                    rep = str(row.get(COL_REP, "")).strip() if COL_REP else ""
                    fec = str(row.get(COL_FEC, "")).strip() if COL_FEC else ""
                    obs = str(row.get(COL_OBS, "")).strip() if COL_OBS else ""
                    tel_raw = row.get(COL_TEL, "") if COL_TEL else ""
                    tels = split_tels(tel_raw)
                    dias, txt_dias = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin reporte")
                    
                    # Badge con dias transcurridos - formato mejorado
                    if not tiene_reporte(rep):
                        badge_html = '<span class="badge badge-ok">Sin reporte</span>'
                    else:
                        if dias is None:
                            badge_html = f'<span class="badge badge-warn">{txt_dias}</span>'
                        elif dias <= 2:
                            badge_html = f'<span class="badge badge-warn">{dias} dias</span>'
                        elif dias <= 5:
                            badge_html = f'<span class="badge badge-orange">{dias} dias</span>'
                        else:
                            badge_html = f'<span class="badge badge-red">{txt_dias}</span>'
                    
                    # Formateo reporte y fecha con iconos y cajas
                    rep_display = f'<span class="rep-box">🗂️ REP: {rep}</span>' if tiene_reporte(rep) else '<span class="rep-box" style="background:#f0fdf4; color:#166534;">✅ Sin REP</span>'
                    fecha_display = f'<span class="rep-box">📅 Fecha: {fec}</span>' if fec and fec.lower() not in ['nan','none',''] else '<span class="rep-box">📅 Fecha: N/A</span>'
                    estado_display = f'<span class="rep-box" style="background:#0f172a; color:white; border-color:#0f172a;">📍 {estado_sel}</span>'

                    # Tarjeta principal con formato de captura
                    st.markdown(f"""
                    <div class="glass" style="padding:20px;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:16px;">
                            <div style="display:flex; gap:14px; align-items:flex-start;">
                                <div style="width:42px; height:42px; background:#0f172a; color:white; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px;">🏢</div>
                                <div>
                                    <div style="font-size:1.2rem; font-weight:900; color:#0f172a; letter-spacing:-0.5px;">{suc_sel}</div>
                                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:8px;">
                                        {estado_display}
                                        {rep_display}
                                        {fecha_display}
                                    </div>
                                </div>
                            </div>
                            <div style="text-align:right;">
                                {badge_html}
                            </div>
                        </div>
                        <div style="margin-top:14px; padding:12px 14px; background:#f8fafc; border:1px solid #f1f5f9; border-radius:10px;">
                            <div style="font-size:0.70rem; font-weight:800; color:#64748b; letter-spacing:0.6px; margin-bottom:4px;">📝 FALLA REPORTADA</div>
                            <div style="color:#1e293b; font-size:0.92rem;">{obs if obs and obs.lower()!='nan' else 'Sin observaciones'}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Lineas telefonicas con icono
                    st.markdown(f"<div style='margin-top:14px; margin-bottom:8px; font-weight:800; font-size:0.85rem;'>☎️ LINEAS TELEFONICAS • {len(tels)} numeros</div>", unsafe_allow_html=True)
                    if tels:
                        cols = st.columns(2)
                        for i, t in enumerate(tels):
                            with cols[i % 2]:
                                st.markdown(f"""
                                <div style="background:white; border:1px solid #e2e8f0; border-radius:12px; padding:10px 14px; display:flex; align-items:center; gap:10px; margin-bottom:10px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                                    <div style="width:34px; height:34px; background:#eff6ff; border-radius:9px; display:flex; align-items:center; justify-content:center;">📞</div>
                                    <div>
                                        <div style="font-size:0.65rem; color:#64748b; font-weight:700;">LINEA TELEFONICA</div>
                                        <div style="font-weight:800; font-size:0.95rem; letter-spacing:0.3px;">{t}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info(f"Sin lineas registradas - {tel_raw}")
            else:
                st.info("Selecciona sucursal para ver detalle")
