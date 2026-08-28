import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Gestión de Expedientes - Los Reartes",
    page_icon="📂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado sencillo
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #1E293B;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .card {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        margin-bottom: 15px;
    }
    .badge-area {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DE DATOS (MOCK / SESSION STATE)
# ==========================================
# Áreas habilitadas en la Comuna
AREAS = [
    "Obras Privadas",
    "Comercio e Industria",
    "Inspección General",
    "Recursos Hídricos / Ambiente",
    "Rentas y Catastro",
    "Mesa de Entrada / Archivo"
]

ESTADOS = ["En Trámite", "Aprobado", "Con Observaciones", "Archivado"]

if "expedientes" not in st.session_state:
    st.session_state.expedientes = pd.DataFrame([
        {
            "id_expediente": "EXP-2026-001",
            "titular": "Juan Pérez",
            "cuenta_catastral": "12-345-001",
            "tipo_tramite": "Visación de Plano de Obra",
            "area_actual": "Obras Privadas",
            "estado": "En Trámite",
            "fecha_ingreso": "2026-08-10 09:30"
        },
        {
            "id_expediente": "EXP-2026-002",
            "titular": "Comercio Las Sierras SRL",
            "cuenta_catastral": "12-345-089",
            "tipo_tramite": "Habilitación Comercial",
            "area_actual": "Comercio e Industria",
            "estado": "En Trámite",
            "fecha_ingreso": "2026-08-15 11:15"
        },
        {
            "id_expediente": "EXP-2026-003",
            "titular": "María González",
            "cuenta_catastral": "12-345-120",
            "tipo_tramite": "Certificado de Factibilidad Hídrica",
            "area_actual": "Recursos Hídricos / Ambiente",
            "estado": "Con Observaciones",
            "fecha_ingreso": "2026-08-20 14:00"
        }
    ])

if "historial_pases" not in st.session_state:
    st.session_state.historial_pases = pd.DataFrame([
        {
            "id_expediente": "EXP-2026-001",
            "fecha_hora": "2026-08-10 09:30",
            "area_origen": "Mesa de Entrada / Archivo",
            "area_destino": "Obras Privadas",
            "usuario": "m_entrada",
            "observaciones": "Ingreso de expediente con plano impreso."
        },
        {
            "id_expediente": "EXP-2026-002",
            "fecha_hora": "2026-08-15 11:15",
            "area_origen": "Mesa de Entrada / Archivo",
            "area_destino": "Comercio e Industria",
            "usuario": "m_entrada",
            "observaciones": "Solicitud de habilitación inicial."
        },
        {
            "id_expediente": "EXP-2026-003",
            "fecha_hora": "2026-08-20 14:00",
            "area_origen": "Obras Privadas",
            "area_destino": "Recursos Hídricos / Ambiente",
            "usuario": "arq_obras",
            "observaciones": "Se deriva para revisión de línea de ribera."
        }
    ])

# ==========================================
# BARRA LATERAL - SELECCIÓN DE ÁREA / USUARIO
# ==========================================
st.sidebar.image("https://img.icons8.com/color/96/folder-invoices.png", width=70)
st.sidebar.title("Comuna de Los Reartes")
st.sidebar.subheader("Sistema de Expedientes")

area_usuario = st.sidebar.selectbox("🏛️ Seleccione su Área / Oficina:", AREAS)
st.sidebar.markdown(f"**Área Activa:** `{area_usuario}`")
st.sidebar.divider()

menu = st.sidebar.radio(
    "Navegación",
    [
        "📥 Bandeja del Área",
        "➕ Nuevo Expediente",
        "🔄 Derivar / Pasar Expediente",
        "🔍 Buscar y Trazabilidad",
        "📊 Vistazo General"
    ]
)

# ==========================================
# 1. BANDEJA DEL ÁREA
# ==========================================
if menu == "📥 Bandeja del Área":
    st.markdown(f"<div class='main-header'>📥 Bandeja de Entrada: {area_usuario}</div>", unsafe_allow_html=True)
    
    # Filtrar expedientes en el área actual
    df_exp = st.session_state.expedientes
    mis_expedientes = df_exp[df_exp["area_actual"] == area_usuario]
    
    col1, col2 = st.columns([3, 1])
    col1.metric("Expedientes Físicamente en Oficina", len(mis_expedientes))
    
    if mis_expedientes.empty:
        st.info("No hay expedientes pendientes en esta área actualmente.")
    else:
        st.dataframe(
            mis_expedientes[["id_expediente", "titular", "cuenta_catastral", "tipo_tramite", "estado", "fecha_ingreso"]],
            use_container_width=True,
            hide_index=True
        )
        
        st.subheader("Detalle del Trámite")
        exp_seleccionado = st.selectbox("Seleccione un expediente para revisar:", mis_expedientes["id_expediente"].tolist())
        
        datos_exp = mis_expedientes[mis_expedientes["id_expediente"] == exp_seleccionado].iloc[0]
        
        with st.container():
            st.markdown(f"""
            <div class='card'>
                <h4>Expediente: {datos_exp['id_expediente']}</h4>
                <p><b>Titular:</b> {datos_exp['titular']} | <b>N° Cuenta/Catastro:</b> {datos_exp['cuenta_catastral']}</p>
                <p><b>Trámite:</b> {datos_exp['tipo_tramite']}</p>
                <p><b>Estado Actual:</b> {datos_exp['estado']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 2. NUEVO EXPEDIENTE
# ==========================================
elif menu == "➕ Nuevo Expediente":
    st.markdown("<div class='main-header'>➕ Registrar Nuevo Expediente</div>", unsafe_allow_html=True)
    
    with st.form("form_nuevo_expediente"):
        col1, col2 = st.columns(2)
        
        nuevo_id = f"EXP-2026-{len(st.session_state.expedientes) + 1:03d}"
        col1.text_input("Número de Expediente (Autogenerado)", value=nuevo_id, disabled=True)
        titular = col1.text_input("Titular / Contribuyente *")
        cuenta = col2.text_input("N° de Cuenta / Padrón Catastral *")
        
        tipo_tramite = col1.selectbox("Tipo de Trámite", [
            "Visación de Plano de Obra",
            "Habilitación Comercial",
            "Factibilidad Ambiental / Hídrica",
            "Inspección Final de Obra",
            "Solicitud General / Reclamo"
        ])
        
        area_inicial = col2.selectbox("Área Destino Inicial", AREAS, index=AREAS.index(area_usuario))
        observacion_inicial = st.text_area("Observaciones o Nota de Ingreso")
        
        submitted = st.form_submit_button("💾 Guardar y Crear Expediente")
        
        if submitted:
            if not titular or not cuenta:
                st.error("Por favor complete los campos obligatorios (*).")
            else:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # Crear registro principal
                nuevo_registro = {
                    "id_expediente": nuevo_id,
                    "titular": titular,
                    "cuenta_catastral": cuenta,
                    "tipo_tramite": tipo_tramite,
                    "area_actual": area_inicial,
                    "estado": "En Trámite",
                    "fecha_ingreso": fecha_actual
                }
                
                # Crear primer pase de historial
                primer_pase = {
                    "id_expediente": nuevo_id,
                    "fecha_hora": fecha_actual,
                    "area_origen": "Mesa de Entrada / Archivo",
                    "area_destino": area_inicial,
                    "usuario": f"resp_{area_usuario.lower().replace(' ', '_')}",
                    "observaciones": observacion_inicial or "Ingreso e inicio de expediente."
                }
                
                st.session_state.expedientes = pd.concat([st.session_state.expedientes, pd.DataFrame([nuevo_registro])], ignore_index=True)
                st.session_state.historial_pases = pd.concat([st.session_state.historial_pases, pd.DataFrame([primer_pase])], ignore_index=True)
                
                st.success(f"¡Expediente {nuevo_id} generado e ingresado a {area_inicial} correctamente!")

# ==========================================
# 3. DERIVAR / PASAR EXPEDIENTE
# ==========================================
elif menu == "🔄 Derivar / Pasar Expediente":
    st.markdown("<div class='main-header'>🔄 Derivación de Expediente a otra Área</div>", unsafe_allow_html=True)
    
    df_exp = st.session_state.expedientes
    mis_expedientes = df_exp[df_exp["area_actual"] == area_usuario]
    
    if mis_expedientes.empty:
        st.warning(f"No hay expedientes en el área '{area_usuario}' para transferir.")
    else:
        exp_a_pasar = st.selectbox("Seleccione el Expediente a Derivar:", mis_expedientes["id_expediente"].tolist())
        datos_exp = mis_expedientes[mis_expedientes["id_expediente"] == exp_a_pasar].iloc[0]
        
        st.info(f"Derivando: **{datos_exp['id_expediente']}** - {datos_exp['titular']} ({datos_exp['tipo_tramite']})")
        
        with st.form("form_pase"):
            destinos_posibles = [a for a in AREAS if a != area_usuario]
            area_destino = st.selectbox("Área Destino:", destinos_posibles)
            nuevo_estado = st.selectbox("Actualizar Estado del Trámite:", ESTADOS, index=ESTADOS.index(datos_exp['estado']))
            observaciones_pase = st.text_area("Observaciones del Pase / Dictamen Técnico *", help="Detalle el motivo del pase o requisitos pendientes.")
            
            btn_pase = st.form_submit_button("🚀 Confirmar Pase de Expediente")
            
            if btn_pase:
                if not observaciones_pase:
                    st.error("Es obligatorio incluir una observación o dictamen del pase.")
                else:
                    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    # Actualizar ubicación y estado en la tabla general
                    idx = st.session_state.expedientes[st.session_state.expedientes["id_expediente"] == exp_a_pasar].index[0]
                    st.session_state.expedientes.at[idx, "area_actual"] = area_destino
                    st.session_state.expedientes.at[idx, "estado"] = nuevo_estado
                    
                    # Agregar registro al historial de pases
                    nuevo_pase = {
                        "id_expediente": exp_a_pasar,
                        "fecha_hora": fecha_actual,
                        "area_origen": area_usuario,
                        "area_destino": area_destino,
                        "usuario": f"resp_{area_usuario.lower().replace(' ', '_')}",
                        "observaciones": observaciones_pase
                    }
                    st.session_state.historial_pases = pd.concat([st.session_state.historial_pases, pd.DataFrame([nuevo_pase])], ignore_index=True)
                    
                    st.success(f"Expediente {exp_a_pasar} derivado con éxito hacia {area_destino}.")

# ==========================================
# 4. BUSCAR Y TRAZABILIDAD
# ==========================================
elif menu == "🔍 Buscar y Trazabilidad":
    st.markdown("<div class='main-header'>🔍 Búsqueda y Trazabilidad Cronológica</div>", unsafe_allow_html=True)
    
    busqueda = st.text_input("Ingrese N° de Expediente, Titular o Cuenta Catastral:")
    
    df_exp = st.session_state.expedientes
    if busqueda:
        resultado = df_exp[
            df_exp["id_expediente"].str.contains(busqueda, case=False) |
            df_exp["titular"].str.contains(busqueda, case=False) |
            df_exp["cuenta_catastral"].str.contains(busqueda, case=False)
        ]
    else:
        resultado = df_exp
        
    st.dataframe(resultado, use_container_width=True, hide_index=True)
    
    if not resultado.empty:
        st.divider()
        st.subheader("📜 Timeline / Historial de Pases")
        exp_id_timeline = st.selectbox("Seleccione Expediente para ver Trazabilidad Completa:", resultado["id_expediente"].tolist())
        
        pases_exp = st.session_state.historial_pases[st.session_state.historial_pases["id_expediente"] == exp_id_timeline]
        
        for i, (_, row) in enumerate(pases_exp.iterrows(), start=1):
            st.markdown(f"""
            <div class='card'>
                <b>Pase #{i}</b> - <i>{row['fecha_hora']}</i><br>
                <b>Origen:</b> {row['area_origen']} ➔ <b>Destino:</b> <span class='badge-area'>{row['area_destino']}</span><br>
                <b>Usuario:</b> {row['usuario']}<br>
                <b>Observaciones:</b> {row['observaciones']}
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# 5. VISTAZO GENERAL / TABLERO
# ==========================================
elif menu == "📊 Vistazo General":
    st.markdown("<div class='main-header'>📊 Estado General de Expedientes Comunales</div>", unsafe_allow_html=True)
    
    df_exp = st.session_state.expedientes
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Expedientes", len(df_exp))
    c2.metric("En Trámite", len(df_exp[df_exp["estado"] == "En Trámite"]))
    c3.metric("Con Observaciones", len(df_exp[df_exp["estado"] == "Con Observaciones"]))
    
    st.divider()
    st.subheader("Distribución por Área Actual")
    conteo_areas = df_exp["area_actual"].value_counts()
    st.bar_chart(conteo_areas)