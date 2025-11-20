import streamlit as st
from modulos.bienvenido import mostrar_bienvenido # Importamos la función mostrar_bienvenido del módulo bienvenido

from modulos.login import login

# Configuración básica de la página (opcional, pero útil para centrar)
st.set_page_config(layout="centered")

# Comprobamos si la sesión ya está iniciada
# Esta línea verifica si la clave "sesion_iniciada" existe en el estado de la sesión
# Y también comprueba si su valor es True.
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    opciones = ["Inicio", "Directiva", "Promotora", "Administrador"] # Agrega más opciones si las necesitas

    # --- Código para centrar las opciones en un "marco" ---
    # Creamos columnas: una estrecha a la izquierda, una ancha en el centro (para el menú), y otra estrecha a la derecha.
    col1, col2, col3 = st.columns([1, 4, 1]) # Aumentamos el ancho de la columna central (4)

    with col2:
        # Usamos st.container para simular el "marco" alrededor de las opciones.
        # Streamlit aplica un ligero padding y margen, creando el efecto visual de un recuadro.
        with st.container(border=True): # Usamos border=True para un marco visible
            # Usamos st.radio con horizontal=True para que se vean como botones en una fila
            seleccion = st.radio(
                "Navegación del Sistema:",
                opciones,
                key="main_menu_selection",
                horizontal=True
            )
    # --- Fin del código para centrar y enmarcar ---

    # Mostramos el contenido de la sección seleccionada fuera de las columnas para que ocupe todo el ancho.
    st.markdown("---") # Separador visual

    if seleccion == "Directiva":
        st.header("Sección Directiva")
        st.write("Panel de control y herramientas para la Directiva.")
        pass # Bloque de código para Directiva

    elif seleccion == "Inicio":
        st.header("Inicio del Sistema")
        st.write("Has seleccionado la página de inicio.")
        # Llamamos a la función que muestra el contenido principal.
        mostrar_bienvenido()
        
    elif seleccion == "Promotora":
        st.header("Sección Promotora")
        st.write("Contenido específico y herramientas para el rol de Promotora.")
        pass

    elif seleccion == "Administrador":
        st.header("Sección Administrador")
        st.write("Contenido de gestión y configuración para el Administrador.")
        pass
else:
    # Si la sesión no está iniciada o el estado es False,
    # llamamos a la función que muestra el formulario de inicio de sesión (login).
    login()
