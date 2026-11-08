"""
mapa_reportes.py - Mapa interactivo de México para la app de reportes de sucursales.

Uso en APP.py (antes de la línea  es_modo_agregar = ... ):

    from mapa_reportes import mostrar_mapa
    try:
        mostrar_mapa(df, COL_EST, COL_SUC, COL_REP, COL_FEC, COL_OBS, COL_TEL,
                     COL_TEL_FALLA, tiene_reporte, split_multi_val, dias_desde, split_tels)
    except Exception as e_mapa:
        st.error(f"No se pudo mostrar el mapa: {e_mapa}")

Requiere en el repo: mexicoHigh.json (junto a APP.py) y 'plotly' en requirements.txt.
"""
import json
import re
import unicodedata
from html import escape
from pathlib import Path

GEOJSON_PATH = Path(__file__).parent / "mexicoHigh.json"

# Nivel 0 = sin reportes, 1 = hasta 2 días, 2 = 3 a 5 días, 3 = más de 5 días (crítico)
COLORES = {0: "#cbd5e1", 1: "#f59e0b", 2: "#f97316", 3: "#ef4444"}
EMOJI = {1: "🟡", 2: "🟠", 3: "🔴"}

# Nombre del Sheet (sin acentos, sin puntos) -> id del estado en mexicoHigh.json
ALIAS_ESTADOS = {
    "AGUASCALIENTES": "MX-AGU", "BAJA CALIFORNIA NORTE": "MX-BCN", "BAJA CALIFORNIA": "MX-BCN",
    "BAJA CALIFORNIA SUR": "MX-BCS", "CAMPECHE": "MX-CAM", "CDMX": "MX-CMX",
    "CIUDAD DE MEXICO": "MX-CMX", "DISTRITO FEDERAL": "MX-CMX", "CHIAPAS": "MX-CHP",
    "CHIHUAHUA": "MX-CHH", "COAHUILA": "MX-COA", "COLIMA": "MX-COL", "DURANGO": "MX-DUR",
    "EDO MEXICO": "MX-MEX", "ESTADO DE MEXICO": "MX-MEX", "MEXICO": "MX-MEX",
    "GUANAJUATO": "MX-GUA", "GUERRERO": "MX-GRO", "HIDALGO": "MX-HID", "JALISCO": "MX-JAL",
    "MICHOACAN": "MX-MIC", "MORELOS": "MX-MOR", "NAYARIT": "MX-NAY", "NUEVO LEON": "MX-NLE",
    "OAXACA": "MX-OAX", "PUEBLA": "MX-PUE", "QUERETARO": "MX-QUE", "QUINTANA ROO": "MX-ROO",
    "SAN LUIS POTOSI": "MX-SLP", "SINALOA": "MX-SIN", "SONORA": "MX-SON", "TABASCO": "MX-TAB",
    "TAMAULIPAS": "MX-TAM", "TLAXCALA": "MX-TLA", "VERACRUZ": "MX-VER", "YUCATAN": "MX-YUC",
    "ZACATECAS": "MX-ZAC",
}

_GEO = None


