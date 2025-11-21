mport streamlit as st
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
    st.session_state["user_role"] = st.sidebar.selectbox("Simular Rol (DEMO):", roles_db, key="role_selector")
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
    elif user_role == "Admin":
        opciones_disponibles_nombres.append("Administrador")
    elif user_role == "Promotora":
        opciones_disponibles_nombres.append("Promotora")
        
    opciones = opciones_disponibles_nombres
    
    # 3. Preparamos SOLO las opciones disponibles con su icono para mostrar
    opciones_display = [f"{todas_las_opciones[op]} {op}" for op in opciones]

    # Determinamos qué opción debe estar seleccionada por defecto (generalmente la primera)
    default_selection_display = opciones_display[0] if opciones_display else "Inicio"


    # --- Código para centrar las opciones en un "marco" ---
    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        # Usamos st.radio con las opciones FILTRADAS
        seleccion_display = st.radio(
            "OPCIONES",
            opciones_display,
            # Establecemos el índice por defecto para prevenir errores de indexación al filtrar
            index=opciones_display.index(default_selection_display) if default_selection_display in opciones_display else 0,
            key="main_menu_selection",
            horizontal=True
        )
        
        # Obtenemos la selección real (sin el icono) para la lógica condicional
        seleccion = seleccion_display.split()[-1] 
    # --- Fin del código para centrar y enmarcar ---

    # Mostramos el contenido de la sección seleccionada fuera de las columnas.
    st.markdown("---") # Separador visual

    if seleccion == "Directiva":
        st.header(f"{todas_las_opciones['Directiva']} Sección Directiva")
        st.write("Panel de control y herramientas para la Directiva.")
        st.write(f"Rol actual: **{user_role}**")
        # Llamada a la nueva función
        mostrar_miembro() 

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
        pass

    elif seleccion == "Administrador":
        st.header(f"{todas_las_opciones['Administrador']} Sección Administrador")
        st.write("Contenido de gestión y configuración para el Administrador.")
        st.write(f"Rol actual: **{user_role}**")
        pass
else:
    # Si la sesión no está iniciada o el estado es False,
    # llamamos a la función que muestra el formulario de inicio de sesión (login).
    login()
