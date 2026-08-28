import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

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
        # Se lee la hoja RELEVAMIENTO
        df = conn.read(worksheet="RELEVAMIENTO", ttl="1m")
        # Limpieza básica de nombres de columnas (quitar espacios)
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
        # Filtrar por área actual si existe la columna
        col_area = "area_actual" if "area_actual" in df_expedientes.columns else "BARRIO/CAPILLA VIEJA"
        
        # Filtro de búsqueda dentro de la bandeja
        filtro_busqueda = st.text_input("🔍 Buscar en tu bandeja (por Titular, Cuenta o N° Exp):", "")
        
        df_area = df_expedientes.copy()
        if filtro_busqueda:
            condicion = (
                df_area["TITULAR/HORROCKS"].astype(str).str.contains(filtro_busqueda, case=False, na=False) |
                df_area["CONT.(CUENTA)/71"].astype(str).str.contains(filtro_busqueda, case=False, na=False) |
                df_area["N° EXP./1"].astype(str).str.contains(filtro_busqueda, case=False, na=False)
            )
            df_area = df_area[condicion]
        
        st.markdown(f"**Total de expedientes encontrados:** `{len(df_area)}`")
        
        # Vista de tabla interactiva
        columnas_visibles = [col for col in ["N° EXP./1", "FECHA/3/28/2002", "TITULAR/HORROCKS", "ASUNTO/CONEXIÓN COSTA / RIO", "CONT.(CUENTA)/71", "BARRIO/CAPILLA VIEJA", "DEUDAS CONEXIÓN"] if col in df_area.columns]
        
        st.dataframe(
            df_area[columnas_visibles],
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
                # Próximo paso: append directo a Google Sheets

# --- TAB 3: BUSCADOR GENERAL ---
with tab3:
    st.subheader("Búsqueda Global en toda la Base Comunitaria")
    q = st.text_input("🔎 Ingrese cualquier término de búsqueda (Nombre, Calle, N° Cuenta, Catastro):")
    
    if q and not df_expedientes.empty:
        # Búsqueda global en todas las filas
        mask = df_expedientes.astype(str).apply(lambda x: x.str.contains(q, case=False, na=False)).any(axis=1)
        res = df_expedientes[mask]
        st.write(f"Se encontraron **{len(res)}** coincidencias:")
        st.dataframe(res, use_container_width=True)
        
