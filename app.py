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
from modulos.Administrador import mostrar_Administrador   # 🔥 NUEVO

# Configuración básica de la página
st.set_page_config(layout="centered", page_title="Gestión Cooperativa")

# --- CSS para estilo de botones ---
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
div.stRadio input[type="radio"] {
    display: none;
}
div.stRadio > div {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# =============================
#  VALIDACIÓN DE SESIÓN
# =============================
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:

    # =============================
    # SIMULACIÓN DE ROLES (DEMO)
    # =============================
    roles_db = ["Presidente", "Admin", "Promotora"]
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = "Presidente"

    st.session_state["user_role"] = st.sidebar.selectbox(
        "Simular Rol (DEMO):",
        roles_db,
        index=roles_db.index(st.session_state["user_role"]),
        key="role_selector"
    )

    # =============================
    # MENÚ PRINCIPAL POR ROL
    # =============================
    user_role = st.session_state["user_role"]

    todas_las_opciones = {
        "Inicio": "🏠",
        "Directiva": "📈",
        "Promotora": "👤",
        "Administrador": "⚙️"
    }

    # Opciones por rol
    opciones = ["Inicio"]
    if user_role == "Presidente":
        opciones += ["Directiva", "Administrador"]
    elif user_role == "Admin":
        opciones += ["Administrador"]
    elif user_role == "Promotora":
        opciones += ["Promotora"]

    # Convertimos a formato con iconos
    opciones_display = [f"{todas_las_opciones[o]} {o}" for o in opciones]

    # Mantener selección previa
    seleccion_actual = st.session_state.get("last_selection", "Inicio")

    try:
        index_default = opciones.index(seleccion_actual)
    except:
        index_default = 0
        st.session_state["last_selection"] = "Inicio"

    # =============================
    # RADIO — Menú superior centrado
    # =============================
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        seleccion_display = st.radio(
            "OPCIONES",
            opciones_display,
            index=index_default,
            key="main_menu_selection",
            horizontal=True
        )

        seleccion = seleccion_display.rsplit(" ", 1)[-1]
        st.session_state["last_selection"] = seleccion

    st.markdown("---")

    # =============================
    #  ACCIONES POR SECCIÓN
    # =============================
    if seleccion == "Inicio":
        st.title("🏠 Inicio del Sistema")
        st.markdown(f"Rol: **{user_role}**")
        mostrar_bienvenido()

    elif seleccion == "Promotora":
        st.title("👤 Sección Promotora")
        st.markdown(f"Rol: **{user_role}**")
        mostrar_Promotora()

    elif seleccion == "Administrador":
        st.title("⚙️ Panel del Administrador")
        st.markdown(f"Rol: **{user_role}**")
        mostrar_Administrador()   # 🔥 AQUI SE ACTIVA EL MÓDULO REAL

    elif seleccion == "Directiva":
        st.title("📈 Sección Directiva")
        st.markdown(f"Rol: **{user_role}**")

        sub_opciones = [
            "Registrar miembro",
            "Asistencia a reuniones",
            "Ahorros",
            "Préstamos",
            "Multas",
            "Pagos"
        ]

        tabs = st.tabs(sub_opciones)

        with tabs[0]:
            mostrar_miembro()

        with tabs[1]:
            mostrar_reunion()

        with tabs[2]:
            mostrar_ahorro()

        with tabs[3]:
            mostrar_Prestamo()

        with tabs[4]:
            mostrar_Multa()

        with tabs[5]:
            mostrar_Pago()

    # =============================
    # Cerrar sesión
    # =============================
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar Sesión", type="primary"):
        st.session_state.clear()
        st.rerun()

else:
    login()
