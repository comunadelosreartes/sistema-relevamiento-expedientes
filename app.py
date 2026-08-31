import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import re

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

# Función para formatear nomenclatura catastral
def formatear_nomenclatura(cadena):
    digitos = re.sub(r'\D', '', cadena)
    if len(digitos) == 19:
        return f"{digitos[0:2]}.{digitos[2:4]}.{digitos[4:6]}.{digitos[6:8]}.{digitos[8:10]}.{digitos[10:14]}.{digitos[14:17]}.{digitos[17:19]}"
    return cadena

# Cargar la base de datos
df_expedientes = cargar_relevamiento()

# Lista oficial de áreas
LISTA_AREAS = [
    "Mesa de Entrada / Administración",
    "Obras Privadas y Catastro",
    "Comercio e Inspecciones",
    "Recursos Hídricos / Obras Públicas",
    "Gestión de Cobranzas / Rentas",
    "Guardia Local",
    "Asesoría Letrada"
]

# Selector de Perfil / Área de Trabajo
with st.sidebar:
    st.header("👤 Perfil de Usuario")
    area_usuario = st.selectbox("Seleccioná tu Área:", LISTA_AREAS)
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
        filtro_busqueda = st.text_input("🔍 Buscar en tu bandeja (por Titular, N° Cuenta, N° Expediente, Barrio):", "")
        
        df_area = df_expedientes.copy()
        
        if filtro_busqueda.strip():
            mask = df_area.astype(str).apply(
                lambda row: row.str.contains(filtro_busqueda, case=False, na=False)
            ).any(axis=1)
            df_area = df_area[mask]
        
        st.markdown(f"**Total de expedientes encontrados:** `{len(df_area)}`")
        
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
            nro_exp = st.text_input("N° Expediente / Trámite:*", placeholder="Ej: EXP-2026-045")
            titular = st.text_input("Titular / Propietario:*", placeholder="Nombre y Apellido")
            profesional = st.text_input("Profesional Interviniente:", placeholder="Arq. / Ing. / MMO")
        with col2:
            cuenta = st.text_input("N° Cuenta Municipal:*", placeholder="Ej: 16300")
            nomenclatura_input = st.text_input(
                "Nomenclatura Catastral (XX.XX.XX.XX.XX.XXXX.XXX.XX):",
                value="12.01.18.--.--.----.---.00",
                help="Formato base precargado. Puede modificar o reemplazar los guiones por los dígitos correspondientes."
            )
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

        st.markdown("---")
        st.markdown("##### 2. CheckList de Documentación Presentada (Registro Físico)")
        st.caption("Marque cada elemento que efectivamente consta en la carpeta entregada:")
        
        chk_col1, chk_col2 = st.columns(2)
        with chk_col1:
            req_pago = st.checkbox("Arancel $8.000 Apertura de Expediente abonado")
            req_nota = st.checkbox("Nota de Solicitud firmada por Propietario y Profesional")
            req_planos = st.checkbox("Planos para visación previa (2 copias firmadas)")
            req_amojonamiento = st.checkbox("Certificado de Amojonamiento Colegiado A3 (Original/Autenticado)")
        with chk_col2:
            req_escritura = st.checkbox("Acreditación Titularidad: Escritura Autenticada / Copia Fiel")
            req_boleto = st.checkbox("Acreditación Titularidad: Boleto C/V (Firmas certificadas/Timbrado + Carta Doc)")
            req_factibilidad = st.checkbox("Factibilidad de Localización (Impacto Ambiental/Industrial)")
            req_turismo = st.checkbox("Adecuación Ley Provincial de Turismo N° 6483 / Dto. 1359/00")

        st.markdown("---")
        st.markdown("##### 3. Circuito de Derivación Inicial y Verificación de Deuda")
        
        opcion_derivacion = st.radio(
            "Seleccione la modalidad de derivación:*",
            [
                "Remitir a Gestión de Cobranzas y Rentas para Control de Deuda y Estado de Cuenta",
                "Derivar a otra área específica (Omitir / Eximir verificación previa de deuda)"
            ]
        )
        
        area_destino_final = "Gestión de Cobranzas / Rentas"
        
        if "otra área" in opcion_derivacion:
            areas_posibles = [a for a in LISTA_AREAS if a != "Gestión de Cobranzas / Rentas"]
            area_destino_final = st.selectbox(
                "Seleccione el Área de Destino Directo:",
                areas_posibles,
                help="Seleccione el área responsable a la que se remitirá este expediente."
            )
            st.warning(f"⚠️ **Atención:** El expediente se asignará directamente a **{area_destino_final}**. Se registrará en la base que se omitió el paso previo por Cobranzas.")

        observaciones = st.text_area("Observaciones adicionales / Notas internas de recepción:", placeholder="Anotaciones complementarias...")

        btn_guardar = st.form_submit_button("💾 Registrar Expediente e Iniciar Circuito", type="primary")

        if btn_guardar:
            if not titular or not cuenta or not nro_exp:
                st.error("⚠️ Por favor complete los campos obligatorios (*): N° Expediente, Titular y N° Cuenta.")
            else:
                nomenclatura_final = formatear_nomenclatura(nomenclatura_input)
                
                if area_destino_final == "Gestión de Cobranzas / Rentas":
                    estado_inicial = "PENDIENTE CONTROL DE DEUDA"
                    control_deuda_nota = "Requerido - Derivado a Cobranzas"
                    msj_derivacion = "📨 **Expediente derivado a Gestión de Cobranzas y Rentas** para verificación de estado de cuenta."
                else:
                    estado_inicial = f"EN TRAMITE - DERIVADO A {area_destino_final.upper()}"
                    control_deuda_nota = f"Omitido / Salteo Autorizado (Derivado a {area_destino_final})"
                    msj_derivacion = f"🚀 **Expediente derivado directamente a {area_destino_final}** (Salteo de verificación de deuda registrado)."

                docs_presentados = []
                if req_pago: docs_presentados.append("Arancel $8000")
                if req_nota: docs_presentados.append("Nota Solicitud")
                if req_planos: docs_presentados.append("Planos (2 copias)")
                if req_amojonamiento: docs_presentados.append("Amojonamiento A3")
                if req_escritura: docs_presentados.append("Escritura Autenticada")
                if req_boleto: docs_presentados.append("Boleto C/V Certificado")
                if req_factibilidad: docs_presentados.append("Factibilidad Ambiental")
                if req_turismo: docs_presentados.append("Ley Turismo N° 6483")
                
                doc_str = ", ".join(docs_presentados) if docs_presentados else "Sin documentación adjunta"

                nueva_fila = pd.DataFrame([{
                    "N° EXPEDIENTE": nro_exp,
                    "TITULAR": titular,
                    "PROFESIONAL": profesional,
                    "CUENTA": cuenta,
                    "NOMENCLATURA CATASTRAL": nomenclatura_final,
                    "BARRIO": barrio,
                    "ASUNTO": asunto,
                    "AREA ACTUAL": area_destino_final,
                    "ESTADO": estado_inicial,
                    "VERIFICACION DEUDA": control_deuda_nota,
                    "DOCUMENTACION PRESENTADA": doc_str,
                    "OBSERVACIONES": observaciones,
                    "FECHA INGRESO": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "REGISTRADO POR": area_usuario
                }])

                try:
                    df_actualizado = pd.concat([df_expedientes, nueva_fila], ignore_index=True)
                    conn.update(worksheet="RELEVAMIENTO", data=df_actualizado)
                    st.cache_data.clear()
                    
                    st.success(f"🎉 **¡Expediente N° {nro_exp} registrado e ingresado al sistema!**")
                    st.info(msj_derivacion)
                    st.markdown(f"**Nomenclatura Registrada:** `{nomenclatura_final}`")
                    st.markdown(f"**Documentación Física Asentada:** `{doc_str}`")
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
        
