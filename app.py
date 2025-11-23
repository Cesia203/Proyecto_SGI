import streamlit as st
# Importamos las funciones necesarias de los módulos.
# Estos módulos deben residir en una carpeta 'modulos'
from modulos.bienvenido import mostrar_bienvenido
from modulos.miembro import mostrar_miembro
from modulos.login import login
from modulos.reunion import mostrar_reunion 
from modulos.ahorro import mostrar_ahorro
from modulos.prestamo import mostrar_prestamo
# Configuración básica de la página
st.set_page_config(layout="centered", page_title="Gestión Cooperativa")

# --- Bloque de Inyección CSS para Enmarcar y Estilizar las Opciones ---
# Este CSS hace que los botones de radio se vean como cajas separadas.
st.markdown("""
<style>
/* Centrar el texto del label/título del st.radio (la palabra "OPCIONES") */
div.stRadio > p {
    text-align: center;
    font-size: 1.5em; /* Tamaño de fuente más grande para el título */
    color: #0077b6; /* Color azul para destacar el título */
    font-weight: 900;
    margin-bottom: 15px;
}

/* Estilo para el contenedor general del radio button, asegurando el centrado */
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
    flex-grow: 1; /* Asegura que las cajas se distribuyan uniformemente */
    min-width: 150px; /* Asegura un tamaño mínimo para cada caja */
    text-align: center; /* Centrar el texto dentro de la etiqueta */
}

/* Estilo cuando una opción de radio está activa/seleccionada */
div.stRadio > label[data-testid*="stDecoration"] {
    background-color: #e0f7ff; /* Fondo para seleccionado */
    border-color: #0077b6; /* Borde para seleccionado */
    color: #0077b6; /* Color de texto/icono */
}

/* Ocultar el punto de radio nativo */
div.stRadio input[type="radio"] {
    display: none;
}

/* Forzar que las opciones se muestren en una fila (horizontal) y centradas */
div.stRadio > div {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)
# --------------------------------------------------------------------

# Comprobamos si la sesión ya está iniciada
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    
    # =========================================================================
    # LÓGICA DE ROLES PARA FILTRAR EL MENÚ
    # =========================================================================
    
    # --- TEMPORAL: Selector de Rol para Demostración (Mantener para probar la navegación) ---
    roles_db = ["Presidente", "Admin", "Promotora"]
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = "Presidente"

    st.session_state["user_role"] = st.sidebar.selectbox(
        "Simular Rol (DEMO):", 
        roles_db, 
        index=roles_db.index(st.session_state["user_role"]), 
        key="role_selector"
    )
    # --- FIN TEMPORAL ---

    # Obtenemos el rol actual.
    user_role = st.session_state.get("user_role", None)

    # 1. Definimos las opciones disponibles (todas)
    todas_las_opciones = {
        "Inicio": "🏠",
        "Directiva": "📈",
        "Promotora": "👤",
        "Administrador": "⚙️"
    }

    # 2. Mapeo de Roles de DB a Opciones de Menú
    opciones_disponibles_nombres = ["Inicio"] # 'Inicio' siempre está disponible

    if user_role == "Presidente":
        opciones_disponibles_nombres.append("Directiva")
        opciones_disponibles_nombres.append("Administrador") # Presidente tiene acceso a Administrador también
    elif user_role == "Admin":
        opciones_disponibles_nombres.append("Administrador")
    elif user_role == "Promotora":
        opciones_disponibles_nombres.append("Promotora")
        
    opciones = opciones_disponibles_nombres
    
    # 3. Preparamos SOLO las opciones disponibles con su icono para mostrar
    opciones_display = [f"{todas_las_opciones[op]} {op}" for op in opciones]

    # Determinamos qué opción debe estar seleccionada por defecto
    current_selection = st.session_state.get("last_selection", "Inicio")
    
    try:
        # Buscamos el índice de la opción real (sin icono)
        seleccion_actual_index = opciones.index(current_selection)
    except ValueError:
        # Si la opción anterior no es válida para el rol, volvemos a 'Inicio'
        seleccion_actual_index = 0 
        st.session_state["last_selection"] = opciones[0]
        
    # --- Código para centrar las opciones en un "marco" ---
    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        # Usamos st.radio con las opciones FILTRADAS
        seleccion_display = st.radio(
            "OPCIONES",
            opciones_display,
            index=seleccion_actual_index, 
            key="main_menu_selection",
            horizontal=True
        )
        
        # Obtenemos la selección real (sin el icono) para la lógica condicional
        # Usamos rsplit para evitar problemas si el nombre tiene espacios
        seleccion = seleccion_display.rsplit(' ', 1)[-1] 
        
        # Guardamos la selección actual
        st.session_state["last_selection"] = seleccion
        
    # --- Fin del código para centrar y enmarcar ---

    # Mostramos el contenido de la sección seleccionada.
    st.markdown("---") # Separador visual

    if seleccion == "Directiva":
        st.title(f"{todas_las_opciones['Directiva']} Sección Directiva")
        st.markdown(f"<p class='text-lg'>Rol de acceso: <b>{user_role}</b></p>", unsafe_allow_html=True)
        
        # --- NUEVO MENÚ DE SUB-OPCIONES PARA DIRECTIVA ---
        sub_opciones_directiva = [
            "Registrar miembro",
            "Asistencia a reuniones",
            "Ahorros",
            "Préstamos",
            "Multas",
            "Pagos"
        ]
        
        # Usamos pestañas para organizar mejor los sub-módulos (más moderno y limpio)
        tabs = st.tabs(sub_opciones_directiva)

        if tabs[0]: # Registrar miembro
            with tabs[0]:
                st.subheader("Registro de Nuevos Miembros")
                st.info("Formulario para ingresar datos de un nuevo miembro.")
                mostrar_miembro() 
        
        if tabs[1]: # Asistencia a reuniones
            with tabs[1]:
                st.subheader("Control de Asistencia")
                st.info("Módulo para registrar la asistencia a las reuniones.")
                mostrar_reunion()
        
        if tabs[2]: # Ahorros
            with tabs[2]:
                st.subheader("Gestión de Ahorros")
                st.info("Visualización y gestión de las cuentas de ahorro de los miembros.")
                st.warning("Implementación pendiente: Lógica de bases de datos para ahorros.")
                mostrar_ahorro()
        if tabs[3]: # Préstamos
            with tabs[3]:
                st.subheader("Administración de Préstamos")
                st.info("Panel de control para solicitudes, desembolsos y seguimiento de pagos de préstamos.")
                st.warning("Implementación pendiente: Lógica de bases de datos para préstamos.")
                mostrar_prestamo()
        if tabs[4]: # Multas
            with tabs[4]:
                st.subheader("Registro y Seguimiento de Multas")
                st.info("Módulo para imponer, registrar y hacer seguimiento a las multas aplicadas.")
                st.warning("Implementación pendiente: Lógica de bases de datos para multas.")

        if tabs[5]: # Pagos
            with tabs[5]:
                st.subheader("Historial y Transacciones de Pagos")
                st.info("Registro de todos los pagos realizados por los miembros.")
                st.warning("Implementación pendiente: Lógica de bases de datos para pagos.")
        
    elif seleccion == "Inicio":
        st.title(f"{todas_las_opciones['Inicio']} Inicio del Sistema")
        st.markdown(f"<p class='text-lg'>Rol de acceso: <b>{user_role}</b></p>", unsafe_allow_html=True)
        mostrar_bienvenido() 
        
    elif seleccion == "Promotora":
        st.title(f"{todas_las_opciones['Promotora']} Sección Promotora")
        st.markdown(f"<p class='text-lg'>Rol de acceso: <b>{user_role}</b></p>", unsafe_allow_html=True)
        st.info("Aquí irían las herramientas para la gestión de clientes, seguimiento de prospectos y campañas de la promotora.")
        
    elif seleccion == "Administrador":
        st.title(f"{todas_las_opciones['Administrador']} Sección Administrador")
        st.markdown(f"<p class='text-lg'>Rol de acceso: <b>{user_role}</b></p>", unsafe_allow_html=True)
        
        st.warning("Página de gestión de usuarios y ajustes del sistema. Solo para personal autorizado.")
        
        # Sub-menú para el Administrador
        admin_opciones = ["Gestión de Usuarios", "Ajustes del Sistema", "Logs de Auditoría"]
        admin_tab = st.tabs(admin_opciones)

        with admin_tab[0]:
            st.subheader("Control de Usuarios y Roles")
            st.write("Herramientas para crear, editar y asignar roles a los usuarios.")
            st.error("Implementación pendiente: CRUD de usuarios.")
        
        with admin_tab[1]:
            st.subheader("Configuración Global")
            st.write("Ajustes de cuotas, tasas de interés por defecto y períodos de reunión.")
            
        with admin_tab[2]:
            st.subheader("Historial de Operaciones")
            st.write("Registro detallado de todas las acciones realizadas por los usuarios en el sistema.")
            
    # Botón de cierre de sesión en la barra lateral
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar Sesión", type="primary"):
        st.session_state["sesion_iniciada"] = False
        # Limpiamos el rol y la selección anterior
        if "user_role" in st.session_state:
            del st.session_state["user_role"]
        if "last_selection" in st.session_state:
            del st.session_state["last_selection"]
        st.rerun()

else:
    # Si la sesión no está iniciada, mostramos el formulario de inicio de sesión
    login()
