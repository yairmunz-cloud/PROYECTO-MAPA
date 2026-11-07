import streamlit as st
from datetime import datetime, timedelta
import hashlib
import hmac
def _hash_pwd(p): return hashlib.sha256(p.encode()).hexdigest()
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

# FIX V42: check_login temprano - Buscar lo usa antes de su definicion original
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


import pandas as pd
from datetime import datetime
import re
import time
import base64


# --- FORZAR REFRESCO DE DATOS PARA MULTI-REPORTE ---
try:
    st.cache_data.clear()
except:
    pass


# --- FIX CACHE: Forzar refresco cada vez ---
try:
    st.cache_data.clear()
except:
    pass
try:
    st.cache_resource.clear()
except:
    pass

st.set_page_config(page_title="REPORTES Y CONSULTAS SUCURSALES SEGUROS ATLAS", layout="wide", page_icon="🏢", initial_sidebar_state="expanded")

# --- FIX 1: HOJA PRINCIPAL UNIFICADA ---
SHEET_PRINCIPAL = "BDSUCURSALES"
ID_CORRECTO_SHEETS = None  # FIX V46: No hardcodear ID - debe venir de st.secrets["sheet_id"]

# FIX FINAL v7: URL del usuario
# FIX SEGURIDAD V41: Se elimino USER_CSV_URL publico - exponia datos sin auth. No usar CSV publicado.


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
        ["🗺 Mapa Reportes", "📈 Analítica Dashboard", "🔒 Buscar Reportes"], 
        index=0 if "Mapa" in st.session_state['pagina'] or "Reportes" in st.session_state['pagina'] else 1 if "Dashboard" in st.session_state['pagina'] else 2 if "Buscar" in st.session_state['pagina'] else 0, 
        key="menu_pagina_v42",
        label_visibility="collapsed"
    )
    # FIX V45: Al salir de Buscar a Mapa/Dashboard, cerrar sesion privada automaticamente
    _pagina_prev = st.session_state.get('pagina')
    if "Mapa" in pagina:
        st.session_state['pagina'] = "🏠 Reportes"
    elif "Buscar" in pagina:
        st.session_state['pagina'] = "🔒 Buscar Reportes"
    else:
        st.session_state['pagina'] = "📊 Dashboard Analítica"
    if _pagina_prev == "🔒 Buscar Reportes" and st.session_state.get('pagina') != "🔒 Buscar Reportes":
        st.session_state['admin_auth'] = False
        st.session_state['current_user'] = None
        st.session_state['last_activity'] = None
        st.session_state['show_login'] = False

