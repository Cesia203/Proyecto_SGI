import streamlit as st
from modulos.bienvenido import mostrar_bienvenido # Importamos la función mostrar_bienvenido del módulo bienvenido
from modulos.miembro import mostrar_miembro # Importamos la función mostrar_miembro del módulo miembro (Nueva)
from modulos.login import login

# Configuración básica de la página (opcional, pero útil para centrar)
st.set_page_config(layout="centered")

# --- Bloque de Inyección CSS para Enmarcar y Estilizar las Opciones ---
# Este código inyecta CSS para que los botones de radio se vean como cajas separadas
# y resalta la opción seleccionada.
st.markdown("""
<style>
/* Centrar el texto del label/título del st.radio (la palabra "OPCIONES") */
div.stRadio > p {
    text-align: center;
    font-size: 1.5em; /* Tamaño de fuente más grande para el título */
    color: #0077b6; /* Color azul para destacar el título */
    font-weight: 900; /* AHORA EN NEGRITA MÁS GRUESA */
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
}

/* Estilo cuando una opción de radio está activa/seleccionada */
div.stRadio > label[data-testid*="stDecoration"] {
    background-color: #e0f7ff; /* Fondo para seleccionado */
    border-color: #0077b6; /* Borde para seleccionado */
    color: #0077b6; /* Color de texto/icono */
}

/* Ocultar el punto de radio nativo, dejando solo el texto y el icono en el marco */
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
    # LÓGICA DE ROLES PARA FILTRAR EL MENÚ (Restaurada)
    # =========================================================================
    
    # --- TEMPORAL: Selector de Rol para Demostración (ELIMINAR EN PRODUCCIÓN) ---
    # Usamos los roles exactos de tu base de datos (Presidente, Admin, Promotora)
    roles_db = ["Presidente", "Admin", "Promotora"]
    # Simulamos que el rol del usuario se obtiene de la sesión
    st.session_state["user_role"] = st.sidebar.selectbox("Simular Rol (DEMO):", roles_db, index=roles_db.index(st.session_state.get("user_role", "Presidente")), key="role_selector")
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

    # Determinamos qué opción debe estar seleccionada por defecto (generalmente la primera)
    # Mantenemos la selección actual si es válida, o volvemos a 'Inicio'.
    current_selection = st.session_state.get("last_selection", "Inicio")
    
    # Obtenemos el índice de la selección actual dentro de las opciones disponibles
    try:
        # Intentamos encontrar la opción actual (sin icono) en las opciones disponibles
        seleccion_actual_index = opciones.index(current_selection)
    except ValueError:
        # Si la opción anterior no está en las opciones disponibles del nuevo rol, volvemos a 0 (Inicio)
        seleccion_actual_index = 0 
        st.session_state["last_selection"] = opciones[0]
        

    # --- Código para centrar las opciones en un "marco" ---
    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        # Usamos st.radio con las opciones FILTRADAS
        seleccion_display = st.radio(
            "OPCIONES",
            opciones_display,
            index=seleccion_actual_index, # Usamos el índice de la selección anterior o 0
            key="main_menu_selection",
            horizontal=True
        )
        
        # Obtenemos la selección real (sin el icono) para la lógica condicional
        seleccion = seleccion_display.split()[-1]
        
        # Guardamos la selección actual para mantenerla al recargar (cambio de rol)
        st.session_state["last_selection"] = seleccion
        
    # --- Fin del código para centrar y enmarcar ---

    # Mostramos el contenido de la sección seleccionada fuera de las columnas.
    st.markdown("---") # Separador visual

    if seleccion == "Directiva":
        st.header(f"{todas_las_opciones['Directiva']} Sección Directiva")
        st.write("Panel de control y herramientas para la Directiva.")
        st.write(f"Rol actual: **{user_role}**")
        
        # --- NUEVO MENÚ DE SUB-OPCIONES PARA DIRECTIVA ---
        sub_opciones_directiva = [
            "Registrar miembro",
            "Asistencia a reuniones",
            "Ahorros",
            "Préstamos",
            "Multas",
            "Pagos"
        ]
        
        # Usamos un selectbox para el sub-menú y lo centramos visualmente
        sub_col1, sub_col2, sub_col3 = st.columns([1, 3, 1])
        with sub_col2:
            sub_seleccion = st.selectbox(
                "Módulos de Gestión",
                sub_opciones_directiva,
                key="directiva_sub_menu"
            )

        st.markdown("---") # Separador visual para el contenido del sub-módulo
        
        # Lógica para mostrar contenido basado en la sub-selección
        if sub_seleccion == "Registrar miembro":
            st.subheader("Registro de Nuevos Miembros")
            st.info("Formulario para ingresar datos de un nuevo miembro de la cooperativa/asociación.")
            
            mostrar_miembro() # Descomentar si se quiere usar el dashboard original en alguna sub-página# Aquí podríamos llamar a una función como `modulos.miembro.mostrar_formulario_registro()`
        elif sub_seleccion == "Asistencia a reuniones":
            st.subheader("Control de Asistencia")
            st.info("Módulo para registrar la asistencia de los miembros a las reuniones de la directiva/asamblea.")
        elif sub_seleccion == "Ahorros":
            st.subheader("Gestión de Ahorros")
            st.info("Visualización y gestión de las cuentas de ahorro de los miembros.")
        elif sub_seleccion == "Préstamos":
            st.subheader("Administración de Préstamos")
            st.info("Panel de control para solicitudes, desembolsos y seguimiento de pagos de préstamos.")
        elif sub_seleccion == "Multas":
            st.subheader("Registro y Seguimiento de Multas")
            st.info("Módulo para imponer, registrar y hacer seguimiento a las multas aplicadas.")
        elif sub_seleccion == "Pagos":
            st.subheader("Historial y Transacciones de Pagos")
            st.info("Registro de todos los pagos realizados por los miembros (cuotas, multas, préstamos, etc.).")
            
        # El contenido de mostrar_miembro() se puede integrar aquí si es necesario, 
        # pero por ahora lo dejo comentado o lo descarto ya que el usuario pidió nuevas opciones.
        

    elif seleccion == "Inicio":
        st.header(f"{todas_las_opciones['Inicio']} Inicio del Sistema")
        st.write("Has seleccionado la página de inicio.")
        st.write(f"Rol actual: **{user_role}**")
        # LLAMADA CORREGIDA: Usamos la función importada 'mostrar_bienvenido'
        mostrar_bienvenido() 
        
    elif seleccion == "Promotora":
        st.header(f"{todas_las_opciones['Promotora']} Sección Promotora")
        st.write("Contenido específico y herramientas para el rol de Promotora.")
        st.write(f"Rol actual: **{user_role}**")
        st.info("Aquí irían las herramientas para la gestión de clientes y campañas de la promotora.")
        
    elif seleccion == "Administrador":
        st.header(f"{todas_las_opciones['Administrador']} Sección Administrador")
        st.write("Contenido de gestión y configuración para el Administrador.")
        st.write(f"Rol actual: **{user_role}**")
        st.warning("Página de gestión de usuarios y ajustes del sistema.")
        
    # Botón de cierre de sesión en la barra lateral
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["sesion_iniciada"] = False
        # Limpiamos el rol y la selección anterior
        if "user_role" in st.session_state:
            del st.session_state["user_role"]
        if "last_selection" in st.session_state:
            del st.session_state["last_selection"]
        st.rerun()

else:
    # Si la sesión no está iniciada o el estado es False,
    # llamamos a la función que muestra el formulario de inicio de sesión (login).
    login()