def _norm(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[.\r\n]", " ", s.upper())
    return re.sub(r"\s+", " ", s).strip()


def id_estado(nombre):
    return ALIAS_ESTADOS.get(_norm(nombre))


def nivel_por_dias(dias):
    if dias is None or dias <= 2:
        return 1
    return 2 if dias <= 5 else 3


def cargar_geojson():
    global _GEO
    if _GEO is None:
        with open(GEOJSON_PATH, encoding="utf-8") as f:
            _GEO = json.load(f)
    return _GEO


def calcular_resumen(df, col_est, col_suc, col_rep, col_fec, col_obs, col_tel,
                     col_tel_falla, tiene_reporte, split_multi_val, dias_desde, split_tels):
    """Devuelve (resumen, sin_mapa). resumen[id_estado] = datos del estado y sus sucursales."""
    resumen, sin_mapa = {}, set()
    if df is None or df.empty or not col_est or not col_suc:
        return resumen, sin_mapa

    def celda(row, col):
        return str(row.get(col, "")).strip() if col else ""

    for _, row in df.iterrows():
        est, suc = celda(row, col_est), celda(row, col_suc)
        if not est or not suc:
            continue
        eid = id_estado(est)
        if eid is None:
            sin_mapa.add(est)
            continue
        e = resumen.setdefault(eid, {"estado_sheet": est, "sucursales": [], "n_reportes": 0,
                                     "max_dias": 0, "nivel": 0})
        reps_all = split_multi_val(celda(row, col_rep))
        fecs = split_multi_val(celda(row, col_fec))
        obs_raw = celda(row, col_obs)
        obs = split_multi_val(obs_raw)
        tfs = split_multi_val(celda(row, col_tel_falla))
        reportes = []
        for i, rep in enumerate(reps_all):
            if not tiene_reporte(rep):
                continue
            fec = fecs[i] if i < len(fecs) else (fecs[0] if fecs else "")
            ob = obs[i] if i < len(obs) else (obs[0] if obs else obs_raw)
            tf = tfs[i] if i < len(tfs) else (tfs[0] if tfs else "")
            dias, txt = dias_desde(fec) if fec else (None, "Sin fecha")
            reportes.append({"rep": rep, "fecha": fec, "obs": ob, "tel_falla": tf, "dias": dias,
                             "txt": txt, "nivel": nivel_por_dias(dias), "indice": i,
                             "tel_raw": celda(row, col_tel)})
        e["sucursales"].append({"sucursal": suc, "telefonos": split_tels(row.get(col_tel, "")),
                                "reportes": reportes})
        e["n_reportes"] += len(reportes)
        for r in reportes:
            e["max_dias"] = max(e["max_dias"], r["dias"] or 0)
    for e in resumen.values():
        if e["n_reportes"]:
            e["nivel"] = nivel_por_dias(e["max_dias"])
        # primero las sucursales con reporte, y entre ellas la más vieja
        e["sucursales"].sort(key=lambda s: (not s["reportes"],
                                            -max([r["dias"] or 0 for r in s["reportes"]] or [0]),
                                            s["sucursal"]))
    return resumen, sin_mapa


def _centro(feature):
    g = feature["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    anillo = max((p[0] for p in polys), key=len)
    return (sum(p[0] for p in anillo) / len(anillo), sum(p[1] for p in anillo) / len(anillo))


def construir_figura(resumen, geo, id_sel=None, alto=500):
    import plotly.graph_objects as go
    feats = geo["features"]
    ids = [f["properties"]["id"] for f in feats]
    z, textos = [], []
    for f in feats:
        eid, nombre = f["properties"]["id"], f["properties"]["name"]
        e = resumen.get(eid)
        z.append(e["nivel"] if e else 0)
        if e and e["n_reportes"]:
            textos.append(f"<b>{nombre}</b><br>Reportes activos: {e['n_reportes']}<br>"
                          f"Más viejo: {e['max_dias']} días<br>Sucursales: {len(e['sucursales'])}")
        elif e:
            textos.append(f"<b>{nombre}</b><br>Sin reportes activos<br>Sucursales: {len(e['sucursales'])}")
        else:
            textos.append(f"<b>{nombre}</b><br>Sin sucursales registradas")
    escala = [[0, COLORES[0]], [1/6, COLORES[0]], [1/6, COLORES[1]], [.5, COLORES[1]],
              [.5, COLORES[2]], [5/6, COLORES[2]], [5/6, COLORES[3]], [1, COLORES[3]]]
    fig = go.Figure(go.Choropleth(
        geojson=geo, locations=ids, z=z, featureidkey="properties.id", colorscale=escala,
        zmin=0, zmax=3, showscale=False, text=textos, hoverinfo="text",
        marker=dict(line=dict(color="white", width=1)),
        selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1))))
    if id_sel in ids:
        fig.add_trace(go.Choropleth(
            geojson=geo, locations=[id_sel], z=[0], featureidkey="properties.id",
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]], showscale=False,
            hoverinfo="skip", marker=dict(line=dict(color="#0f172a", width=3))))
    lon, lat, txt = [], [], []
    for f in feats:
        e = resumen.get(f["properties"]["id"])
        if e and e["n_reportes"]:
            x, y = _centro(f)
            lon.append(x); lat.append(y); txt.append(str(e["n_reportes"]))
    if txt:
        fig.add_trace(go.Scattergeo(lon=lon, lat=lat, text=txt, mode="text", hoverinfo="skip",
                                    textfont=dict(color="white", size=15, family="Arial Black"),
                                    showlegend=False))
    fig.update_geos(fitbounds="locations", visible=False, projection_type="mercator",
                    bgcolor="rgba(0,0,0,0)")
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=alto, dragmode=False,
                      paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    return fig


