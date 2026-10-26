import streamlit as st

# Forzar la carga limpia de librerías básicas antes de los mapas
try:
    import folium
    from streamlit_folium import st_folium
    LIBRERIAS_OK = True
except Exception as e:
    LIBRERIAS_OK = False
    ERROR_TXT = str(e)

st.set_page_config(page_title="Mapa de Sucursales", layout="wide")
st.title("📍 Monitoreo de Sucursales")

if not LIBRERIAS_OK:
    st.error(f"Falta instalar componentes en requirements.txt. Error interno: {ERROR_TXT}")
    st.info("Por favor, asegúrate de que el archivo 'requirements.txt' esté guardado en la raíz de tu GitHub con los nombres correctos.")
else:
    st.success("¡Componentes listos! Cargando el mapa...")
    
    # Crear mapa básico de respaldo
    m = folium.Map(location=[23.6345, -102.5528], zoom_start=5)
    
    # Marcador de prueba central (CDMX)
    folium.CircleMarker(
        location=[19.4326, -99.1332],
        radius=10,
        popup="Sucursal Matriz Centro - Operando Normal",
        color="#1E90FF",
        fill=True,
        fill_color="#1E90FF"
    ).add_to(m)
    
    # Renderizar mapa de forma segura
    try:
        st_folium(m, width="100%", height=500)
    except Exception as map_err:
        st.error(f"Error al dibujar el mapa en pantalla: {map_err}")
