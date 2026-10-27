import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(page_title="SUCRSALES • Premium", layout="wide", page_icon="🏢")

# --- DISEÑO PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Fondo degradado aesthetic */
    .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #dbeafe 0%, transparent 60%),
                    radial-gradient(1000px 500px at 90% 10%, #e0e7ff 0%, transparent 60%),
                    radial-gradient(800px 400px at 50% 120%, #fef3c7 0%, transparent 60%),
                    linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* Ocultar menu feo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Títulos grandes */
    h1 { font-size: 2.4rem !important; font-weight: 800 !important; letter-spacing: -0.5px; color: #0f172a !important; }
    h3 { font-size: 1.35rem !important; font-weight: 700 !important; color: #1e293b !important; }
    
    /* Tarjetas Glassmorphism REAL con blur */
    .glass {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(16px) saturate(180%);
        -webkit-backdrop-filter: blur(16px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.8);
        border-radius: 18px;
        padding: 20px 22px;
        box-shadow: 0 8px 32px rgba(15, 23, 42, 0.08), 0 2px 8px rgba(15, 23, 42, 0.04);
        transition: all 0.25s ease;
    }
    .glass:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(15, 23, 42, 0.12);
        background: rgba(255, 255, 255, 0.9) !important;
    }
    
    .glass-dark {
        background: rgba(15, 23, 42, 0.88) !important;
        backdrop-filter: blur(16px);
        color: white;
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    
    /* Selectbox mas grande y bonito */
    div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.9) !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
        font-size: 1.05rem !important;
        min-height: 48px !important;
        backdrop-filter: blur(10px);
    }
    div[data-baseweb="select"] span {
        font-size: 1.05rem !important;
    }
    
    /* Botones reporte aesthetic */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1rem !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
        background: rgba(255,255,255,0.85) !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        background: white !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08) !important;
    }
    
    /* Botones primarios */
    div[data-testid="stButton"] > button[kind="primary"] {
        background: #0f172a !important;
        color: white !important;
    }
    
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 100px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.2px;
    }
    .badge-ok { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .badge-warn { background: #fef9c3; color: #854d0e; border: 1px solid #fde68a; }
    .badge-orange { background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }
    .badge-red { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    
    .suc-title {
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        color: #0f172a;
        letter-spacing: -0.3px;
        margin: 10px 0 8px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60, show_spinner=False)
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90/pub?output=csv"
    df = pd.read_csv(url, dtype=str)
    df.columns = df.columns.str.strip().str.upper()
    return df.dropna(how='all')

df = cargar_datos()

def col(kws):
    for c in df.columns:
        for kw in kws:
            if kw in c:
                return c
    return None

COL_EST = col(['ESTADO','EDO'])
COL_SUC = col(['SUCURSAL','SUC','SITIO'])
COL_TEL = col(['TELMEX','TEL','LINEA'])
COL_REP = col(['NO. REPORTE','NO REPORTE','REPORTE'])
COL_FEC = col(['FECHA','FEC'])

df[COL_EST] = df[COL_EST].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
df[COL_SUC] = df[COL_SUC].astype(str).str.strip()

def tiene_reporte(v):
    if pd.isna(v): return False
    return str(v).strip().lower() not in ["","0","0.0","sin reporte","none","nan","vacio","s/r"]

def dias_desde(fecha_str):
    if not fecha_str or str(fecha_str).lower() in ['nan','none','']: return None, "Fecha pendiente"
    dt = pd.to_datetime(fecha_str, errors='coerce', dayfirst=True)
    if pd.isna(dt): return None, f"Formato inválido"
    dias = (datetime.now() - dt).days
    return dias, f"{dias} días"

def split_tels(raw):
    if pd.isna(raw) or str(raw).lower() in ['nan','none','']: return []
    return [t.strip() for t in re.split(r'[\n,;/]+', str(raw)) if t.strip() and t.strip().lower()!='nan']

lista_estados = sorted(df[COL_EST].dropna().unique())
if "estado_sel" not in st.session_state:
    st.session_state.estado_sel = lista_estados[0]
if "sucursal_sel" not in st.session_state:
    st.session_state.sucursal_sel = None

# --- HEADER PREMIUM ---
c_head1, c_head2 = st.columns([3,1])
with c_head1:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:6px">
        <div style="width:48px; height:48px; background:#0f172a; border-radius:14px; display:flex; align-items:center; justify-content:center; color:white; font-size:22px; box-shadow:0 8px 20px rgba(0,0,0,0.15)">🏢</div>
        <div>
            <div style="font-size:1.7rem; font-weight:800; letter-spacing:-0.5px; color:#0f172a; line-height:1.1">BDSUCRSALES</div>
            <div style="font-size:0.95rem; color:#64748b; font-weight:500">Consulta Interactiva • En vivo desde Google Sheets</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with c_head2:
    st.markdown(f"""
    <div class="glass" style="text-align:center; padding:12px">
        <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:700">Última sync</div>
        <div style="font-size:1rem; font-weight:700; color:#0f172a">{datetime.now().strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# --- FILTROS AESTHETIC ---
f1, f2, f3 = st.columns([1.1, 1.8, 0.7], gap="medium")

with f1:
    st.markdown('<div class="glass" style="padding:16px">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b; letter-spacing:0.8px; margin-bottom:8px; text-transform:uppercase">📍 Estado</div>', unsafe_allow_html=True)
    estado_temp = st.selectbox("Estado", options=lista_estados, index=lista_estados.index(st.session_state.estado_sel) if st.session_state.estado_sel in lista_estados else 0, label_visibility="collapsed")
    if estado_temp != st.session_state.estado_sel:
        st.session_state.estado_sel = estado_temp
        st.session_state.sucursal_sel = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

df_estado = df[df[COL_EST] == st.session_state.estado_sel]
lista_suc = sorted(df_estado[COL_SUC].dropna().unique())

with f2:
    st.markdown('<div class="glass" style="padding:16px">', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.8rem; font-weight:700; color:#64748b; letter-spacing:0.8px; margin-bottom:8px; text-transform:uppercase">🏬 Sucursales • {len(lista_suc)} en {st.session_state.estado_sel}</div>', unsafe_allow_html=True)
    # Ahora dice solo "Sucursales" y se despliega automático
    idx_suc = lista_suc.index(st.session_state.sucursal_sel)+1 if st.session_state.sucursal_sel in lista_suc else 0
    suc_temp = st.selectbox("Sucursales", options=["-- Ver todas las sucursales --"] + lista_suc, index=idx_suc, label_visibility="collapsed", placeholder="Escribe para buscar...")
    if suc_temp == "-- Ver todas las sucursales --":
        if st.session_state.sucursal_sel is not None:
            st.session_state.sucursal_sel = None
            st.rerun()
    else:
        if suc_temp != st.session_state.sucursal_sel:
            st.session_state.sucursal_sel = suc_temp
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with f3:
    st.markdown('<div class="glass" style="padding:16px; text-align:center">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b; letter-spacing:0.8px; margin-bottom:10px; text-transform:uppercase">Acciones</div>', unsafe_allow_html=True)
    if st.button("🔄 Actualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    if st.session_state.sucursal_sel:
        if st.button("✕ Limpiar", use_container_width=True):
            st.session_state.sucursal_sel = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# --- REPORTES ABIERTOS PREMIUM ---
df_reportes = df[df[COL_REP].apply(tiene_reporte)] if COL_REP else pd.DataFrame()

st.markdown(f"""
<div class="glass-dark" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px">
    <div style="display:flex; align-items:center; gap:12px">
        <div style="width:40px; height:40px; background:rgba(239,68,68,0.2); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px">🚨</div>
        <div>
            <div style="font-size:1.15rem; font-weight:700">Reportes Activos</div>
            <div style="font-size:0.85rem; opacity:0.7">{len(df_reportes)} sucursales requieren atención</div>
        </div>
    </div>
    <div style="font-size:2rem; font-weight:800">{len(df_reportes)}</div>
</div>
""", unsafe_allow_html=True)

if not df_reportes.empty:
    cols = st.columns(4)
    for i, (_, r) in enumerate(df_reportes.iterrows()):
        with cols[i % 4]:
            est = str(r[COL_EST]).strip()
            suc = str(r[COL_SUC]).strip()
            rep = str(r[COL_REP]).strip()
            dias, _ = dias_desde(r[COL_FEC] if COL_FEC else "")
            if st.button(f"🚨 {suc}\n{est} • {rep} • {dias}d" if dias else f"🚨 {suc} • {est}", key=f"rep_{i}_{suc}_{est}", use_container_width=True):
                st.session_state.estado_sel = est
                st.session_state.sucursal_sel = suc
                st.rerun()
else:
    st.markdown('<div class="glass" style="text-align:center; padding:28px"><div style="font-size:2rem">✅</div><div style="font-weight:700; font-size:1.1rem; margin-top:6px">¡Todo en orden!</div><div style="color:#64748b">No hay reportes activos en el país</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# --- DETALLE ---
if st.session_state.sucursal_sel:
    fila_df = df[df[COL_SUC] == st.session_state.sucursal_sel]
    fila_estado_match = fila_df[fila_df[COL_EST] == st.session_state.estado_sel]
    if not fila_estado_match.empty:
        fila_df = fila_estado_match
    fila = fila_df.iloc[0]
    rep = fila.get(COL_REP, "")
    fec = fila.get(COL_FEC, "")
    tels = split_tels(fila.get(COL_TEL, ""))
    dias, txt = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin reporte")

    if dias is None:
        badge_class = "badge-ok"
        badge_txt = "🟢 Sin reporte"
        color_dias = "#166534"
    elif dias <=3:
        badge_class = "badge-warn"
        badge_txt = f"🟡 {dias} días"
        color_dias = "#854d0e"
    elif dias <=7:
        badge_class = "badge-orange"
        badge_txt = f"🟠 {dias} días"
        color_dias = "#9a3412"
    else:
        badge_class = "badge-red"
        badge_txt = f"🔴 {dias} días"
        color_dias = "#991b1b"

    c1, c2 = st.columns([2.2, 1], gap="large")
    with c1:
        st.markdown(f"""
        <div class="glass" style="padding:28px">
            <div style="display:flex; justify-content:space-between; align-items:center">
                <div class="badge {badge_class}">{badge_txt}</div>
                <div style="font-size:0.85rem; color:#64748b; font-weight:600">{fila[COL_EST]} • REP: {rep if tiene_reporte(rep) else '—'}</div>
            </div>
            <div class="suc-title" style="font-size:1.9rem !important; margin-top:14px">🏢 {fila[COL_SUC]}</div>
            <div style="display:flex; gap:20px; margin-top:18px; flex-wrap:wrap">
                <div><div style="font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.8px">Fecha reporte</div><div style="font-size:1.05rem; font-weight:600">{fec if str(fec)!='nan' else 'N/A'}</div></div>
                <div><div style="font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.8px">Días transcurridos</div><div style="font-size:1.4rem; font-weight:800; color:{color_dias}">{txt}</div></div>
                <div><div style="font-size:0.75rem; color:#64748b; font-weight:700; text-transform:uppercase; letter-spacing:0.8px">Líneas</div><div style="font-size:1.05rem; font-weight:600">{len(tels)} números</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("### 📞 Líneas Telefónicas")
        if not tels:
            st.markdown('<div class="glass" style="text-align:center; padding:20px; color:#64748b">Sin líneas registradas</div>', unsafe_allow_html=True)
        else:
            tc = st.columns(2)
            for idx, t in enumerate(tels):
                with tc[idx % 2]:
                    st.markdown(f"""
                    <div class="glass" style="padding:16px 18px; display:flex; align-items:center; gap:12px; margin-bottom:12px">
                        <div style="width:36px; height:36px; background:#f1f5f9; border-radius:10px; display:flex; align-items:center; justify-content:center">📞</div>
                        <div style="font-size:1.1rem; font-weight:600; letter-spacing:0.3px">{t}</div>
                    </div>
                    """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="glass" style="text-align:center; padding:24px">
            <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:1px">Días con reporte</div>
            <div style="font-size:3rem; font-weight:900; color:{color_dias}; line-height:1; margin:10px 0">{dias if dias is not None else '—'}</div>
            <div style="font-size:0.9rem; color:#64748b; font-weight:500">{txt}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass" style="padding:18px">
            <div style="font-size:0.8rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:12px">Resumen</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px"><span style="color:#64748b">Estado</span><span style="font-weight:700">{fila[COL_EST]}</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px"><span style="color:#64748b">Sucursal</span><span style="font-weight:700">{fila[COL_SUC][:18]}</span></div>
            <div style="display:flex; justify-content:space-between"><span style="color:#64748b">Líneas</span><span style="font-weight:700">{len(tels)}</span></div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown(f"### 🏬 Sucursales en {st.session_state.estado_sel}")
    filtro = st.text_input("", placeholder="🔍 Filtra por nombre o teléfono...", label_visibility="collapsed")
    df_mostrar = df_estado
    if filtro:
        mask = df_mostrar[COL_SUC].str.contains(filtro, case=False, na=False)
        if COL_TEL:
            mask = mask | df_mostrar[COL_TEL].astype(str).str.contains(filtro, case=False, na=False)
        df_mostrar = df_mostrar[mask]

    if df_mostrar.empty:
        st.markdown('<div class="glass" style="text-align:center; padding:30px; color:#64748b">Sin resultados</div>', unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for idx, (_, r) in enumerate(df_mostrar.iterrows()):
            with cols[idx % 3]:
                rep = r.get(COL_REP, "")
                fec = r.get(COL_FEC, "")
                es_activo = tiene_reporte(rep)
                if es_activo:
                    dias, _ = dias_desde(fec)
                    if dias is None:
                        badge = '<span class="badge badge-warn">🟡 Pendiente</span>'
                    elif dias <=3:
                        badge = f'<span class="badge badge-warn">🟡 {dias}d</span>'
                    elif dias <=7:
                        badge = f'<span class="badge badge-orange">🟠 {dias}d</span>'
                    else:
                        badge = f'<span class="badge badge-red">🔴 {dias}d</span>'
                else:
                    badge = '<span class="badge badge-ok">🟢 OK</span>'
                
                tels_html = "".join([f"<div style='font-size:0.9rem; color:#334155; margin:2px 0'>• {t}</div>" for t in split_tels(r.get(COL_TEL,""))][:3])
                more = f"<div style='font-size:0.8rem; color:#64748b'>+{len(split_tels(r.get(COL_TEL,'')))-3} más</div>" if len(split_tels(r.get(COL_TEL,'')))>3 else ""
                
                st.markdown(f"""
                <div class="glass">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        {badge}
                        <span style="font-size:0.8rem; color:#94a3b8; font-weight:600">{r[COL_EST]}</span>
                    </div>
                    <div style="font-size:1.2rem; font-weight:800; margin:12px 0 8px 0; color:#0f172a">🏢 {r[COL_SUC]}</div>
                    <div style="min-height:60px">{tels_html}{more}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ver detalle →", key=f"ver_{idx}_{r[COL_SUC]}_{r[COL_EST]}", use_container_width=True):
                    st.session_state.estado_sel = str(r[COL_EST]).strip()
                    st.session_state.sucursal_sel = str(r[COL_SUC]).strip()
                    st.rerun()
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