def _id_desde_evento(ev, ids):
    try:
        puntos = ev["selection"]["points"]
    except Exception:
        return None
    for p in puntos or []:
        if p.get("location") in ids:
            return p["location"]
        if p.get("curve_number", 0) == 0 and isinstance(p.get("point_index"), int):
            if 0 <= p["point_index"] < len(ids):
                return ids[p["point_index"]]
    return None


def _tel_html(tels, en_falla):
    partes = []
    for t in tels:
        digitos = re.sub(r"\D", "", t)
        link = f'<a href="tel:{digitos}">{escape(t)}</a>'
        partes.append(f"🚨 <b style='color:#b91c1c'>{link}</b>" if digitos in en_falla else f"📞 {link}")
    return " &nbsp; ".join(partes)


def mostrar_mapa(df, col_est, col_suc, col_rep, col_fec, col_obs, col_tel, col_tel_falla,
                 tiene_reporte, split_multi_val, dias_desde, split_tels):
    import streamlit as st
    geo = cargar_geojson()
    nombres = {f["properties"]["id"]: f["properties"]["name"] for f in geo["features"]}
    ids = list(nombres)
    resumen, sin_mapa = calcular_resumen(df, col_est, col_suc, col_rep, col_fec, col_obs, col_tel,
                                         col_tel_falla, tiene_reporte, split_multi_val, dias_desde,
                                         split_tels)

    # --- Estado seleccionado: clic en el mapa o botón de la barra lateral ---
    def _elegir(eid):
        st.session_state["mapa_estado_id"] = eid

    ev_id = _id_desde_evento(st.session_state.get("mapa_mx"), ids)
    if ev_id != st.session_state.get("_mapa_ev_prev"):
        st.session_state["_mapa_ev_prev"] = ev_id
        if ev_id:
            st.session_state["mapa_estado_id"] = ev_id
    id_sel = st.session_state.get("mapa_estado_id")

    con_rep = sorted([i for i, e in resumen.items() if e["n_reportes"]],
                     key=lambda i: -resumen[i]["max_dias"])
    total = sum(resumen[i]["n_reportes"] for i in con_rep)

    # --- Barra lateral: reportes activos, del más crítico al menos ---
    with st.sidebar:
        st.markdown("#### 🚨 Reportes activos")
        if not con_rep:
            st.caption("Sin reportes activos")
        for i in con_rep:
            e = resumen[i]
            st.button(f"{EMOJI[e['nivel']]} {nombres[i]} · {e['n_reportes']} rep · {e['max_dias']} d",
                      key=f"side_{i}", on_click=_elegir, args=(i,), width="stretch")

    # --- Franja de resumen ---
    peor = nombres[con_rep[0]] if con_rep else "—"
    chip = ("<div style='background:white;border:1px solid #e2e8f0;border-radius:12px;padding:8px 12px;'>"
            "<div style='font-size:11px;color:#64748b;font-weight:700'>{}</div>"
            "<div style='font-size:18px;font-weight:900;color:#0f172a'>{}</div></div>")
    k1, k2, k3 = st.columns(3)
    k1.markdown(chip.format("🚨 REPORTES ACTIVOS", total), unsafe_allow_html=True)
    k2.markdown(chip.format("🗺 ESTADOS AFECTADOS", len(con_rep)), unsafe_allow_html=True)
    k3.markdown(chip.format("🔴 MÁS CRÍTICO", escape(peor)), unsafe_allow_html=True)

    c_mapa, c_panel = st.columns([3, 2], gap="medium")
    with c_mapa:
        leyenda = "".join(f"<span style='display:inline-flex;align-items:center;gap:5px;margin-right:12px;"
                          f"font-size:12px;font-weight:600;color:#334155'><span style='width:12px;height:12px;"
                          f"border-radius:3px;background:{COLORES[n]}'></span>{t}</span>"
                          for n, t in [(0, "Sin reporte"), (1, "Hasta 2 días"), (2, "3 a 5 días"),
                                       (3, "Más de 5 días")])
        st.markdown(f"<div style='margin:6px 0'>{leyenda}</div>", unsafe_allow_html=True)
        st.plotly_chart(construir_figura(resumen, geo, id_sel), key="mapa_mx", on_select="rerun",
                        selection_mode="points", width="stretch", config={"displayModeBar": False})

    with c_panel:
        if not id_sel or id_sel not in nombres:
            st.info("👆 Toca un estado del mapa para ver sus sucursales y reportes.")
        else:
            e = resumen.get(id_sel)
            st.markdown(f"### 📍 {nombres[id_sel]}")
            if not e:
                st.caption("No hay sucursales registradas en este estado.")
            else:
                st.caption(f"{len(e['sucursales'])} sucursales · {e['n_reportes']} reportes activos")
                sin_rep = []
                for s in e["sucursales"]:
                    if not s["reportes"]:
                        sin_rep.append(s)
                        continue
                    for r in s["reportes"]:
                        color = COLORES[r["nivel"]]
                        fallas = {re.sub(r"\D", "", x) for x in str(r["tel_falla"]).split(",")} - {""}
                        st.markdown(
                            f"<div style='background:white;border:1px solid #e2e8f0;border-left:5px solid {color};"
                            f"border-radius:12px;padding:12px 14px;margin-bottom:6px'>"
                            f"<div style='display:flex;justify-content:space-between;gap:8px'>"
                            f"<b>{escape(s['sucursal'])}</b>"
                            f"<span style='background:{color};color:white;border-radius:99px;padding:2px 10px;"
                            f"font-size:12px;font-weight:800;white-space:nowrap'>{escape(str(r['txt']))}</span></div>"
                            f"<div style='font-size:12.5px;color:#475569;margin-top:4px'>🗂 REP {escape(r['rep'])}"
                            f" &nbsp; 📅 {escape(r['fecha'] or 'N/A')}</div>"
                            f"<div style='font-size:13px;margin-top:6px;color:#1e293b'>📝 "
                            f"{escape(r['obs']) if r['obs'] and r['obs'].lower() != 'nan' else 'Sin observaciones'}</div>"
                            f"<div style='font-size:13px;margin-top:6px'>{_tel_html(s['telefonos'], fallas)}</div>"
                            f"</div>", unsafe_allow_html=True)
                        if st.button(f"✅ CERRAR REPORTE {r['rep']}", type="primary", width="stretch",
                                     key=f"mapa_cerrar_{id_sel}_{s['sucursal']}_{r['indice']}_{r['rep']}"):
                            st.session_state["delete_target"] = {
                                "estado": e["estado_sheet"], "sucursal": s["sucursal"], "rep": r["rep"],
                                "fec": r["fecha"], "obs": r["obs"], "tel": r["tel_raw"], "indice": r["indice"]}
                            if st.session_state.get("admin_auth"):
                                st.session_state["show_delete_confirm"] = True
                                st.session_state["show_delete_login"] = False
                            else:
                                st.session_state["show_delete_login"] = True
                                st.session_state["show_delete_confirm"] = False
                            st.rerun()
                if sin_rep:
                    with st.expander(f"Sucursales sin reporte ({len(sin_rep)})"):
                        for s in sin_rep:
                            st.markdown(f"**{s['sucursal']}**", unsafe_allow_html=True)
                            if s["telefonos"]:
                                st.markdown(_tel_html(s["telefonos"], set()), unsafe_allow_html=True)

    if sin_mapa and st.session_state.get("admin_auth"):
        st.caption("⚠ Estados del Sheet que no se pudieron ubicar en el mapa: " + ", ".join(sorted(sin_mapa)))
