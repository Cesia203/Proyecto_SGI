import streamlit as st
from modulos.bienvenido import mostrar_bienvenido # Importamos la función mostrar_bienvenido del módulo bienvenido

from modulos.login import login

# Comprobamos si la sesión ya está iniciada
# Esta línea verifica si la clave "sesion_iniciada" existe en el estado de la sesión
# Y también comprueba si su valor es True.
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    opciones = ["Inicio", "Directiva","Promotora","Administrador"] # Agrega más opciones si las necesitas

    # --- Nuevo código para centrar las opciones ---
    # Creamos columnas: una estrecha a la izquierda, una ancha en el centro y otra estrecha a la derecha.
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Usamos st.radio para que las opciones aparezcan en el centro de la columna 2.
        seleccion = st.radio("Selecciona una opción:", opciones, key="main_menu_selection")
    # --- Fin del código para centrar ---

    # Según la opción seleccionada, mostramos el contenido correspondiente
    if seleccion == "Directiva":
        st.header("Sección de Ventas (Contenido Principal)")
        st.write("Aquí se mostrarán los datos y herramientas relacionados con las ventas.")
        pass # Bloque de código para Ventas (anteriormente vacío)

    elif seleccion == "Inico":
        st.header("Otra Opción Seleccionada")
        st.write("Has seleccionado otra opción.")
        # Aquí podrías agregar el contenido de otras opciones

        # Si la sesión está iniciada (el usuario ha iniciado sesión),
        # llamamos a la función que muestra el contenido principal o de ventas.
        mostrar_bienvenido()
    elif seleccion == "Promotora":
    elif seleccion == "Administrador":
else:
    # Si la sesión no está iniciada o el estado es False,
    # llamamos a la función que muestra el formulario de inicio de sesión (login).
    login()
