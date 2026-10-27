import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(page_title="BDSUCRSALES - Consulta Interactiva", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; }
    .glass-card { background: white; border-radius: 10px; padding: 16px; border: 1px solid #e2e8f0; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 14px; }
    .kpi { font-size: 1.8rem; font-weight: 800; color: #0f172a; }
    .kpi-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .detalle-suc { font-size: 1.3rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60, show_spinner="Actualizando desde Google Sheets...")
def cargar_datos():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQbPB21bbVtlV6t7MzhSr9C_n7Ma_JC5STnHvToJJ0Bgfw379Vq2ehw5YppKXL-cegurpbGGn-8hB90/pub?output=csv"
    df = pd.read_csv(url, dtype=str)
    df.columns = df.columns.str.strip().str.upper()
    df = df.dropna(how='all')
    return df

df = cargar_datos()

def col(keywords):
    for c in df.columns:
        for kw in keywords:
            if kw in c:
                return c
    return None

COL_EST = col(['ESTADO','EDO'])
COL_SUC = col(['SUCURSAL','SUC','SITIO'])
COL_TEL = col(['TELMEX','TEL','LINEA'])
COL_REP = col(['NO. REPORTE','NO REPORTE','REPORTE'])
COL_FEC = col(['FECHA','FEC'])

if not COL_EST or not COL_SUC:
    st.error(f"No detecté columnas de Estado/Sucursal. Columnas: {list(df.columns)}")
    st.stop()

df[COL_EST] = df[COL_EST].astype(str).str.strip().replace({'nan':'', 'None':''}).replace('', pd.NA).ffill().str.strip()
df[COL_SUC] = df[COL_SUC].astype(str).str.strip()

def tiene_reporte(v):
    if pd.isna(v): return False
    return str(v).strip().lower() not in ["","0","0.0","sin reporte","none","nan","vacio","s/r"]

def dias_desde(fecha_str):
    if not fecha_str or str(fecha_str).lower() in ['nan','none','']: return None, "Fecha pendiente"
    dt = pd.to_datetime(fecha_str, errors='coerce', dayfirst=True)
    if pd.isna(dt): return None, f"Formato inválido: {fecha_str}"
    dias = (datetime.now() - dt).days
    return dias, f"{dias} días"

def split_tels(raw):
    if pd.isna(raw) or str(raw).lower() in ['nan','none','']: return []
    return [t.strip() for t in re.split(r'[\n,;/]+', str(raw)) if t.strip() and t.strip().lower()!='nan']

# --- SESSION STATE INICIALIZADO CORRECTAMENTE ---
lista_estados = sorted(df[COL_EST].dropna().unique())

if "estado_sel" not in st.session_state:
    st.session_state.estado_sel = lista_estados[0] if lista_estados else ""
if "sucursal_sel" not in st.session_state:
    st.session_state.sucursal_sel = None

# --- UI SUPERIOR ---
st.title("🏢 Consulta Interactiva BDSUCRSALES")
st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} • Auto-actualiza cada 60s")

col1, col2, col3 = st.columns([1, 1.5, 0.8])

with col1:
    # IMPORTANTE: No usar key que choque con session_state, usamos valor temporal
    estado_temp = st.selectbox(
        "1️⃣ Selecciona Estado", 
        options=lista_estados, 
        index=lista_estados.index(st.session_state.estado_sel) if st.session_state.estado_sel in lista_estados else 0
    )
    # Si cambia el selectbox, actualizamos session_state y limpiamos sucursal si no pertenece
    if estado_temp != st.session_state.estado_sel:
        st.session_state.estado_sel = estado_temp
        st.session_state.sucursal_sel = None
        st.rerun()

df_estado = df[df[COL_EST] == st.session_state.estado_sel]
lista_sucursales_estado = sorted(df_estado[COL_SUC].dropna().unique())

with col2:
    opciones = ["-- Ver todas --"] + lista_sucursales_estado
    # Calcular indice actual
    if st.session_state.sucursal_sel in lista_sucursales_estado:
        idx_suc = lista_sucursales_estado.index(st.session_state.sucursal_sel) + 1
    else:
        idx_suc = 0
    
    suc_temp = st.selectbox(
        f"2️⃣ Buscar Sucursal en {st.session_state.estado_sel} ({len(lista_sucursales_estado)})",
        options=opciones,
        index=idx_suc
    )
    if suc_temp == "-- Ver todas --":
        if st.session_state.sucursal_sel is not None:
            # si el usuario selecciona ver todas, limpiamos
            if st.button("Limpiar selección"):
                st.session_state.sucursal_sel = None
                st.rerun()
    else:
        if suc_temp != st.session_state.sucursal_sel:
            st.session_state.sucursal_sel = suc_temp
            st.rerun()

with col3:
    st.write("")
    st.write("")
    if st.button("🔄 Forzar actualización", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.divider()

# --- LISTA REPORTES ABIERTOS - CORREGIDO ---
df_reportes = df[df[COL_REP].apply(tiene_reporte)] if COL_REP else pd.DataFrame()
st.subheader(f"🚨 Sucursales con Reporte Abierto ({len(df_reportes)})")

if not df_reportes.empty:
    cols_rep = st.columns(4)
    for i, (_, r) in enumerate(df_reportes.iterrows()):
        with cols_rep[i % 4]:
            est = str(r[COL_EST]).strip()
            suc = str(r[COL_SUC]).strip()
            rep = str(r[COL_REP]).strip()
            fec = r[COL_FEC] if COL_FEC else ""
            dias, _ = dias_desde(fec)
            label_dias = f" • {dias}d" if dias is not None else ""
            
            # FORMA CORRECTA: if button -> set state -> rerun
            if st.button(f"🚨 {suc} ({est}) - {rep}{label_dias}", key=f"rep_{i}_{suc}_{est}", use_container_width=True):
                st.session_state.estado_sel = est
                st.session_state.sucursal_sel = suc
                st.rerun()
else:
    st.success("✅ Sin reportes abiertos.")

st.divider()

# --- DETALLE ---
if st.session_state.sucursal_sel:
    fila_df = df[df[COL_SUC] == st.session_state.sucursal_sel]
    # Si hay duplicadas por estado, filtrar por estado seleccionado primero
    fila_estado_match = fila_df[fila_df[COL_EST] == st.session_state.estado_sel]
    if not fila_estado_match.empty:
        fila_df = fila_estado_match
    
    if fila_df.empty:
        st.error(f"No encontré datos para {st.session_state.sucursal_sel}")
        if st.button("Volver a todas"):
            st.session_state.sucursal_sel = None
            st.rerun()
    else:
        fila = fila_df.iloc[0]
        rep = fila.get(COL_REP, "")
        fec = fila.get(COL_FEC, "")
        tels = split_tels(fila.get(COL_TEL, ""))
        dias, texto_dias = dias_desde(fec) if tiene_reporte(rep) else (None, "Sin reporte")

        st.markdown(f"### 📍 Detalle: {fila[COL_SUC]} ({fila[COL_EST]})")
        
        c_det1, c_det2 = st.columns([2,1])
        with c_det1:
            color_dias = '#c0392b' if dias and dias>7 else '#d35400' if dias and dias>3 else '#27ae60' if dias else '#64748b'
            
            st.markdown(f"""
            <div class="glass-card">
                <div class="kpi-label">Información del Reporte</div>
                <div style="margin-top:8px"><b>Número de Reporte:</b> {rep if tiene_reporte(rep) else '🟢 Sin reporte activo'}</div>
                <div><b>Fecha:</b> {fec if str(fec)!='nan' else 'N/A'}</div>
                <div><b>Días transcurridos:</b> <span style="font-weight:800; color:{color_dias}">{texto_dias}</span></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("**📞 Números Telefónicos:**")
            if not tels:
                st.info("Sin líneas registradas")
            else:
                for t in tels:
                    st.markdown(f"<div class='glass-card' style='padding:8px 12px; margin-bottom:6px'>• {t}</div>", unsafe_allow_html=True)

        with c_det2:
            st.markdown(f"<div class='glass-card'><div class='kpi-label'>Estado</div><div class='kpi'>{fila[COL_EST]}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='glass-card'><div class='kpi-label'>Días con reporte</div><div class='kpi' style='color:{color_dias}'>{texto_dias}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='glass-card'><div class='kpi-label'>Líneas</div><div class='kpi'>{len(tels)}</div></div>", unsafe_allow_html=True)
            if st.button("⬅️ Volver al listado del estado", use_container_width=True):
                st.session_state.sucursal_sel = None
                st.rerun()

else:
    st.subheader(f"📍 Sucursales en {st.session_state.estado_sel} ({len(df_estado)})")
    filtro_texto = st.text_input("Filtrar por nombre o teléfono dentro del estado:", placeholder="Escribe para filtrar...")
    df_mostrar = df_estado
    if filtro_texto:
        mask = df_mostrar[COL_SUC].str.contains(filtro_texto, case=False, na=False)
        if COL_TEL:
            mask = mask | df_mostrar[COL_TEL].astype(str).str.contains(filtro_texto, case=False, na=False)
        df_mostrar = df_mostrar[mask]

    if df_mostrar.empty:
        st.warning("Sin resultados.")
    else:
        cols = st.columns(3)
        for idx, (_, r) in enumerate(df_mostrar.iterrows()):
            with cols[idx % 3]:
                rep = r.get(COL_REP, "")
                fec = r.get(COL_FEC, "")
                es_activo = tiene_reporte(rep)
                if es_activo:
                    dias, txt = dias_desde(fec)
                    color = "#c0392b" if dias and dias>7 else "#d35400" if dias and dias>3 else "#b7950b"
                    badge = f"<span style='color:{color}; font-weight:700'>🚨 Rep: {rep} • {txt}</span>"
                else:
                    badge = "<span style='color:#27ae60; font-weight:700'>🟢 OK</span>"
                tels_html = "".join([f"<div style='font-size:0.85rem'>• {t}</div>" for t in split_tels(r.get(COL_TEL,""))]) or "<i style='font-size:0.8rem'>Sin líneas</i>"
                st.markdown(f"<div class='glass-card'>{badge}<div style='font-weight:700; margin:6px 0'>🏢 {r[COL_SUC]}</div><div>{tels_html}</div></div>", unsafe_allow_html=True)
                if st.button(f"Ver detalle →", key=f"ver_{idx}_{r[COL_SUC]}_{r[COL_EST]}", use_container_width=True):
                    st.session_state.estado_sel = str(r[COL_EST]).strip()
                    st.session_state.sucursal_sel = str(r[COL_SUC]).strip()
                    st.rerun()
