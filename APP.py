import streamlit as st
import pandas as pd
from datetime import datetime
import re
import time

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

lista_estados = sorted(df[COL_EST].dropna().unique())
df_reportes = df[df[COL_REP].apply(tiene_reporte)] if COL_REP else pd.DataFrame()

# --- HEADER ---
c1, c2 = st.columns([2.2, 1.3])
with c1:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:16px">
        <div style="width:52px; height:52px; border-radius:14px; overflow:hidden; background:white">
            <img src="data:image/png;base64,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" style="width:100%; height:100%; object-fit:cover">
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
            # Evitar bucle infinito: solo procesar si es diferente al ultimo procesado
            if st.session_state.get('last_jump') != sel:
                est_jump, suc_jump = opciones[sel]
                st.session_state['jump_est'] = est_jump
                st.session_state['jump_suc'] = suc_jump
                st.session_state['last_jump'] = sel
                st.rerun()
            # Reset visual del dropdown a "Seleccionar reporte..." para no quedarse ciclado
            st.session_state['jump_rep_final'] = "Seleccionar reporte..."

# --- DETERMINAR INDICES PARA JUMP ---
default_est_idx = 0
default_suc = None
if 'jump_est' in st.session_state:
    if st.session_state['jump_est'] in lista_estados:
        default_est_idx = lista_estados.index(st.session_state['jump_est'])
        default_suc = st.session_state.get('jump_suc')

# --- FILTROS SIN LOGICA COMPLICADA ---
f1, f2, f3 = st.columns([1.1, 1.8, 0.7], gap="medium")
with f1:
    st.markdown('<div class="filter-pill"><div class="filter-label">📍 Estado</div>', unsafe_allow_html=True)
    estado_actual = st.selectbox("Estado", lista_estados, index=default_est_idx, key="estado_real", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# Limpiar jump si el usuario cambio manualmente de estado
if 'jump_est' in st.session_state and estado_actual != st.session_state['jump_est']:
    del st.session_state['jump_est']
    if 'jump_suc' in st.session_state:
        del st.session_state['jump_suc']
    default_suc = None

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
    if st.button("🔄 Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# --- DETALLE USA DIRECTAMENTE LAS VARIABLES DE LOS WIDGETS ---
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

# No borrar jump_est inmediatamente - dejarlo para que mantenga el estado seleccionado
# Se borra solo cuando el usuario cambia manualmente de estado (arriba)
pass
