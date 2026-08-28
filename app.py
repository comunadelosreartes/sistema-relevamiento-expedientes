import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración general
st.set_page_config(
    page_title="Sistema de Relevamiento de Expedientes",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Sistema Integrado de Expedientes - Comuna de Los Reartes")

# Inicializar conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Función para cargar datos de la pestaña RELEVAMIENTO
@st.cache_data(ttl=60)
def cargar_relevamiento():
    try:
        df = conn.read(worksheet="RELEVAMIENTO", ttl="1m")
        # Eliminar columnas completamente vacías y limpiar espacios en encabezados
        df = df.dropna(how='all', axis=1)
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame()

# Cargar la base de datos
df_expedientes = cargar_relevamiento()

# Selector de Perfil / Área de Trabajo
with st.sidebar:
    st.header("👤 Perfil de Usuario")
    area_usuario = st.selectbox(
        "Seleccioná tu Área:",
        [
            "Obras Privadas y Catastro",
            "Comercio e Inspecciones",
            "Recursos Hídricos / Obras Públicas",
            "Gestión de Cobranzas / Rentas",
            "Guardia Local",
            "Asesoría Letrada",
            "Mesa de Entrada / Administración"
        ]
    )
    st.info(f"Sesión activa: **{area_usuario}**")
    
    if st.button("🔄 Refrescar Datos"):
        st.cache_data.clear()
        st.rerun()

# Definición de Pestañas Principales
tab1, tab2, tab3 = st.tabs(["📥 Mi Bandeja de Entrada", "➕ Cargar Nuevo Expediente", "🔎 Buscador & Historial"])

# --- TAB 1: BANDEJA DE ENTRADA POR ÁREA ---
with tab1:
    st.subheader(f"Expedientes asignados a: {area_usuario}")
    
    if not df_expedientes.empty:
        # Filtro de búsqueda dentro de la bandeja
        filtro_busqueda = st.text_input("🔍 Buscar en tu bandeja (por Titular, N° Cuenta, N° Expediente, Barrio):", "")
        
        df_area = df_expedientes.copy()
        
        # Búsqueda segura en todas las columnas para evitar KeyError
        if filtro_busqueda.strip():
            mask = df_area.astype(str).apply(
                lambda row: row.str.contains(filtro_busqueda, case=False, na=False)
            ).any(axis=1)
            df_area = df_area[mask]
        
        st.markdown(f"**Total de expedientes encontrados:** `{len(df_area)}`")
        
        # Mostrar la tabla completa con scroll horizontal interactivo
        st.dataframe(
            df_area,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No se pudieron cargar los datos o la planilla está vacía.")

# --- TAB 2: ALTA DE EXPEDIENTES ---
with tab2:
    st.subheader("Cargar Nuevo Expediente / Trámite")
    
    with st.form("form_nuevo_expediente"):
        col1, col2 = st.columns(2)
        with col1:
            nro_exp = st.text_input("N° Expediente:")
            titular = st.text_input("Nombre / Titular:")
            cuenta = st.text_input("N° Cuenta Municipal:")
            barrio = st.selectbox("Barrio:", ["EL VERGEL", "LOS REARTES", "CAPILLA VIEJA", "LA ISLA", "GUTIERREZ", "OTRO"])
        with col2:
            asunto = st.selectbox("Asunto / Tramite:", ["PERMISO DE EDIFICACIÓN", "HABILITACION COMERCIAL", "SOLICITUD DE SERVICIOS", "MENSURA", "USUCAPION", "OTRO"])
            catastral = st.text_input("Nomenclatura Catastral:")
            observaciones = st.text_area("Observaciones iniciales:")
        
        btn_guardar = st.form_submit_button("💾 Registrar Expediente")
        
        if btn_guardar:
            if not titular:
                st.error("El campo 'Titular' es obligatorio.")
            else:
                st.success(f"Expediente para **{titular}** preparado para registrar en el área **{area_usuario}**.")

# --- TAB 3: BUSCADOR GENERAL ---
with tab3:
    st.subheader("Búsqueda Global en toda la Base Comunitaria")
    q = st.text_input("🔎 Ingrese cualquier término de búsqueda (Nombre, Calle, N° Cuenta, Catastro):", key="global_search")
    
    if q and not df_expedientes.empty:
        mask = df_expedientes.astype(str).apply(lambda row: row.str.contains(q, case=False, na=False)).any(axis=1)
        res = df_expedientes[mask]
        st.write(f"Se encontraron **{len(res)}** coincidencias:")
        st.dataframe(res, use_container_width=True, hide_index=True)
