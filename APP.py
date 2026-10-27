import streamlit as st
import pandas as pd
from datetime import datetime
import re
import time
import base64

# Cargar logo Atlas - intentar desde archivo local o usar base64 embebido
try:
    with open("image_af8068.png", "rb") as f:
        b64_logo = base64.b64encode(f.read()).decode()
except:
    try:
        with open("/mnt/data/image_af8068.png", "rb") as f:
            b64_logo = base64.b64encode(f.read()).decode()
    except:
        b64_logo = ""

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
    return [t.strip() for t in re.split(r'[\n,;/]+', str(raw)) if t.strip() and t.strip().lower()!='nan']

# USUARIOS AUTORIZADOS - DOS USUARIOS
USUARIOS = {
    "yair": "AtlasY",
    "francisco": "AtlasF"
}

def check_login(user, pwd):
    try:
        # Si hay secrets, usarlos, si no usar diccionario local
        if "users" in st.secrets:
            users_secret = st.secrets["users"]
            return user in users_secret and users_secret[user] == pwd
        else:
            return USUARIOS.get(user) == pwd
    except:
        return USUARIOS.get(user) == pwd

def log_acceso(usuario, accion="Login"):
    """Registra acceso en hoja LOG_ACCESOS"""
    now = datetime.now()
    fecha = now.strftime("%d/%m/%Y")
    hora = now.strftime("%H:%M:%S")
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            sheet_id = st.secrets.get("sheet_id", "1QbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90")
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("LOG_ACCESOS")
            except:
                ws = sh.add_worksheet(title="LOG_ACCESOS", rows=1000, cols=10)
                ws.append_row(["FECHA", "HORA", "USUARIO", "ACCION", "DETALLE"])
            ws.append_row([fecha, hora, usuario, accion, f"Acceso desde app"])
    except Exception as e:
        # Guardar local si no hay credenciales
        if 'log_accesos_demo' not in st.session_state:
            st.session_state['log_accesos_demo'] = []
        st.session_state['log_accesos_demo'].append({"fecha": fecha, "hora": hora, "usuario": usuario, "accion": accion})

def log_reporte_historial(usuario, estado, sucursal, no_reporte, fecha_reporte, tel=""):
    """Registra reporte en HISTORIAL_REPORTES para graficas y consultas por dia/mes/año"""
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
            sheet_id = st.secrets.get("sheet_id", "1QbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90")
            sh = client.open_by_key(sheet_id)
            try:
                ws = sh.worksheet("HISTORIAL_REPORTES")
            except:
                ws = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=5000, cols=15)
                ws.append_row(["FECHA_REGISTRO", "HORA_REGISTRO", "DIA", "MES", "ANIO", "USUARIO", "ESTADO", "SUCURSAL", "NO_REPORTE", "FECHA_REPORTE", "TEL"])
            ws.append_row([fecha_reg, hora_reg, dia, mes, anio, usuario, estado, sucursal, no_reporte, fecha_reporte, tel])
    except Exception as e:
        if 'historial_demo' not in st.session_state:
            st.session_state['historial_demo'] = []
        st.session_state['historial_demo'].append({"fecha_reg": fecha_reg, "hora": hora_reg, "dia": dia, "mes": mes, "anio": anio, "usuario": usuario, "estado": estado, "sucursal": sucursal, "no_reporte": no_reporte, "fecha_reporte": fecha_reporte})

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
    if not df_reportes.empty:
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

# FILTROS
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

# LOGIN MODAL - DOS USUARIOS
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
                st.success(f"Bienvenido {u}")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
    with cl2:
        if st.button("Cancelar", use_container_width=True):
            st.session_state['show_login'] = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# FORMULARIO AGREGAR REPORTE
