import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(page_title="SUCURSALES - PRUEBAS", layout="wide")

SHEET_ID = "12uBzVEE5ZqO7V6OIKSlCTB7BdSQWk_3sn12LhFdMWg4"
SHEET_ID_PUBLICO_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTySrWdMEtPBo7u4r6df8shaedXk8783RUOdOPsjLwIh1xz4nLHdAdaheYFMB1-CLI2XtzpzLa7SQXm/pub?output=csv"

# --- SECRETS ---
def get_secrets():
    try:
        return st.secrets
    except:
        return {}

# --- LOGIN SIMPLE ---
if 'logged' not in st.session_state:
    st.session_state['logged'] = False
    st.session_state['current_user'] = ""

if not st.session_state['logged']:
    st.title("SUCURSALES - PRUEBAS - Login")
    u = st.text_input("Usuario")
    p = st.text_input("Password", type="password")
    if st.button("Entrar"):
        secrets = get_secrets()
        users = secrets.get("users", {"yair": "AtlasY", "francisco": "AtlasF"})
        if u in users and users[u] == p:
            st.session_state['logged'] = True
            st.session_state['current_user'] = u
            st.rerun()
        else:
            st.error("Usuario o password incorrecto")
    st.stop()

# --- CONEXION GOOGLE SHEETS ---
def get_gspread_client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        secrets = get_secrets()
        if "gcp_service_account" not in secrets:
            return None, None
        creds = Credentials.from_service_account_info(secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        client = gspread.authorize(creds)
        sh = client.open_by_key(secrets.get("sheet_id", SHEET_ID))
        return client, sh
    except Exception as e:
        st.warning(f"No se pudo conectar a Google Sheets privado: {e}. Usando datos publicos para mostrar.")
        return None, None

def norm(s):
    return str(s).strip().upper().replace("  ", " ")

@st.cache_data(ttl=10, show_spinner=False)
def cargar_datos_mostrar():
    # 1. Intenta cargar BDSUCURSALES privada si tiene datos
    try:
        client, sh = get_gspread_client()
        if sh:
            try:
                ws = sh.worksheet("BDSUCURSALES")
            except:
                ws = sh.sheet1
            data = ws.get_all_records()
            if data and len(data) > 3:
                df = pd.DataFrame(data)
                df.columns = [str(c).strip().upper() for c in df.columns]
                df = df.dropna(how='all')
                if len(df) > 3:
                    return df
    except:
        pass
    # 2. Fallback CSV publico original (este SI tiene datos)
    try:
        url = f"{SHEET_ID_PUBLICO_CSV}&cb={int(time.time())}"
        df = pd.read_csv(url, dtype=str)
        df.columns = [str(c).strip().upper() for c in df.columns]
        return df.dropna(how='all')
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df = cargar_datos_mostrar()

if df.empty:
    st.error("No hay datos para mostrar. Verifica que BDSUCURSALES tenga datos o que el CSV publico este disponible.")
    st.stop()

# Detectar columnas
def buscar_col(kws):
    for c in df.columns:
        for kw in kws:
            if kw in c:
                return c
    return None

COL_EST = buscar_col(['ESTADO','EDO'])
COL_SUC = buscar_col(['SUCURSAL','SUC','SITIO'])
COL_TEL = buscar_col(['TELMEX','TEL','LINEA'])
COL_REP = buscar_col(['NO. REPORTE','NO REPORTE','REPORTE'])
COL_FEC = buscar_col(['FECHA','FEC'])
COL_FALLA = buscar_col(['FALLA','OBSERVACIONES','OBS','COMENTARIO'])

if not COL_EST or not COL_SUC:
    st.error(f"No se encontraron columnas ESTADO/SUCURSAL. Columnas encontradas: {list(df.columns)}")
    st.stop()

# --- UI FILTROS ---
st.title("SUCURSALES - PRUEBAS")
col1, col2, col3 = st.columns([2,3,1])
with col1:
    estados = sorted(df[COL_EST].dropna().unique().tolist())
    estado_actual = st.selectbox("ESTADO", estados, index=0 if "AGUASCALIENTES" not in estados else estados.index("AGUASCALIENTES"))
with col2:
    df_estado = df[df[COL_EST] == estado_actual]
    sucursales = sorted(df_estado[COL_SUC].dropna().unique().tolist())
    if not sucursales:
        sucursales = ["-"]
    sucursal_actual = st.selectbox(f"SUCURSALES - {len(sucursales)} EN {estado_actual}", sucursales)
with col3:
    if st.button("Cerrar sesion"):
        st.session_state['logged'] = False
        st.rerun()

# Mostrar detalle
df_filtro = df_estado[df_estado[COL_SUC] == sucursal_actual]

if not df_filtro.empty:
    st.subheader(f"{sucursal_actual} - {estado_actual}")
    # Mostrar lineas telefonicas
    for _, row in df_filtro.iterrows():
        tel = row.get(COL_TEL, "") if COL_TEL else ""
        rep = row.get(COL_REP, "") if COL_REP else ""
        fec = row.get(COL_FEC, "") if COL_FEC else ""
        falla = row.get(COL_FALLA, "") if COL_FALLA else ""
        with st.expander(f"Linea: {tel} - Reporte: {rep} - {fec}"):
            st.write(f"**Falla:** {falla}")
            st.write(f"**Reporte:** {rep} | **Fecha:** {fec} | **Tel:** {tel}")
else:
    st.info("No hay detalle para esta sucursal.")

st.divider()

# --- AGREGAR REPORTE ---
st.header("AGREGAR REPORTE")

if 'batch_reportes' not in st.session_state:
    st.session_state['batch_reportes'] = []

c1, c2, c3 = st.columns(3)
with c1:
    tel_input = st.text_input("TELMEX / LINEA", value=str(df_filtro.iloc[0][COL_TEL]) if not df_filtro.empty and COL_TEL else "")
    no_reporte = st.text_input("NO. REPORTE")
with c2:
    fecha_reporte = st.text_input("FECHA DE REPORTE", value=datetime.now().strftime("%d/%m/%Y"))
    obs = st.text_area("FALLA / OBSERVACIONES")
with c3:
    st.write(" ")
    st.write(" ")

# Boton AGREGAR A LA LISTA (cola)
if st.button("➕ AGREGAR REPORTE A LA LISTA", type="primary"):
    if not no_reporte:
        st.error("Pon NO. REPORTE")
    else:
        nuevo = {
            'estado': estado_actual,
            'sucursal': sucursal_actual,
            'tel': tel_input,
            'no_reporte': no_reporte,
            'fecha_reporte': fecha_reporte,
            'obs': obs,
            'usuario': st.session_state['current_user'],
            'timestamp': datetime.now().isoformat()
        }
        st.session_state['batch_reportes'].append(nuevo)
        st.success(f"Agregado a cola: {sucursal_actual} - {no_reporte}")
        st.rerun()

# Mostrar cola
if st.session_state['batch_reportes']:
    st.subheader(f"Cola de reportes ({len(st.session_state['batch_reportes'])})")
    df_batch = pd.DataFrame(st.session_state['batch_reportes'])
    st.dataframe(df_batch)
    
    col_guardar, col_limpiar = st.columns(2)
    with col_guardar:
        if st.button("💾 GUARDAR TODO EN LOTE", type="primary"):
            client, sh = get_gspread_client()
            if not sh:
                st.error("No hay conexion a Google Sheets privado. Verifica secrets gcp_service_account y sheet_id")
                st.stop()
            
            # --- LOGICA CORREGIDA COMO PEDISTE ---
            try:
                # Hoja 1 BDSUCURSALES
                try:
                    ws_main = sh.worksheet("BDSUCURSALES")
                except:
                    ws_main = sh.sheet1
                
                headers = ws_main.row_values(1)
                headers_upper = [h.strip().upper() for h in headers]
                
                def find_idx(keywords):
                    for i, h in enumerate(headers_upper):
                        for kw in keywords:
                            if kw in h:
                                return i+1
                    return None
                
                col_est_idx = find_idx(['ESTADO','EDO'])
                col_suc_idx = find_idx(['SUCURSAL','SUC','SITIO'])
                col_rep_idx = find_idx(['NO. REPORTE','NO REPORTE','REPORTE'])
                col_fec_idx = find_idx(['FECHA DE REPORTE','FECHA REPORTE','FECHA'])
                col_falla_idx = find_idx(['FALLA','OBSERVACIONES','OBS'])
                col_tel_idx = find_idx(['TELMEX','TEL','LINEA'])
                
                # Hoja HISTORIAL
                try:
                    ws_hist = sh.worksheet("HISTORIAL_REPORTES")
                except:
                    ws_hist = sh.add_worksheet(title="HISTORIAL_REPORTES", rows=1000, cols=10)
                    ws_hist.append_row(["FECHA_REGISTRO","USUARIO","ESTADO","SUCURSAL","TELMEX","NO_REPORTE","FECHA_REPORTE","FALLA","TIMESTAMP"])
                
                all_values = ws_main.get_all_values()
                guardados = 0
                for r in st.session_state['batch_reportes']:
                    # 1. Buscar fila en Hoja1 por ESTADO + SUCURSAL
                    row_found = None
                    for idx in range(1, len(all_values)):
                        row = all_values[idx]
                        try:
                            est_cell = row[col_est_idx-1] if col_est_idx and col_est_idx-1 < len(row) else ""
                            suc_cell = row[col_suc_idx-1] if col_suc_idx and col_suc_idx-1 < len(row) else ""
                            if norm(est_cell) == norm(r['estado']) and norm(suc_cell) == norm(r['sucursal']):
                                row_found = idx+1
                                break
                        except:
                            continue
                    
                    # 2. Hoja1: REEMPLAZAR solo 3 casillas
                    if row_found:
                        if col_rep_idx:
                            ws_main.update_cell(row_found, col_rep_idx, r['no_reporte'])
                        if col_fec_idx:
                            ws_main.update_cell(row_found, col_fec_idx, r['fecha_reporte'])
                        if col_falla_idx:
                            ws_main.update_cell(row_found, col_falla_idx, r['obs'])
                        if col_tel_idx and r['tel']:
                            ws_main.update_cell(row_found, col_tel_idx, r['tel'])
                    else:
                        # Si no existe, crear fila nueva
                        new_row = [""] * len(headers)
                        if col_est_idx: new_row[col_est_idx-1] = r['estado']
                        if col_suc_idx: new_row[col_suc_idx-1] = r['sucursal']
                        if col_tel_idx: new_row[col_tel_idx-1] = r['tel']
                        if col_rep_idx: new_row[col_rep_idx-1] = r['no_reporte']
                        if col_fec_idx: new_row[col_fec_idx-1] = r['fecha_reporte']
                        if col_falla_idx: new_row[col_falla_idx-1] = r['obs']
                        ws_main.append_row(new_row)
                    
                    # 3. HISTORIAL_REPORTES: APPEND siempre
                    ws_hist.append_row([
                        datetime.now().strftime("%d/%m/%Y %H:%M"),
                        r['usuario'],
                        r['estado'],
                        r['sucursal'],
                        r['tel'],
                        r['no_reporte'],
                        r['fecha_reporte'],
                        r['obs'],
                        r['timestamp']
                    ])
                    guardados += 1
                
                st.success(f"✅ Guardados {guardados} reportes: Hoja1 reemplazada y HISTORIAL agregado.")
                st.session_state['batch_reportes'] = []
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error guardando: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    with col_limpiar:
        if st.button("🗑️ Limpiar cola"):
            st.session_state['batch_reportes'] = []
            st.rerun()

st.divider()

# --- CONSULTA HISTORIAL PARA GRAFICAR ---
st.header("📊 Consultas de Reportes (desde HISTORIAL_REPORTES)")

try:
    client, sh = get_gspread_client()
    historial_df = None
    if sh:
        try:
            ws_hist = sh.worksheet("HISTORIAL_REPORTES")
            data = ws_hist.get_all_records()
            if data:
                historial_df = pd.DataFrame(data)
        except:
            pass
    
    if historial_df is not None and not historial_df.empty:
        st.dataframe(historial_df.tail(50))
        
        # Graficas simples
        if 'ESTADO' in historial_df.columns or 'SUCURSAL' in historial_df.columns:
            col_a, col_b = st.columns(2)
            with col_a:
                if 'ESTADO' in historial_df.columns:
                    st.bar_chart(historial_df['ESTADO'].value_counts())
            with col_b:
                if 'USUARIO' in historial_df.columns:
                    st.bar_chart(historial_df['USUARIO'].value_counts())
    else:
        st.info("Aun no hay datos en HISTORIAL_REPORTES. Agrega un reporte y guardalo para ver graficas.")
        
except Exception as e:
    st.error(f"Error consultando historial: {e}")

st.sidebar.write(f"Usuario: {st.session_state['current_user']}")
st.sidebar.write(f"Cola: {len(st.session_state.get('batch_reportes', []))}")
if st.sidebar.button("Refrescar datos"):
    st.cache_data.clear()
    st.rerun()
