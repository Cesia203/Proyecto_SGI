import streamlit as st

# Importamos las funciones necesarias de los módulos.
from modulos.bienvenido import mostrar_bienvenido
from modulos.miembro import mostrar_miembro
from modulos.login import login
from modulos.reunion import mostrar_reunion
from modulos.ahorro import mostrar_ahorro
from modulos.Prestamo import mostrar_Prestamo
from modulos.Multa import mostrar_Multa
from modulos.Pago import mostrar_Pago
from modulos.Promotora import mostrar_Promotora
from modulos.Administrador import mostrar_Administrador
from modulos.reporte import mostrar_reporte
from modulos.caja import mostrar_caja
from modulos.acta import mostrar_acta
from modulos.ciclo import mostrar_ciclo
from modulos.asistencia import mostrar_asistencia   # ← NUEVO IMPORT

# Configuración básica
st.set_page_config(layout="centered", page_title="Gestión Cooperativa")

# CSS
st.markdown("""
<style>
div.stRadio > p {
    text-align: center;
    font-size: 1.5em;
    color: #0077b6;
    font-weight: 900;
    margin-bottom: 15px;
}
div.stRadio > label {
    padding: 10px 15px;
    margin: 5px;
    border-radius: 10px;
    border: 2px solid #ddd;
    background-color: white;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    font-weight: bold;
    cursor: pointer;
    flex-grow: 1;
    min-width: 150px;
    text-align: center;
}
div.stRadio > label[data-testid*="stDecoration"] {
    background-color: #e0f7ff;
    border-color: #0077b6;
    color: #0077b6;
}
div.stRadio input[type="radio"] { display: none; }
div.stRadio > div { flex-direction: row; flex-wrap: wrap; justify-content: center; }
</style>
""", unsafe_allow_html=True)


# =======================
# SESIÓN
# =======================
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:

    roles_principales = ["Directiva", "Administrador", "Promotor"]

    st.session_state["rol_principal"] = st.sidebar.selectbox(
        "Seleccionar rol principal:",
        roles_principales
    )

    # SUB-ROLES DE DIRECTIVA
    if st.session_state["rol_principal"] == "Directiva":
        st.session_state["rol_directiva"] = st.sidebar.selectbox(
            "Cargo dentro de Directiva:",
            ["Presidente", "Tesorera", "Secretaria"]
        )
        user_role = st.session_state["rol_directiva"]
    else:
        user_role = st.session_state["rol_principal"]

    # =============================
    # MENÚ SUPERIOR
    # =============================
    opciones = ["Inicio"]

    if st.session_state["rol_principal"] == "Directiva":
        opciones.append("Directiva")

    if st.session_state["rol_principal"] == "Administrador":
        opciones.append("Administrador")

    if st.session_state["rol_principal"] == "Promotor":
        opciones.append("Promotor")

    iconos = {
        "Inicio": "🏠",
        "Directiva": "📈",
        "Administrador": "⚙️",
        "Promotor": "👤"
    }

    opciones_display = [f"{iconos[o]} {o}" for o in opciones]

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        seleccion_display = st.radio(
            "OPCIONES",
            opciones_display,
            horizontal=True
        )
        seleccion = seleccion_display.split(" ", 1)[1]

    st.markdown("---")

    # =============================
    # CONTENIDOS
    # =============================
    if seleccion == "Inicio":
        st.title("🏠 Inicio del Sistema")
        st.markdown(f"Rol: **{user_role}**")
        mostrar_bienvenido()

    elif seleccion == "Promotor":
        st.title("👤 Panel del Promotor")
        mostrar_Promotora()

    elif seleccion == "Administrador":
        st.title("⚙️ Panel del Administrador")
        mostrar_Administrador()

    elif seleccion == "Directiva":
        st.title(f"📈 Directiva – Rol: {user_role}")

        # -------------------------------
        # OPCIONES DEPENDIENTES DEL CARGO
        # -------------------------------
        if user_role == "Presidente":
            sub_opciones = ["Reuniones", "Acta", "Ciclo", "Caja"]

        elif user_role == "Tesorera":
            sub_opciones = ["Caja", "Ahorros", "Ciclo", "Préstamos"]

        elif user_role == "Secretaria":
            sub_opciones = ["Multas", "Registrar miembro", "Asistencia"]  # ← AGREGADO

        tabs = st.tabs(sub_opciones)

        # PRESIDENTE
        if user_role == "Presidente":
            with tabs[0]: mostrar_reunion()
            with tabs[1]: mostrar_acta()
            with tabs[2]: mostrar_ciclo()
            with tabs[3]: mostrar_caja()

        # TESORERA
        if user_role == "Tesorera":
            with tabs[0]: mostrar_caja()
            with tabs[1]: mostrar_ahorro()
            with tabs[2]: mostrar_ciclo()
            with tabs[3]: mostrar_Prestamo()
            with tabs[4]: mostrar_Pago()

        # SECRETARIA
        if user_role == "Secretaria":
            with tabs[0]: mostrar_Multa()
            with tabs[1]: mostrar_miembro()
            with tabs[2]: mostrar_asistencia()   # ← NUEVA PESTAÑA

    # =============================
    # CERRAR SESIÓN
    # =============================
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar Sesión", type="primary"):
        st.session_state.clear()
        st.rerun()

else:
    login()