if st.session_state['admin_auth'] and st.session_state['show_add_form']:
    st.markdown('<div class="glass" style="border:2px solid #16a34a; padding:28px">', unsafe_allow_html=True)
    st.markdown(f"### ➕ Agregar Reporte - Usuario: **{st.session_state['current_user']}**")
    st.info(f"{len(df)} sucursales • Se guardara en BDSUCURSALES + HISTORIAL + LOG")
    
    with st.form("form_add_reporte"):
        fc1, fc2 = st.columns(2)
        with fc1:
            est_new = st.selectbox("Estado", lista_estados, index=lista_estados.index(estado_actual) if estado_actual in lista_estados else 0)
            suc_new = st.text_input("Sucursal", value=sucursal_actual)
            rep_new = st.text_input("No. Reporte *", placeholder="Ej: 51564186")
        with fc2:
            tel_new = st.text_input("Lineas Telefonicas", placeholder="Ej: 551-102-2050")
            fec_new = st.date_input("Fecha Reporte", value=datetime.now().date())
        
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            submitted = st.form_submit_button("💾 Guardar en Google Sheets", type="primary", use_container_width=True)
        with c_f2:
            cerrar = st.form_submit_button("Cerrar formulario", use_container_width=True)
        
        if cerrar:
            st.session_state['show_add_form'] = False
            st.rerun()
        
        if submitted:
            if not rep_new:
                st.error("No. Reporte obligatorio")
            else:
                try:
                    if "gcp_service_account" in st.secrets:
                        import gspread
                        from google.oauth2.service_account import Credentials
                        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
                        client = gspread.authorize(creds)
                        sheet_id = st.secrets.get("sheet_id", "1QbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90")
                        sh = client.open_by_key(sheet_id)
                        # Hoja principal
                        try:
                            ws_main = sh.worksheet("BDSUCURSALES")
                        except:
                            ws_main = sh.sheet1
                        ws_main.append_row([est_new, suc_new, tel_new, rep_new, fec_new.strftime("%d/%m/%Y")])
                        
                        # LOG_ACCESOS y HISTORIAL ya se manejan en funciones
                        log_acceso(st.session_state['current_user'], f"Agrego reporte {rep_new} en {suc_new}")
                        log_reporte_historial(st.session_state['current_user'], est_new, suc_new, rep_new, fec_new.strftime("%d/%m/%Y"), tel_new)
                        
                        st.success(f"Reporte {rep_new} agregado a {suc_new}")
                        st.cache_data.clear()
                        st.balloons()
                    else:
                        st.warning("⚠️ MODO DEMO - El reporte NO se guardo en Google Sheets real")
                        st.error("Faltan credenciales de Google. Para que guarde real, debes configurar Service Account en Secrets.")
                        log_acceso(st.session_state['current_user'], f"Demo: intento agregar {rep_new} en {suc_new} - SIN GUARDAR EN SHEET")
                        log_reporte_historial(st.session_state['current_user'], est_new, suc_new, rep_new, fec_new.strftime("%d/%m/%Y"), tel_new)
                        st.info(f"Reporte {rep_new} guardado SOLO en memoria local (se borra al recargar). Para guardado permanente, configura Secrets.")
                        st.success(f"Demo local: {rep_new} - {suc_new}")
                except Exception as e:
                    st.error(f"Error: {e}")
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
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🔍 Consultas Historial")
        st.caption("Filtra reportes por dia, mes, año, usuario y No. Reporte")
        
        # Cargar historial (real si hay credenciales, si no demo)
        df_hist_real = pd.DataFrame()
        if 'historial_demo' in st.session_state and st.session_state['historial_demo']:
            df_hist_real = pd.DataFrame(st.session_state['historial_demo'])
        else:
            # Intentar cargar desde Google Sheets si hay credenciales
            try:
                if "gcp_service_account" in st.secrets:
                    import gspread
                    from google.oauth2.service_account import Credentials
                    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
                    client = gspread.authorize(creds)
                    sheet_id = st.secrets.get("sheet_id", "1QbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90")
                    sh = client.open_by_key(sheet_id)
                    ws = sh.worksheet("HISTORIAL_REPORTES")
                    data = ws.get_all_records()
                    if data:
                        df_hist_real = pd.DataFrame(data)
            except:
                pass
        
        if not df_hist_real.empty:
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filtro_anio = st.selectbox("Año", ["Todos"] + sorted(df_hist_real['ANIO'].astype(str).unique().tolist() if 'ANIO' in df_hist_real.columns else df_hist_real['anio'].astype(str).unique().tolist() if 'anio' in df_hist_real.columns else []), key="f_anio")
            with col_f2:
                filtro_mes = st.selectbox("Mes", ["Todos"] + sorted(df_hist_real['MES'].astype(str).unique().tolist() if 'MES' in df_hist_real.columns else df_hist_real['mes'].astype(str).unique().tolist() if 'mes' in df_hist_real.columns else []), key="f_mes")
            
            filtro_usuario = st.selectbox("Usuario", ["Todos"] + sorted(df_hist_real['USUARIO'].astype(str).unique().tolist() if 'USUARIO' in df_hist_real.columns else df_hist_real['usuario'].astype(str).unique().tolist() if 'usuario' in df_hist_real.columns else []), key="f_user")
            
            filtro_suc = st.text_input("Filtrar por sucursal", placeholder="Ej: CORDOBA", key="f_suc")
            filtro_rep = st.text_input("🔍 Buscar No. Reporte", placeholder="Ej: 51564186", key="f_rep")
            
            # Aplicar filtros
            df_filtrado = df_hist_real.copy()
            # Normalizar nombres de columnas (mayusculas o minusculas)
            df_filtrado.columns = [c.upper() for c in df_filtrado.columns]
            
            if filtro_anio != "Todos" and 'ANIO' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['ANIO'].astype(str) == filtro_anio]
            if filtro_mes != "Todos" and 'MES' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['MES'].astype(str) == filtro_mes]
            if filtro_usuario != "Todos" and 'USUARIO' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['USUARIO'].astype(str) == filtro_usuario]
            if filtro_suc and 'SUCURSAL' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['SUCURSAL'].astype(str).str.contains(filtro_suc, case=False, na=False)]
            if filtro_rep and 'NO_REPORTE' in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado['NO_REPORTE'].astype(str).str.contains(filtro_rep, case=False, na=False)]
            
            st.markdown(f"**{len(df_filtrado)} reportes encontrados**")
            
            # Metricas
            m1, m2 = st.columns(2)
            with m1:
                st.metric("Total", len(df_filtrado))
            with m2:
                if 'SUCURSAL' in df_filtrado.columns:
                    st.metric("Sucursales", df_filtrado['SUCURSAL'].nunique())
            
            # Graficas
            if not df_filtrado.empty:
                if 'FECHA_REGISTRO' in df_filtrado.columns:
                    st.markdown("**Por dia**")
                    por_dia = df_filtrado.groupby('FECHA_REGISTRO').size()
                    st.bar_chart(por_dia)
                elif 'FECHA_REG' in df_filtrado.columns:
                    st.markdown("**Por dia**")
                    por_dia = df_filtrado.groupby('FECHA_REG').size()
                    st.bar_chart(por_dia)
                
                if 'SUCURSAL' in df_filtrado.columns:
                    st.markdown("**Por sucursal (Top 10)**")
                    por_suc = df_filtrado.groupby('SUCURSAL').size().sort_values(ascending=False).head(10)
                    st.bar_chart(por_suc)
                
                if 'MES' in df_filtrado.columns:
                    st.markdown("**Por mes**")
                    por_mes = df_filtrado.groupby('MES').size()
                    st.bar_chart(por_mes)
                
                if 'USUARIO' in df_filtrado.columns:
                    st.markdown("**Por usuario**")
                    por_user = df_filtrado.groupby('USUARIO').size()
                    st.bar_chart(por_user)
                
                st.markdown("**Tabla filtrada**")
                st.dataframe(df_filtrado, use_container_width=True, height=300)
                
                # Boton exportar
                csv = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Descargar CSV filtrado", csv, f"reportes_filtrados_{filtro_anio}_{filtro_mes}.csv", "text/csv", use_container_width=True)
            else:
                st.warning("Sin resultados con esos filtros")
        else:
            st.info("Aun no hay historial. Agrega reportes con el boton ➕")
            # Mostrar demo vacio o con datos de ejemplo si no hay nada
            if 'log_accesos_demo' in st.session_state and st.session_state['log_accesos_demo']:
                st.markdown("---")
                st.markdown("### 📝 Log Accesos")
                df_log = pd.DataFrame(st.session_state['log_accesos_demo'])
                # Filtro log
                f_log_user = st.selectbox("Filtrar log por usuario", ["Todos"] + sorted(df_log['usuario'].unique().tolist() if 'usuario' in df_log.columns else []), key="f_log_user")
                if f_log_user != "Todos":
                    df_log = df_log[df_log['usuario'] == f_log_user]
                st.dataframe(df_log, use_container_width=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# DETALLE
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
        st.markdown(
            '<div class="glass" style="padding:26px">'
            f'<div style="display:flex; justify-content:space-between; align-items:center"><div class="badge {b_class}">{b_txt}</div><div style="font-size:0.85rem; color:#64748b; font-weight:600; display:flex; gap:8px; align-items:center"><span>{fila[COL_EST]}</span>•{rep_html}</div></div>'
            f'<div style="font-size:1.9rem; font-weight:800; margin-top:14px">🏢 {fila[COL_SUC]}</div>'
            f'<div style="display:flex; gap:28px; margin-top:18px"><div><div style="font-size:0.72rem; color:#64748b; font-weight:700; text-transform:uppercase">Fecha reporte</div><div style="font-weight:700">{fec if str(fec)!="nan" else "N/A"}</div></div>'
            f'<div><div style="font-size:0.72rem; color:#64748b; font-weight:700; text-transform:uppercase">Dias</div><div style="font-size:1.35rem; font-weight:900; color:{c_dias}">{txt}</div></div>'
            f'<div><div style="font-size:0.72rem; color:#64748b; font-weight:700; text-transform:uppercase">Lineas</div><div style="font-weight:700">{len(tels)} numeros</div></div></div></div>',
            unsafe_allow_html=True
        )
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
        # Grafica historica de esta sucursal si hay historial
        if 'historial_demo' in st.session_state and st.session_state['historial_demo']:
            df_h = pd.DataFrame(st.session_state['historial_demo'])
            df_suc_h = df_h[df_h['sucursal'] == sucursal_actual]
            if not df_suc_h.empty:
                st.markdown(f'<div class="glass" style="padding:16px; margin-top:12px"><div style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase; margin-bottom:8px">Historial de esta sucursal ({len(df_suc_h)} reportes)</div></div>', unsafe_allow_html=True)
                st.bar_chart(df_suc_h.groupby('fecha_reg').size())
