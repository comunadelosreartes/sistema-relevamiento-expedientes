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
        df = conn.read(worksheet="RELEVAMIENTO", ttl="1m")
        # Eliminar columnas completamente vacías y limpiar espacios
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
            "Mesa de Entrada / Administración",
            "Obras Privadas y Catastro",
            "Comercio e Inspecciones",
            "Recursos Hídricos / Obras Públicas",
            "Gestión de Cobranzas / Rentas",
            "Guardia Local",
            "Asesoría Letrada"
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
        
        # Búsqueda segura en todas las columnas
        if filtro_busqueda.strip():
            mask = df_area.astype(str).apply(
                lambda row: row.str.contains(filtro_busqueda, case=False, na=False)
            ).any(axis=1)
            df_area = df_area[mask]
        
        st.markdown(f"**Total de expedientes encontrados:** `{len(df_area)}`")
        
        # Mostrar la tabla completa
        st.dataframe(
            df_area,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No se pudieron cargar los datos o la planilla está vacía.")

# --- TAB 2: ALTA DE EXPEDIENTES Y CHECKLIST DE REQUISITOS ---
with tab2:
    st.subheader("📋 Ingreso de Nuevo Expediente / Trámite de Obra")
    
    with st.form("form_nuevo_expediente", clear_on_submit=True):
        st.markdown("##### 1. Datos Principales del Inmueble y Titular")
        col1, col2, col3 = st.columns(3)
        with col1:
            nro_exp = st.text_input("N° Expediente / Tramite:*", placeholder="Ej: EXP-2026-045")
            titular = st.text_input("Titular / Propietario:*", placeholder="Nombre y Apellido")
            profesional = st.text_input("Profesional Interviniente:", placeholder="Arq. / Ing. / MMO")
        with col2:
            cuenta = st.text_input("N° Cuenta Municipal:*", placeholder="Ej: 16300")
            nomenclatura = st.text_input("Nomenclatura Catastral:", placeholder="Ej: 04-02-...")
            barrio = st.selectbox("Barrio / Sector:", ["LOS REARTES", "CAPILLA VIEJA", "EL VERGEL", "LA ISLA", "GUTIERREZ", "OTRO"])
        with col3:
            asunto = st.selectbox("Asunto / Tipo de Obra:", [
                "PERMISO DE EDIFICACIÓN (Resol. N° 703/02)",
                "AMPLIACIÓN / REFACCIÓN",
                "HABILITACIÓN COMERCIAL",
                "MENSURA / DESMEMBRAMIENTO",
                "USUCAPIÓN",
                "OTRO"
            ])
            estado_deuda = st.radio("¿Registra Deuda Municipal?:*", [
                "No Registrar Deuda (Al día)",
                "Registra Deuda / Pendiente de Verificación"
            ], help="Si presenta deuda o requiere verificación, se derivará automáticamente a Gestión de Cobranzas.")

        st.markdown("---")
        st.markdown("##### 2. Requisitos para Apertura de Expediente de Obras (Verificación)")
        st.caption("Marque la documentación que el vecino/profesional adjunta al momento de la presentación en Mesa de Entrada:")
        
        chk_col1, chk_col2 = st.columns(2)
        with chk_col1:
            req_pago = st.checkbox(" Arancel $8.000 Apertura de Expediente abonado.")
            req_nota = st.checkbox(" Nota de Solicitud firmada por Propietario y Profesional.")
            req_planos = st.checkbox(" Planos para visación previa (2 copias firmadas).")
            req_amojonamiento = st.checkbox(" Certificado de Amojonamiento Colegiado A3 (Original/Autenticado).")
        with chk_col2:
            req_escritura = st.checkbox(" Acreditación Titularidad: Escritura Autenticada / Copia Fiel.")
            req_boleto = st.checkbox(" Acreditación Titularidad: Boleto C/V (Firmas certificadas/Timbrado + Gastos Carta Doc).")
            req_factibilidad = st.checkbox(" Factibilidad de Localización (Impacto Ambiental/Industrial si aplica).")
            req_turismo = st.checkbox(" Adecuación Ley Provincial de Turismo N° 6483 / Dto. 1359/00 (Aloj. Turístico).")

        st.markdown("---")
        observaciones = st.text_area("Observaciones adicionales / Notas de Recepción:", placeholder="Ingrese anotaciones internas de recepción...")

        btn_guardar = st.form_submit_button("💾 Registrar Expediente e Iniciar Circuito", type="primary")

        if btn_guardar:
            if not titular or not cuenta or not nro_exp:
                st.error("⚠️ Por favor complete los campos obligatorios (*): N° Expediente, Titular y N° Cuenta.")
            else:
                # Determinar área de derivación automática
                if "Registra Deuda" in estado_deuda:
                    area_destino = "Gestión de Cobranzas / Rentas"
                    estado_inicial = "PENDIENTE LIBRE DEUDA"
                    msj_derivacion = "⚠️ Se ha derivado automáticamente a **Gestión de Cobranzas / Rentas** para verificación de deuda."
                else:
                    area_destino = "Obras Privadas y Catastro"
                    estado_inicial = "EN TRAMITE - INGRESO"
                    msj_derivacion = "✅ Se ha derivado a **Obras Privadas y Catastro** para revisión técnica."

                # Consolidar documentación presentada
                docs = []
                if req_pago: docs.append("Arancel $8000 OK")
                if req_nota: docs.append("Nota Solicitud OK")
                if req_planos: docs.append("Planos (2 copias) OK")
                if req_amojonamiento: docs.append("Amojonamiento A3 OK")
                if req_escritura: docs.append("Escritura Autenticada")
                if req_boleto: docs.append("Boleto C/V Certificado")
                if req_factibilidad: docs.append("Factibilidad Ambiental")
                if req_turismo: docs.append("Ley Turismo N° 6483")
                
                doc_str = ", ".join(docs) if docs else "Sin documentación adjunta"

                # Armar la nueva fila para la base
                nueva_fila = pd.DataFrame([{
                    "N° EXPEDIENTE": nro_exp,
                    "TITULAR": titular,
                    "PROFESIONAL": profesional,
                    "CUENTA": cuenta,
                    "NOMENCLATURA CATASTRAL": nomenclatura,
                    "BARRIO": barrio,
                    "ASUNTO": asunto,
                    "AREA ACTUAL": area_destino,
                    "ESTADO": estado_inicial,
                    "DOCUMENTACION PRESENTADA": doc_str,
                    "OBSERVACIONES": observaciones,
                    "FECHA INGRESO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "REGISTRADO POR": area_usuario
                }])

                try:
                    # Combinar con los datos existentes y guardar en Google Sheets
                    df_actualizado = pd.concat([df_expedientes, nueva_fila], ignore_index=True)
                    conn.update(worksheet="RELEVAMIENTO", data=df_actualizado)
                    st.cache_data.clear()
                    
                    st.success(f"🎉 **¡Expediente N° {nro_exp} registrado con éxito!**")
                    st.info(msj_derivacion)
                    st.write(f"**Documentación presentada:** `{doc_str}`")
                except Exception as err:
                    st.error(f"Error al guardar en Google Sheets: {err}")

# --- TAB 3: BUSCADOR GENERAL ---
with tab3:
    st.subheader("Búsqueda Global en toda la Base Comunitaria")
    q = st.text_input("🔎 Ingrese cualquier término de búsqueda (Nombre, Calle, N° Cuenta, Catastro):", key="global_search")
    
    if q and not df_expedientes.empty:
        mask = df_expedientes.astype(str).apply(lambda row: row.str.contains(q, case=False, na=False)).any(axis=1)
        res = df_expedientes[mask]
        st.write(f"Se encontraron **{len(res)}** coincidencias:")
        st.dataframe(res, use_container_width=True, hide_index=True)
        
