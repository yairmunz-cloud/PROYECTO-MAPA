import streamlit as st
import pandas as pd
from datetime import datetime
import re
import time
import base64

try:
    with open("image_af8068.png", "rb") as f:
        b64_logo = base64.b64encode(f.read()).decode()
except:
    try:
        with open("/mnt/data/image_af8068.png", "rb") as f:
            b64_logo = base64.b64encode(f.read()).decode()
    except:
        b64_logo = "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"

st.set_page_config(page_title="SUCURSALES", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    html, body { font-family: Inter, sans-serif; }
    .stApp { background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .glass { background: rgba(255,255,255,0.9) !important; border-radius: 18px; padding: 20px 22px; box-shadow: 0 8px 32px rgba(15,23,42,0.08); border: 1px solid white; }
    .glass-dark { background: rgba(15,23,42,0.88) !important; color: white; border-radius: 18px; padding: 16px 18px; }
    .badge { display:inline-flex; padding:6px 12px; border-radius:100px; font-size:0.82rem; font-weight:700; }
    .badge-ok { background:#dcfce7; color:#166534; border:1px solid #bbf7d0; }
    .badge-warn { background:#fef9c3; color:#854d0e; border:1px solid #fde68a; }
    .badge-orange { background:#ffedd5; color:#9a3412; border:1px solid #fed7aa; }
    .badge-red { background:#fee2e2; color:#991b1b; border:1px solid #fecaca; }
    .filter-pill { background: white; border: 1px solid #e2e8f0; border-radius: 50px !important; padding: 10px 18px 12px 18px !important; }
    .filter-label { font-size:0.72rem !important; font-weight:800 !important; color:#64748b !important; letter-spacing:0.8px; text-transform:uppercase; margin-bottom:2px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60, show_spinner=False)
def cargar_datos():
    base_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90/pub?output=csv"
    url = f"{base_url}&cb={int(time.time())}"
    df = pd.read_csv(url, dtype=str)
    df.columns = df.columns.str.strip().str.upper()
    return df.dropna(how='all')

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

df[COL_EST] = df[COL_EST].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
df[COL_SUC] = df[COL_SUC].astype(str).str.strip()

def tiene_reporte(v):
    if pd.isna(v): return False
    return str(v).strip().lower() not in ["","0","0.0","sin reporte","none","nan","vacio","s/r"]

def dias_desde(fecha_str):
    if not fecha_str or str(fecha_str).lower() in ['nan','none','']: return None, "Fecha pendiente"
    dt = pd.to_datetime(fecha_str, errors='coerce', dayfirst=True)
    if pd.isna(dt): return None, "Formato invalido"
    return (datetime.now() - dt).days, f"{(datetime.now() - dt).days} dias"

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
            sheet_id = st.secrets.get("sheet_id", "[STRIPPED 79 bytes]")
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("LOG_ACCESOS")
            except:
                ws = sh.add_worksheet(title="LOG_ACCESOS", rows=1000, cols=10)
                ws.append_row(["FECHA", "HORA", "USUARIO", "ACCION", "DETALLE"])
            ws.append_row([fecha, hora, usuario, accion, "Acceso desde app"])
    except:
        if 'log_accesos_demo' not in st.session_state:
            st.session_state['log_accesos_demo'] = []
        st.session_state['log_accesos_demo'].append({"fecha": fecha, "hora": hora, "usuario": usuario, "accion": accion})

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
            sheet_id = st.secrets.get("sheet_id", "[STRIPPED 79 bytes]")
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=5000, cols=15)
                ws.append_row(["FECHA_REGISTRO", "HORA_REGISTRO", "DIA", "MES", "ANIO", "USUARIO", "ESTADO", "SUCURSAL", "NO_REPORTE", "FECHA_REPORTE", "TEL", "OBSERVACIONES"])
            ws.append_row([fecha_reg, hora_reg, dia, mes, anio, usuario, estado, sucursal, no_reporte, fecha_reporte, tel, observaciones])
    except:
        if 'historial_demo' not in st.session_state:
            st.session_state['historial_demo'] = []
        st.session_state['historial_demo'].append({"fecha_reg": fecha_reg, "hora": hora_reg, "dia": dia, "mes": mes, "anio": anio, "usuario": usuario, "estado": estado, "sucursal": sucursal, "no_reporte": no_reporte, "fecha_reporte": fecha_reporte, "tel": tel, "observaciones": observaciones})

lista_estados = sorted(df[COL_EST].dropna().unique())
df_reportes = df[df[COL_REP].apply(tiene_reporte)] if COL_REP else pd.DataFrame()

if 'admin_auth' not in st.session_state:
    st.session_state['admin_auth'] = False
if 'show_login' not in st.session_state:
    st.session_state['show_login'] = False
if 'show_add_form' not in st.session_state:
    st.session_state['show_add_form'] = False
if 'current_user' not in st.session_state:
    st.session_state['current_user'] = None
if 'batch_reportes' not in st.session_state:
    st.session_state['batch_reportes'] = []

# HEADER
c1, c2 = st.columns([2.2, 1.3])
with c1:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:16px">
        <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; background:white">
            <img src="data:image/png;base64,{b64_logo}" style="width:100%; height:100%; object-fit:cover">
        </div>
        <div style="font-size:2rem; font-weight:900; letter-spacing:-0.8px">SUCURSALES</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="glass-dark">
        <div style="display:flex; justify-content:space-between; align-items:center">
            <div style="display:flex; gap:10px; align-items:center"><div style="width:34px; height:34px; background:rgba(239,68,68,0.25); border-radius:9px; display:flex; align-items:center; justify-content:center">🚨</div>
            <div><div style="font-weight:700">Reportes Activos</div><div style="font-size:0.75rem; opacity:0.7">{len(df_reportes)} requieren atencion</div></div></div>
            <div style="font-size:1.6rem; font-weight:900">{len(df_reportes)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if not df_reportes.empty and not st.session_state.get('show_add_form'):
        opciones = {f"{r[COL_SUC]} ({r[COL_EST]})": (str(r[COL_EST]), str(r[COL_SUC])) for _, r in df_reportes.iterrows()}
        sel = st.selectbox("jump", ["Seleccionar reporte..."] + list(opciones.keys()), label_visibility="collapsed", key="jump_rep_final")
        if sel != "Seleccionar reporte...":
            if st.session_state.get('last_jump') != sel:
                est_jump, suc_jump = opciones[sel]
                st.session_state['estado_real'] = est_jump
                st.session_state['sucursal_real'] = suc_jump
                st.session_state['jump_est'] = est_jump
                st.session_state['jump_suc'] = suc_jump
                st.session_state['last_jump'] = sel
                st.rerun()

default_est_idx = 0
default_suc = None
if 'estado_real' in st.session_state and st.session_state['estado_real'] in lista_estados:
    default_est_idx = lista_estados.index(st.session_state['estado_real'])
    default_suc = st.session_state.get('sucursal_real')
elif 'jump_est' in st.session_state and st.session_state['jump_est'] in lista_estados:
    default_est_idx = lista_estados.index(st.session_state['jump_est'])
    default_suc = st.session_state.get('jump_suc')

es_modo_agregar = st.session_state.get('show_add_form', False) and st.session_state.get('admin_auth', False)

if not es_modo_agregar:
    f1, f2, f3 = st.columns([1.1, 1.8, 0.7], gap="medium")
    with f1:
        st.markdown('<div class="filter-pill"><div class="filter-label">📍 Estado</div>', unsafe_allow_html=True)
        estado_actual = st.selectbox("Estado", lista_estados, index=default_est_idx, key="estado_real", label_visibility="collapsed")
        if 'jump_est' in st.session_state and estado_actual != st.session_state['jump_est']:
            if 'jump_est' in st.session_state:
                del st.session_state['jump_est']
            if 'jump_suc' in st.session_state:
                del st.session_state['jump_suc']
            default_suc = None
        st.markdown('</div>', unsafe_allow_html=True)
    df_estado = df[df[COL_EST] == estado_actual]
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique())
    with f2:
        st.markdown(f'<div class="filter-pill"><div class="filter-label">🏬 Sucursales • {len(lista_suc)} en {estado_actual}</div>', unsafe_allow_html=True)
        if default_suc and default_suc in lista_suc:
            idx_suc = lista_suc.index(default_suc)
        else:
            idx_suc = 0
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
            if st.button("➕", use_container_width=True, help="Agregar reporte - solo admin"):
                st.session_state['show_login'] = True
                st.session_state['show_add_form'] = False
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    if 'estado_real' in st.session_state and st.session_state['estado_real'] in lista_estados:
        estado_actual = st.session_state['estado_real']
    elif 'jump_est' in st.session_state and st.session_state['jump_est'] in lista_estados:
        estado_actual = st.session_state['jump_est']
    else:
        estado_actual = lista_estados[default_est_idx] if lista_estados else ""
    df_estado = df[df[COL_EST] == estado_actual]
    lista_suc = sorted(df_estado[COL_SUC].dropna().unique())
    if 'sucursal_real' in st.session_state and st.session_state['sucursal_real'] in lista_suc:
        sucursal_actual = st.session_state['sucursal_real']
    elif 'jump_suc' in st.session_state and st.session_state['jump_suc'] in lista_suc:
        sucursal_actual = st.session_state['jump_suc']
    else:
        sucursal_actual = lista_suc[0] if lista_suc else ""

# LOGIN
if st.session_state['show_login'] and not st.session_state['admin_auth']:
    st.markdown('<div class="glass" style="border:2px solid #0f172a; padding:24px">', unsafe_allow_html=True)
    st.markdown("### 🔐 Login Administrador")
    st.caption("Acceso restringido - Solo personal autorizado")
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

# FORMULARIO MODO LIMPIO
if st.session_state['admin_auth'] and st.session_state['show_add_form']:
    st.markdown('<div class="glass" style="border:2px solid #16a34a; padding:28px">', unsafe_allow_html=True)
    st.markdown(f"### ➕ Agregar Reporte - Usuario: **{st.session_state['current_user']}**")
    st.info(f"Modo lote: agrega N reportes y al final guarda todo en Google Sheets")
    
    st.markdown("#### 1️⃣ Selecciona Estado y Sucursal (se filtra automaticamente)")
    fc_sel1, fc_sel2 = st.columns(2)
    with fc_sel1:
        est_new = st.selectbox("Estado del reporte", lista_estados, index=lista_estados.index(estado_actual) if estado_actual in lista_estados else 0, key="form_est_outside")
    est_new_clean = str(est_new).strip().upper()
    df_suc_filtro = df[df[COL_EST].str.strip().str.upper() == est_new_clean]
    lista_suc_filtro = sorted(df_suc_filtro[COL_SUC].dropna().unique())
    with fc_sel2:
        opciones_suc = lista_suc_filtro + ["➕ Otra / Nueva sucursal..."]
        if sucursal_actual in lista_suc_filtro:
            idx_def = lista_suc_filtro.index(sucursal_actual)
        else:
            idx_def = 0
        suc_sel = st.selectbox(f"Sucursal - {len(lista_suc_filtro)} en {est_new_clean}", opciones_suc, index=idx_def, key=f"form_suc_outside_{est_new_clean}")
    
    if suc_sel == "➕ Otra / Nueva sucursal...":
        suc_new = st.text_input("Escribe nueva sucursal *", placeholder="Ej: CORDOBA", key="form_suc_new_text")
        lineas_sucursal = []
        if suc_new:
            st.warning(f"Se creara nueva: {suc_new} en {est_new}")
    else:
        suc_new = suc_sel
        fila_suc = df_suc_filtro[df_suc_filtro[COL_SUC] == suc_new]
        if not fila_suc.empty:
            lineas_sucursal = split_tels(fila_suc.iloc[0].get(COL_TEL, ""))
        else:
            lineas_sucursal = []
        st.success(f"Sucursal: {suc_new} - {len(lineas_sucursal)} lineas")
    
    st.markdown("---")
    st.markdown("#### 2️⃣ Lineas con falla y datos")
    st.markdown("**📞 Lineas telefonicas de la sucursal - Selecciona cual tiene falla**")
    if lineas_sucursal:
        st.caption(f"{len(lineas_sucursal)} lineas en {suc_new}")
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
    st.markdown("#### 3️⃣ Datos del reporte")
    st.markdown(f"**Resumen:** Estado: {est_new} | Sucursal: {suc_new} | Lineas: {tel_final if tel_final else 'Ninguna seleccionada'}")
    
    with st.form("form_reporte_final", clear_on_submit=True):
        fc1, fc2 = st.columns(2)
        with fc1:
            rep_new = st.text_input("No. Reporte *", placeholder="45163", key="form_rep_final")
        with fc2:
            fec_new = st.date_input("Fecha Reporte", value=datetime.now().date(), key="form_fec_final")
        obs_new = st.text_area("📝 Observaciones / Falla reportada *", placeholder="Ej: falla, sin linea, ruido...", height=90, key="form_obs_final")
        st.markdown("---")
        c1f, c2f = st.columns([1.3, 0.7])
        with c1f:
            btn_add = st.form_submit_button("➕ AGREGAR REPORTE A LA LISTA", type="primary", use_container_width=True)
        with c2f:
            btn_close = st.form_submit_button("Cerrar formulario", use_container_width=True)
        if btn_close:
            st.session_state['show_add_form'] = False
            st.rerun()
        if btn_add:
            if not rep_new:
                st.error("No. Reporte obligatorio")
            elif not suc_new:
                st.error("Sucursal obligatoria")
            elif not tel_final:
                st.error("Selecciona al menos una linea con falla")
            elif not obs_new:
                st.error("Observaciones obligatoria")
            else:
                nuevo = {"estado": est_new, "sucursal": suc_new, "tel": tel_final, "no_reporte": rep_new, "fecha_reporte": fec_new.strftime("%d/%m/%Y"), "obs": obs_new}
                st.session_state['batch_reportes'].append(nuevo)
                st.success(f"✅ Reporte {rep_new} agregado - Total: {len(st.session_state['batch_reportes'])}")
                st.session_state['clear_after_add'] = True
                st.rerun()
    
    if st.session_state.get('clear_after_add'):
        # Limpiar checkboxes de lineas
        for k in list(st.session_state.keys()):
            if k.startswith("chk_linea_"):
                del st.session_state[k]
        # Limpiar campos del form
        for k in ["form_rep_final", "form_obs_final", "tel_extra_outside", "tel_new_suc_outside", "tel_final", "seleccionadas"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state['clear_after_add'] = False
        st.rerun()

    # LISTA DE REPORTES EN COLA - DEBAJO DEL BOTON AGREGAR (como en tu 2da imagen)
    if st.session_state['batch_reportes']:
        st.markdown("---")
        st.markdown(f"#### 📋 Reportes en cola ({len(st.session_state['batch_reportes'])}) - Aun no guardados")
        for idx, r in enumerate(st.session_state['batch_reportes']):
            col_r1, col_r2 = st.columns([5,1])
            with col_r1:
                st.markdown(f"<div style='background:#f0fdf4; border:1px solid #bbf7d0; border-left:4px solid #16a34a; padding:10px 14px; border-radius:10px; margin-bottom:8px'>"
                            f"<b>{idx+1}. {r['sucursal']} ({r['estado']})</b> - REP: {r['no_reporte']} - Lineas: {r['tel']}<br><small>{r['obs'][:100]}</small>"
                            f"</div>", unsafe_allow_html=True)
            with col_r2:
                if st.button("❌", key=f"del_batch_{idx}_{r['no_reporte']}"):
                    st.session_state['batch_reportes'].pop(idx)
                    st.rerun()
        st.markdown("---")
        c_save1, c_save2 = st.columns([1.5, 0.5])
        with c_save1:
            if st.button(f"💾 GUARDAR LOS {len(st.session_state['batch_reportes'])} REPORTES EN GOOGLE SHEETS", type="primary", use_container_width=True):
                try:
                    guardados = 0
                    if "gcp_service_account" in st.secrets:
                        import gspread
                        from google.oauth2.service_account import Credentials
                        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
                        client = gspread.authorize(creds)
                        sheet_id = st.secrets.get("sheet_id", "1B0pB5yR2VqY7Jz8KxL9MnOpQrStUvWxYz1234567890")
                        sh = client.open_by_key(sheet_id)
                        try:
                            ws_main = sh.worksheet("BDSUCURSALES")
                        except:
                            ws_main = sh.sheet1
                        for r in st.session_state['batch_reportes']:
                            ws_main.append_row([r['estado'], r['sucursal'], r['tel'], r['no_reporte'], r['fecha_reporte'], r['obs']])
                            log_reporte_historial(st.session_state['current_user'], r['estado'], r['sucursal'], r['no_reporte'], r['fecha_reporte'], r['tel'], r['obs'])
                            guardados += 1
                        log_acceso(st.session_state['current_user'], f"Guardo lote de {guardados} reportes")
                        st.success(f"✅ {guardados} reportes guardados - Cerrando sesion...")
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
                        st.warning(f"DEMO: {guardados} reportes solo en memoria")
                        st.session_state['batch_reportes'] = []
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        with c_save2:
            if st.button("🗑️ Limpiar lista", use_container_width=True):
                st.session_state['batch_reportes'] = []
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state['admin_auth']:
    with st.sidebar:
        st.success(f"👤 {st.session_state['current_user']} conectado")
        if st.button("🔓 Cerrar sesion"):
            log_acceso(st.session_state['current_user'], "Logout")
            st.session_state['admin_auth'] = False
            st.session_state['show_add_form'] = False
            st.session_state['show_login'] = False
            st.session_state['current_user'] = None
            st.session_state['batch_reportes'] = []
            st.rerun()
        st.markdown("---")
        st.markdown("### 🔍 Consultas Historial")
        df_hist = pd.DataFrame(st.session_state.get('historial_demo', []))
        if not df_hist.empty:
            f_anio = st.selectbox("Año", ["Todos"] + sorted(df_hist['anio'].unique().tolist()), key="f_anio2")
            f_mes = st.selectbox("Mes", ["Todos"] + sorted(df_hist['mes'].unique().tolist()), key="f_mes2")
            f_user = st.selectbox("Usuario", ["Todos"] + sorted(df_hist['usuario'].unique().tolist()), key="f_user2")
            f_suc = st.text_input("Sucursal", placeholder="CORDOBA", key="f_suc2")
            f_rep = st.text_input("No. Reporte", placeholder="51564186", key="f_rep2")
            df_f = df_hist.copy()
            if f_anio != "Todos":
                df_f = df_f[df_f['anio'] == f_anio]
            if f_mes != "Todos":
                df_f = df_f[df_f['mes'] == f_mes]
            if f_user != "Todos":
                df_f = df_f[df_f['usuario'] == f_user]
            if f_suc:
                df_f = df_f[df_f['sucursal'].str.contains(f_suc, case=False, na=False)]
            if f_rep:
                df_f = df_f[df_f['no_reporte'].str.contains(f_rep, case=False, na=False)]
            st.write(f"{len(df_f)} reportes")
            if not df_f.empty:
                st.bar_chart(df_f.groupby('sucursal').size())
                st.dataframe(df_f, use_container_width=True)

# DETALLE PRINCIPAL - OCULTO EN MODO AGREGAR
if not st.session_state.get('show_add_form', False):
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    if lista_suc and sucursal_actual:
        fila_df = df_estado[df_estado[COL_SUC] == sucursal_actual]
        if fila_df.empty:
            fila_df = df[df[COL_SUC] == sucursal_actual]
        fila = fila_df.iloc[0]
        rep = fila.get(COL_REP, "")
        fec = fila.get(COL_FEC, "")
        tels = split_tels(fila.get(COL_TEL, ""))
        dias, txt = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin reporte")
        if dias is None:
            b_class = "badge-ok"; b_txt = "🟢 Sin reporte"; c_dias = "#166534"
        elif dias <= 3:
            b_class = "badge-warn"; b_txt = f"🟡 {dias} dias"; c_dias = "#854d0e"
        elif dias <= 7:
            b_class = "badge-orange"; b_txt = f"🟠 {dias} dias"; c_dias = "#9a3412"
        else:
            b_class = "badge-red"; b_txt = f"🔴 {dias} dias"; c_dias = "#991b1b"
        c_det1, c_det2 = st.columns([2.2, 1])
        with c_det1:
            rep_html = f'<span style="background:#fee2e2; color:#991b1b; padding:5px 12px; border-radius:20px; font-weight:800; font-size:0.95rem; border:1px solid #fecaca">REP: {rep}</span>' if tiene_reporte(rep) else '<span style="color:#16a34a; font-weight:700">🟢 Sin reporte</span>'
            st.markdown('<div class="glass" style="padding:26px">'
                f'<div style="display:flex; justify-content:space-between; align-items:center"><div class="badge {b_class}">{b_txt}</div><div style="font-size:0.85rem; color:#64748b; font-weight:600; display:flex; gap:8px; align-items:center"><span>{fila[COL_EST]}</span>•{rep_html}</div></div>'
                f'<div style="font-size:1.9rem; font-weight:800; margin-top:14px">🏢 {fila[COL_SUC]}</div>'
                f'<div style="display:flex; gap:28px; margin-top:18px"><div><div style="font-size:0.72rem; color:#64748b; font-weight:700; text-transform:uppercase">Fecha reporte</div><div style="font-weight:700">{fec if str(fec)!="nan" else "N/A"}</div></div>'
                f'<div><div style="font-size:0.72rem; color:#64748b; font-weight:700; text-transform:uppercase">Dias</div><div style="font-size:1.35rem; font-weight:900; color:{c_dias}">{txt}</div></div>'
                f'<div><div style="font-size:0.72rem; color:#64748b; font-weight:700; text-transform:uppercase">Lineas</div><div style="font-weight:700">{len(tels)} numeros</div></div></div></div>', unsafe_allow_html=True)
            if COL_OBS and COL_OBS in fila and str(fila.get(COL_OBS, "")).strip().lower() not in ["", "nan", "none"]:
                obs_mostrar = fila.get(COL_OBS, "")
                st.markdown(f'<div class="glass" style="padding:16px; margin-top:12px; border-left:4px solid #f59e0b"><div style="font-size:0.75rem; font-weight:700; color:#92400e; text-transform:uppercase; margin-bottom:6px">📝 Observaciones / Falla</div><div style="font-size:0.95rem; color:#0f172a">{obs_mostrar}</div></div>', unsafe_allow_html=True)
            st.markdown("### 📞 Lineas Telefonicas")
            if not tels:
                st.markdown('<div class="glass" style="text-align:center; padding:20px; color:#64748b">Sin lineas</div>', unsafe_allow_html=True)
            else:
                cols_t = st.columns(2)
                for i, t in enumerate(tels):
                    with cols_t[i % 2]:
                        st.markdown(f'<div class="glass" style="padding:12px 16px; margin-bottom:10px">📞 {t}</div>', unsafe_allow_html=True)
        with c_det2:
            st.markdown(f'<div class="glass" style="text-align:center; padding:24px"><div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase">Dias con reporte</div><div style="font-size:3rem; font-weight:900; color:{c_dias}">{dias if dias is not None else "—"}</div><div style="color:#64748b">{txt}</div></div>', unsafe_allow_html=True)