# --- DASHBOARD ANALÍTICA - PUBLICO ---
if st.session_state.get('pagina') == "📊 Dashboard Analítica":
    import altair as alt
    st.title("📊 Dashboard Analítica - Sucursales [PRUEBA V49 ESTÉTICA]")
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
                        try: sheet_id = SHEET_ID_PRUEBAS = st.secrets.get("sheet_id")  # FIX V46: sin fallback a test
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
        st.markdown(f"""<div style="background:white; padding:18px; border-radius:12px; border-left:5px solid #0f172a; box-shadow:0 2px 8px rgba(0,0,0,0.06); height:120px;"><div style="font-size:13px; color:#64748b; font-weight:600;">📋 Total eventos</div><div style="font-size:32px; font-weight:800; color:#0f172a; margin-top:4px;">{total_ev}</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div style="background:white; padding:18px; border-radius:12px; border-left:5px solid #ef4444; box-shadow:0 2px 8px rgba(0,0,0,0.06); height:120px;"><div style="font-size:13px; color:#64748b; font-weight:600;">🏆 Sucursal con más eventos</div><div style="font-size:18px; font-weight:800; color:#0f172a; margin-top:4px; white-space:normal; word-break:break-word; line-height:1.2;">{top_suc}</div><div style="font-size:12px; color:#16a34a; background:#dcfce7; display:inline-block; padding:2px 8px; border-radius:99px; margin-top:4px;">↗ {top_suc_num} eventos</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div style="background:white; padding:18px; border-radius:12px; border-left:5px solid #3b82f6; box-shadow:0 2px 8px rgba(0,0,0,0.06); height:120px;"><div style="font-size:13px; color:#64748b; font-weight:600;">🗺 Estado con más fallas</div><div style="font-size:22px; font-weight:800; color:#0f172a; margin-top:4px; white-space:normal; word-break:break-word;">{top_edo}</div><div style="font-size:12px; color:#64748b; margin-top:4px;">{top_edo_num} eventos</div></div>""", unsafe_allow_html=True)
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
            chart = alt.Chart(top10).mark_bar(color='#1e40af').encode(x='REPORTES:Q', y=alt.Y('SUCURSAL:N', sort='-x'), tooltip=['SUCURSAL','REPORTES']).properties(height=400)
            st.altair_chart(chart, width='stretch')
    with c2:
        st.subheader("📅 Reportes por Mes / Año")
        if 'MES' in df_f.columns and 'ANO' in df_f.columns:
            df_f['MES_ANO'] = df_f['ANO'].astype(str) + "-" + df_f['MES'].astype(str).str.zfill(2)
            por_mes = df_f.groupby('MES_ANO').size().reset_index(name='REPORTES').sort_values('MES_ANO')
            chart2 = alt.Chart(por_mes).mark_line(point=True, color='#0f172a').encode(x='MES_ANO:N', y='REPORTES:Q', tooltip=['MES_ANO','REPORTES']).properties(height=400)
            st.altair_chart(chart2, width='stretch')
    # --- RESTAURADO V47: Graficas que se perdieron en v39-v46 al recortar Dashboard ---
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("🗺 Fallas por Estado")
        st.caption("Paleta azul-gris • Anillo")
        if 'ESTADO' in df_f.columns:
            por_edo = df_f['ESTADO'].value_counts().reset_index()
            por_edo.columns = ['ESTADO','REPORTES']
            blues_grays = ['#0f172a','#1e3a8a','#1e40af','#1d4ed8','#2563eb','#3b82f6','#60a5fa','#93c5fd','#bfdbfe','#dbeafe','#e0e7ff','#cbd5e1','#94a3b8','#64748b','#475569','#334155']
            domain_estados = por_edo['ESTADO'].tolist()
            range_colors = (blues_grays * ((len(domain_estados)//len(blues_grays))+1))[:len(domain_estados)]
            total_edo = int(por_edo['REPORTES'].sum())
            chart3 = alt.Chart(por_edo).mark_arc(innerRadius=75, outerRadius=130, cornerRadius=6, stroke="#ffffff", strokeWidth=2.5).encode(
                theta=alt.Theta('REPORTES:Q', stack=True),
                color=alt.Color('ESTADO:N', scale=alt.Scale(domain=domain_estados, range=range_colors), legend=alt.Legend(title="Estado", orient="right")),
                tooltip=[alt.Tooltip('ESTADO:N', title='Estado'), alt.Tooltip('REPORTES:Q', title='Reportes')],
                order=alt.Order('REPORTES:Q', sort='descending')
            ).properties(height=420, title=alt.TitleParams(text=f"Total: {total_edo} reportes", fontSize=12, color="#64748b"))
            st.altair_chart(chart3, width='stretch')
    with c4:
        def mes_a_letra(m):
            mapa = {'1':'Enero','2':'Febrero','3':'Marzo','4':'Abril','5':'Mayo','6':'Junio','7':'Julio','8':'Agosto','9':'Septiembre','10':'Octubre','11':'Noviembre','12':'Diciembre',1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre','01':'Enero','02':'Febrero','03':'Marzo','04':'Abril','05':'Mayo','06':'Junio','07':'Julio','08':'Agosto','09':'Septiembre','10':'Octubre','11':'Noviembre','12':'Diciembre'}
            try:
                s = str(m).strip()
                if not s: return s
                key = s.lstrip('0')
                if key == '': key = '0'
                if key in mapa: return mapa[key]
                try: return mapa[int(s)]
                except: return mapa.get(s, s)
            except: return str(m)
        st.subheader("📊 Reportes por Día / Hora / Mes")
        vista = st.selectbox("Ver por:", ["DIA del mes","HORA_REGISTRO","MES"], index=2, key="vista_dashboard_final_v47")
        if vista == "DIA del mes" and 'DIA' in df_f.columns:
            data = df_f['DIA'].value_counts().sort_index().reset_index()
            data.columns = ['DIA','REPORTES']
            chart4 = alt.Chart(data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color='#3b82f6').encode(x=alt.X('DIA:O', title='Día del mes'), y=alt.Y('REPORTES:Q', title='Reportes'), tooltip=['DIA','REPORTES']).properties(height=380)
            st.altair_chart(chart4, width='stretch')
        elif vista == "HORA_REGISTRO" and 'HORA_REGISTRO' in df_f.columns:
            try:
                df_f['_HORA'] = df_f['HORA_REGISTRO'].astype(str).str[:2]
                data = df_f['_HORA'].value_counts().sort_index().reset_index()
                data.columns = ['HORA','REPORTES']
                chart4 = alt.Chart(data).mark_bar(cornerRadiusTopLeft=4, color='#f59e0b').encode(x=alt.X('HORA:O', title='Hora del día'), y=alt.Y('REPORTES:Q', title='Reportes'), tooltip=['HORA','REPORTES']).properties(height=380)
                st.altair_chart(chart4, width='stretch')
            except Exception as e: st.error(str(e))
        elif vista == "MES" and 'MES' in df_f.columns:
            data = df_f['MES'].value_counts().sort_index().reset_index()
            data.columns = ['MES','REPORTES']
            data['MES_LETRA'] = data['MES'].apply(lambda x: mes_a_letra(x))
            try:
                data['MES_NUM'] = pd.to_numeric(data['MES'], errors='coerce')
                data = data.sort_values('MES_NUM')
            except: pass
            chart4 = alt.Chart(data).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color='#3b82f6').encode(x=alt.X('MES_LETRA:O', title='Mes', sort=None), y=alt.Y('REPORTES:Q', title='Reportes'), tooltip=[alt.Tooltip('MES_LETRA:N', title='Mes'), alt.Tooltip('REPORTES:Q', title='Reportes')]).properties(height=380)
            st.altair_chart(chart4, width='stretch')
    st.markdown("---")
    st.subheader("⏱ Tiempo de reparación / Cierre")
    try:
        if 'FECHA_REGISTRO' in df_f.columns and 'FECHA' in df_f.columns:
            df_f['_FECHA_REG'] = pd.to_datetime(df_f['FECHA_REGISTRO'], dayfirst=True, errors='coerce')
            df_f['_FECHA_REP'] = pd.to_datetime(df_f['FECHA'], dayfirst=True, errors='coerce')
            df_f['_DIAS'] = (df_f['_FECHA_REG'] - df_f['_FECHA_REP']).dt.days
            df_valid = df_f[df_f['_DIAS'].notna() & (df_f['_DIAS']>=0)]
            if not df_valid.empty:
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Promedio cierre", f"{df_valid['_DIAS'].mean():.1f} días")
                col_b.metric("Más rápido", f"{df_valid['_DIAS'].min()} días")
                col_c.metric("Más lento", f"{df_valid['_DIAS'].max()} días")
                chart5 = alt.Chart(df_valid).mark_bar().encode(alt.X('_DIAS:Q', bin=alt.Bin(maxbins=20), title='Días para cierre'), y='count()').properties(title="Distribución tiempo de cierre")
                st.altair_chart(chart5, width='stretch')
                por_suc_tiempo = df_valid.groupby('SUCURSAL')['_DIAS'].mean().reset_index().sort_values('_DIAS', ascending=False).head(10)
                chart6 = alt.Chart(por_suc_tiempo).mark_bar(color='#1e293b').encode(x='_DIAS:Q', y=alt.Y('SUCURSAL:N', sort='-x')).properties(title="Tiempo promedio cierre por sucursal (Top 10 más lentas)")
                st.altair_chart(chart6, width='stretch')
    except Exception as e: st.warning(f"No se pudo calcular tiempo: {e}")
    st.markdown("---")
    st.subheader("📞 Top Líneas Telefónicas con más fallas")
    try:
        col_tel = None
        for cand in ['LINEAS CON FALLA','LINEA CON FALLA','TEL FALLA','LINEAS','LINEA','TEL','TELMEX']:
            if cand in df_f.columns:
                col_tel = cand
                break
        if not col_tel:
            for c in df_f.columns:
                if 'LINEA' in c or 'TEL' in c:
                    col_tel = c
                    break
        if col_tel:
            from collections import Counter, defaultdict
            todas_lineas = []
            linea_to_suc = defaultdict(set)
            linea_to_estado = defaultdict(set)
            for idx, row in df_f.iterrows():
                val = str(row.get(col_tel, '')).strip()
                if not val or val.lower() in ['nan','none','']: continue
                suc = str(row.get('SUCURSAL','')).strip()
                edo = str(row.get('ESTADO','')).strip()
                for p in val.split('|'):
                    for pc in p.split(','):
                        num = pc.strip()
                        if num and len(num)>=3:
                            todas_lineas.append(num)
                            if suc: linea_to_suc[num].add(suc)
                            if edo: linea_to_estado[num].add(edo)
            if todas_lineas:
                counter = Counter(todas_lineas)
                top_lineas = counter.most_common(20)
                data_rows = []
                for linea, fallas in top_lineas:
                    sucs = ", ".join(sorted(linea_to_suc.get(linea, []))[:3])
                    edos = ", ".join(sorted(linea_to_estado.get(linea, []))[:2])
                    data_rows.append({"LINEA": linea, "FALLAS": fallas, "SUCURSAL(ES)": sucs, "ESTADO": edos})
                df_lineas = pd.DataFrame(data_rows)
                c_line1, c_line2 = st.columns([1.5,1.5])
                with c_line1:
                    chart_df = df_lineas.head(10).copy()
                    chart_line = alt.Chart(chart_df).mark_bar(color='#1e40af').encode(x='FALLAS:Q', y=alt.Y('LINEA:N', sort='-x', title='LINEA'), tooltip=['LINEA','FALLAS','SUCURSAL(ES)','ESTADO']).properties(height=450)
                    st.altair_chart(chart_line, width='stretch')
                with c_line2:
                    st.markdown("**Detalle con sucursal:**")
                    st.dataframe(df_lineas, width='stretch', hide_index=True)
                    csv_lineas = df_lineas.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar líneas CSV", csv_lineas, "lineas_mas_fallas_con_sucursal.csv", "text/csv")
            else: st.info("No hay datos en LINEAS CON FALLA / TEL")
        else: st.info(f"No se encontró columna de líneas. Columnas: {list(df_f.columns)[:20]}")
    except Exception as e: st.error(f"Error graficando líneas: {e}")
    st.markdown("---")
    st.subheader("📋 Resumen por Sucursal")
    if 'SUCURSAL' in df_f.columns:
        resumen = df_f.groupby(['ESTADO','SUCURSAL']).size().reset_index(name='TOTAL_REPORTES')
        resumen = resumen.sort_values('TOTAL_REPORTES', ascending=False)
        html = """<style>.resumen-wrap { width:100%; background:white; border:1px solid #e2e8f0; border-radius:12px; box-shadow:0 1px 3px rgba(0,0,0,0.05); max-height:500px; overflow-y:auto; overflow-x:hidden; }.resumen-table { width:100%; border-collapse:collapse; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size:14px; }.resumen-table th { background:#f8fafc; color:#64748b; font-weight:500; font-size:11px; text-transform:uppercase; letter-spacing:0.05em; padding:12px 16px; border-bottom:1px solid #e2e8f0; text-align:left; position:sticky; top:0; z-index:1; }.resumen-table th:last-child { text-align:center !important; }.resumen-table td { padding:10px 16px; border-bottom:1px solid #f1f5f9; color:#334155; font-weight:400; }.resumen-table td:last-child { text-align:center !important; }.resumen-table tr:hover { background:#f8fafc; }</style><div class="resumen-wrap"><table class="resumen-table"><thead><tr><th style="width:20%">ESTADO</th><th style="width:45%">SUCURSAL</th><th style="width:35%; text-align:center;">TOTAL_REPORTES</th></tr></thead><tbody>"""
        for _, r in resumen.iterrows():
            html += f"<tr><td>{r['ESTADO']}</td><td>{r['SUCURSAL']}</td><td style='text-align:center;'>{int(r['TOTAL_REPORTES'])}</td></tr>"
        html += "</tbody></table></div>"
        st.markdown(html, unsafe_allow_html=True)
        csv = resumen.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar reporte CSV", csv, "reporte_sucursales_mas_fallas.csv", "text/csv")
    
    st.stop()

# --- BUSCAR REPORTES - PRIVADO Y COMPACTO ---
if st.session_state.get('pagina') == "🔒 Buscar Reportes":
    # FIX SEGURIDAD V41: Timeout 30 min - si paso mucho tiempo, cerrar sesion
    try:
        last_act = st.session_state.get('last_activity')
        if last_act and st.session_state.get('admin_auth'):
            diff_min = (now_mx().replace(tzinfo=None) - last_act).total_seconds()/60
            if diff_min > 30:
                st.session_state['admin_auth'] = False
                st.session_state['current_user'] = None
                st.warning("Sesión expirada por inactividad (30 min). Vuelve a ingresar.")
    except:
        pass
    if not st.session_state.get('admin_auth'):
        st.title("🔒 Buscar Reportes - Acceso Privado")
        st.warning("Esta sección es privada. Ingresa credenciales para buscar reportes viejos cerrados.")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            user_b = st.text_input("Usuario", key="buscar_user", placeholder="Usuario admin")
        with col_b2:
            pass_b = st.text_input("Contraseña", type="password", key="buscar_pass", placeholder="Contraseña")
        if st.button("🔓 Ingresar a Buscar Reportes", key="btn_buscar_login", type="primary"):
            if check_login(user_b.strip().lower(), pass_b):
                st.session_state['admin_auth'] = True
                st.session_state['current_user'] = user_b.strip().lower()
                st.session_state['last_activity'] = now_mx().replace(tzinfo=None)
                # FIX V44: log_acceso esta definido mas abajo, no debe tumbar el login si aun no existe
                try:
                    log_acceso(user_b.strip().lower(), "Login Buscar Reportes")
                except:
                    pass
                st.success("Acceso concedido")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        st.stop()
    # Si ya esta autenticado, mostrar buscador compacto
    st.title("🔒 Buscar Reportes Viejos")
    st.caption("Busca por No. Reporte, Sucursal o Estado - Solo usuarios autorizados")
    import altair as alt
    @st.cache_data(ttl=60)
    def cargar_historial_buscar():
        df_h = None
        try:
            if "gcp_service_account" in st.secrets:
                import gspread
                from google.oauth2.service_account import Credentials
                creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
                client = gspread.authorize(creds)
                sid = st.secrets.get("sheet_id", ID_CORRECTO_SHEETS)
                sh = client.open_by_key(sid)
                ws = sh.worksheet("HISTORIAL_REPORTES")
                vals = ws.get_all_values()
                if vals and len(vals)>1:
                    headers = [h.strip().upper() for h in vals[0]]
                    df_h = pd.DataFrame(vals[1:], columns=headers)
        except Exception as e:
            st.error(f"Error cargando historial: {e}")
        return df_h
    df_hist_b = cargar_historial_buscar()
    if df_hist_b is None or df_hist_b.empty:
        st.warning("No se encontró HISTORIAL_REPORTES.")
        st.stop()
    df_hist_b.columns = [c.strip().upper() for c in df_hist_b.columns]
    # Buscador compacto
    col_s1, col_s2 = st.columns([3,1])
    with col_s1:
        search_b = st.text_input("Buscar reporte (No. Reporte, Sucursal, Estado)", placeholder="Ej: 945969 o GUADALAJARA o PUEBLA", key="search_buscar_compact")
    with col_s2:
        st.markdown(f"<div style='margin-top:28px; padding:8px 12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; font-size:0.85rem;'><b>{len(df_hist_b)} eventos</b></div>", unsafe_allow_html=True)
    df_f_b = df_hist_b.copy()
    if search_b:
        sl = search_b.lower().strip()
        mask_b = pd.Series([False]*len(df_f_b))
        for col_b in ['NO_REPORTE','SUCURSAL','ESTADO','USUARIO']:
            if col_b in df_f_b.columns:
                mask_b = mask_b | df_f_b[col_b].astype(str).str.lower().str.contains(sl, na=False)
        df_f_b = df_f_b[mask_b]
    # Tabla compacta - solo columnas clave, altura pequeña
    cols_mostrar = [c for c in ['FECHA_REGISTRO','ESTADO','SUCURSAL','NO_REPORTE','FECHA_REPORTE','USUARIO'] if c in df_f_b.columns]
    if not df_f_b.empty:
        st.dataframe(df_f_b[cols_mostrar].sort_values('FECHA_REGISTRO' if 'FECHA_REGISTRO' in cols_mostrar else cols_mostrar[0], ascending=False).head(50), width='stretch', height=250)
        st.caption(f"Mostrando {min(50, len(df_f_b))} de {len(df_f_b)} eventos (Total: {len(df_hist_b)}). Tabla compacta para no ocupar mucho espacio.")
    else:
        st.info("No se encontraron reportes con ese criterio.")
    if st.button("🔓 Cerrar sesión privada", key="btn_logout_buscar"):
        st.session_state['admin_auth'] = False
        st.rerun()
    st.stop()

if st.session_state.get('pagina') != "🏠 Reportes":
    st.stop()

B64_ATLAS_LOGO = "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"
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
    .glass { background: #ffffff !important; border-radius: 16px; padding: 20px 22px; box-shadow: 0 2px 12px rgba(15,23,42,0.06); border: 1px solid #e2e8f0; }
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
def cargar_datos(sheet_id_override=None):
    df_privado = None
    try:
        if "gcp_service_account" in st.secrets:
            import gspread
            from google.oauth2.service_account import Credentials
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets"])
            client = gspread.authorize(creds)
            # FIX V39: Secrets primero - produccion 12uBz... debe ganar sobre test 196...
            sid = sheet_id_override or st.secrets.get("sheet_id") or ID_CORRECTO_SHEETS
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
    # FIX V39: No usar CSV de pruebas como fallback en produccion - mostraria datos equivocados
    # Si gspread fallo (ej: Invalid JWT), mostrar error en vez de datos de pruebas
    if df_privado is not None and not df_privado.empty:
        return df_privado
    # Si no hay datos privados, retornar vacio para que se vea que no cargo produccion
    st.error("No se pudo cargar el Sheet de producción. Revisa Secrets: sheet_id y private_key deben ser los de producción.")
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


def eliminar_reporte_hoja1(estado, sucursal, reporte_a_borrar, fecha_a_borrar=None, falla_a_borrar=None):
    """v17: Borra SOLO el reporte seleccionado, deja los demas con |"""
    try:
        if "gcp_service_account" not in st.secrets:
            return True, "Demo"
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
        sheet_id = st.secrets.get("sheet_id", ID_CORRECTO_SHEETS)
        try:
            sh = client.open_by_key(sheet_id)
        except:
            sh = client.open_by_key(ID_CORRECTO_SHEETS)
        
        ws_found = None
        row_found = None
        for ws_try in sh.worksheets():
            try:
                vals = ws_try.get_all_values()
                if not vals or len(vals) < 2:
                    continue
                last_estado = ""
                for idx in range(1, len(vals)):
                    row = vals[idx]
                    if len(row) < 2:
                        continue
                    est_raw = row[0] if len(row) > 0 else ""
                    suc_raw = row[1] if len(row) > 1 else ""
                    if est_raw and str(est_raw).strip():
                        last_estado = est_raw
                    est_cell = last_estado if last_estado else est_raw
                    if not est_cell or not suc_raw:
                        continue
                    if clean_norm(est_cell) == clean_norm(estado) and clean_norm(suc_raw) == clean_norm(sucursal):
                        ws_found = ws_try
                        row_found = idx + 1
                        break
                if ws_found:
                    break
            except:
                continue
        
        if not ws_found or not row_found:
            return False, f"No se encontro {estado} - {sucursal}"
        
        rep_actual = ws_found.cell(row_found, 4).value or ""
        fecha_actual = ws_found.cell(row_found, 5).value or ""
        falla_actual = ws_found.cell(row_found, 6).value or ""
        tel_actual = ws_found.cell(row_found, 7).value or "" if ws_found.col_count >= 7 else ""
        
        reportes = split_multi_val(rep_actual)
        fechas = split_multi_val(fecha_actual)
        fallas = split_multi_val(falla_actual)
        tels = split_multi_val(tel_actual)
        
        idx_borrar = -1
        reporte_str = str(reporte_a_borrar).strip()
        for i, r in enumerate(reportes):
            if str(r).strip() == reporte_str:
                idx_borrar = i
                break
        
        if idx_borrar == -1:
            return False, f"No se encontro REP {reporte_str} en {reportes}"
        
        nuevos_rep = [v for j, v in enumerate(reportes) if j != idx_borrar]
        if len(reportes) == 1:
            nuevas_fec = []
            nuevas_fal = []
            nuevos_tel = []
        else:
            nuevas_fec = [v for j, v in enumerate(fechas) if j != idx_borrar] if len(fechas) > 1 else fechas
            nuevas_fal = [v for j, v in enumerate(fallas) if j != idx_borrar] if len(fallas) > 1 else fallas
            nuevos_tel = [v for j, v in enumerate(tels) if j != idx_borrar] if len(tels) > 1 else tels
            # Si fechas/fallas tienen solo 1 valor pero reportes tenian varios, dejarlas como estan (no borrar)
            if len(fechas) == 1 and len(reportes) > 1:
                nuevas_fec = fechas
            if len(fallas) == 1 and len(reportes) > 1:
                nuevas_fal = fallas
            if len(tels) == 1 and len(reportes) > 1:
                nuevos_tel = tels
        
        ws_found.update_cell(row_found, 4, " | ".join(nuevos_rep) if nuevos_rep else "")
        ws_found.update_cell(row_found, 5, " | ".join(nuevas_fec) if nuevas_fec else "")
        ws_found.update_cell(row_found, 6, " | ".join(nuevas_fal) if nuevas_fal else "")
        if ws_found.col_count >= 7:
            ws_found.update_cell(row_found, 7, " | ".join(nuevos_tel) if nuevos_tel else "")
        
        return True, f"Borrado REP:{reporte_str} en {ws_found.title} fila {row_found}. Quedan {len(nuevos_rep)}"
    except Exception as e:
        import traceback
        return False, f"Error al cerrar: {e} {traceback.format_exc()}"




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
        if count == 1: 
            label = f"{estado_val} - {suc_val} | REP: {reps_list[0]} | {txt_badge}"
        else: 
            label = f"{estado_val} - {suc_val} | {count} REPORTES | {txt_badge} ({count} activos)"
        opciones_activas.append(label)
        mapa_activos[label] = {"estado": estado_val, "sucursal": suc_val, "count": count, "reps": reps_list, "reps_all": reps_list, "row": row_base, "fec": fecs[0] if fecs else "", "fec_all": fecs}
    opciones_activas = sorted(opciones_activas)
    mapa_activos_global = mapa_activos
else: total_reps_global = 0
opciones_con_todos = ["-- Ver todas las sucursales --"] + opciones_activas

c1, c2 = st.columns([2.2, 1.3])
with c1:
    if b64_logo:
        st.markdown(f"""<div style="display:flex; align-items:center; gap:12px"><div style="width:48px; height:48px; border-radius:14px; overflow:hidden; background:white"><img src="data:image/png;base64,{b64_logo}" style="width:100%; height:100%; object-fit:cover"></div><div style="font-size:1.75rem; font-weight:900; letter-spacing:-0.8px; line-height:1.1">REPORTES Y CONSULTAS<br>SUCURSALES SEGUROS ATLAS</div></div>""", unsafe_allow_html=True)
    else:
        logo_html_fallback = '<div style="width:56px; height:56px; border-radius:14px; background:linear-gradient(135deg,#dc2626,#b91c1c); display:flex; align-items:center; justify-content:center; color:white; font-weight:900; font-size:26px; box-shadow:0 2px 8px rgba(30,58,138,0.3);">A</div>'
        st.markdown(f"""<div style="display:flex; align-items:center; gap:12px;">{logo_html_fallback}<div style="font-size:1.75rem; font-weight:900; line-height:1.1">REPORTES Y CONSULTAS<br>SUCURSALES SEGUROS ATLAS</div></div>""", unsafe_allow_html=True)
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
    # --- FIX SYNC: Al seleccionar en Reportes Activos, sincronizar con Estado/Sucursal de abajo ---
    # --- FIX SYNC ROBUSTO: Prioridad a seleccion manual abajo ---
    try:
        # 1. Detectar si Estado o Sucursal de abajo cambiaron manualmente
        curr_est = st.session_state.get('estado_real', '')
        curr_suc = st.session_state.get('sucursal_real', '')
        last_est = st.session_state.get('last_estado_real', '')
        last_suc = st.session_state.get('last_sucursal_real', '')
        
        # Si Estado o Sucursal de abajo cambiaron manualmente, resetear filtro de arriba
        bottom_changed = (curr_est != last_est) or (curr_suc != last_suc)
        if bottom_changed and last_est and last_suc:
            # Usuario cambio manual abajo, resetear filtro arriba
            if st.session_state.get('filtro_activo_sel', '') != "-- Ver todas las sucursales --":
                st.session_state['reset_filtro_pendiente'] = True  # FIX: no asignar directo despues del widget
                st.session_state['last_filtro_activo_sel'] = "-- Ver todas las sucursales --"
                st.session_state['last_estado_real'] = curr_est
                st.session_state['last_sucursal_real'] = curr_suc
                try:
                    st.cache_data.clear()
                except:
                    pass
                st.rerun()
        
        # 2. Si filtro de arriba cambio, sincronizar abajo
        sel_filtro = st.session_state.get('filtro_activo_sel', '')
        last_filtro = st.session_state.get('last_filtro_activo_sel', '-- Ver todas las sucursales --')
        if sel_filtro != last_filtro:
            st.session_state['last_filtro_activo_sel'] = sel_filtro
            if sel_filtro and sel_filtro != "-- Ver todas las sucursales --" and sel_filtro in mapa_activos:
                info_filtro = mapa_activos[sel_filtro]
                est_f = info_filtro.get('estado', '')
                suc_f = info_filtro.get('sucursal', '')
                if est_f and suc_f:
                    st.session_state['estado_real'] = est_f
                    st.session_state['sucursal_real'] = suc_f
                    st.session_state['last_estado_real'] = est_f
                    st.session_state['last_sucursal_real'] = suc_f
                    st.rerun()
        
        # Actualizar last values si no hubo cambio
        if not bottom_changed:
            st.session_state['last_estado_real'] = curr_est
            st.session_state['last_sucursal_real'] = curr_suc
    except Exception as e_sync:
        pass
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



# --- V36: LOGIN Y CONFIRMAR CIERRE ARRIBA - Para no hacer scroll ---
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
                            # FIX V40: Al cerrar reporte, cerrar sesion privada para que Buscar Reportes vuelva a pedir credenciales
                            st.session_state['admin_auth'] = False
                            st.session_state['current_user'] = None
                            st.session_state['last_activity'] = None
                            st.session_state['show_login'] = False
                            # FIX: limpiar cache y resetear box SIN ERROR - v26
                            try:
                                st.cache_data.clear()
                            except:
                                pass
                            st.session_state['reset_filtro_pendiente'] = True  # FIX: no asignar directo despues del widget
                            st.rerun()
                            st.cache_data.clear()
                            st.session_state['reset_filtro_pendiente'] = True
                            st.rerun()
                        else: st.error(f"Error al cerrar: {msg}")
                except Exception as e:
                    st.error(f"Error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        st.markdown('</div>', unsafe_allow_html=True)

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
            <div style="background:white; border-radius:8px; padding:10px 14px; border-left:4px solid #1e40af;"><b>CASE San Juan - 800 905 2200</b><br><span style="font-size:0.85rem; color:#64748b;">CDMX y zona metropolitana - Edo. de México - Morelos - Guerrero</span></div>
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

                        # --- Mostrar telefonos aunque Sin reporte ---
                        try:
                            tel_raw_sin = str(row.get(COL_TEL, "")).strip() if COL_TEL in row else ""
                            if tel_raw_sin:
                                tels_sin = split_tels(tel_raw_sin)
                                if tels_sin:
                                    st.markdown(f"<div style='margin-top:12px; padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;'><div style='font-weight:700; font-size:0.85rem;'>☎ LINEAS TELEFONICAS • {len(tels_sin)} numeros - Sin reporte activo</div></div>", unsafe_allow_html=True)
                                    cols_sin = st.columns(2)
                                    for i_sin, t_sin in enumerate(tels_sin):
                                        with cols_sin[i_sin % 2]:
                                            st.markdown(f"<div style='background:white; border:1px solid #e2e8f0; border-radius:8px; padding:8px 10px; margin-bottom:6px; font-size:0.85rem;'>📞 {t_sin}</div>", unsafe_allow_html=True)
                        except Exception as e_tel_sin:
                            pass


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
                        # Mostrar telefonos incluso sin reporte - FIX v28
                        try:
                            if not tels:
                                # Intentar obtener telefonos de la fila base
                                if 'row_base' in locals() and row_base is not None:
                                    tel_raw_full = str(row_base.get(COL_TEL, "")).strip() if COL_TEL in row_base else ""
                                    if tel_raw_full:
                                        tels = split_tels(tel_raw_full)
                        except:
                            pass
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

# [MOVED TO TOP v36 - limpio]
