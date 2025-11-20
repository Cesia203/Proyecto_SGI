import streamlit as st
from modulos.bienvenido import mostrar_bienvenido # Importamos la función mostrar_bienvenido del módulo bienvenido

from modulos.login import login

# Comprobamos si la sesión ya está iniciada
# Esta línea verifica si la clave "sesion_iniciada" existe en el estado de la sesión
# Y también comprueba si su valor es True.
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    opciones = ["Inicio", "Directiva", "Promotora", "Administrador"] # Agrega más opciones si las necesitas

    # --- Nuevo código para centrar las opciones ---
    # Creamos columnas: una estrecha a la izquierda, una ancha en el centro y otra estrecha a la derecha.
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Usamos st.radio para que las opciones aparezcan en el centro de la columna 2.
        seleccion = st.radio("Selecciona una opción:", opciones, key="main_menu_selection")
    # --- Fin del código para centrar ---

    # Según la opción seleccionada, mostramos el contenido correspondiente
    if seleccion == "Directiva":
        st.header("Sección Directiva")
        st.write("Panel de control y herramientas para la Directiva.")
        pass # Bloque de código para Directiva

    elif seleccion == "Inicio": # Corregido de "Inico" a "Inicio"
        st.header("Inicio del Sistema")
        st.write("Has seleccionado la página de inicio.")
        # Si la sesión está iniciada (el usuario ha iniciado sesión),
        # llamamos a la función que muestra el contenido principal o de ventas.
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
