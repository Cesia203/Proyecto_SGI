import streamlit as st
from modulos.bienvenido import mostrar_bienvenido # Importamos la función mostrar_bienvenido del módulo bienvenido

from modulos.login import login

# Comprobamos si la sesión ya está iniciada
# Esta línea verifica si la clave "sesion_iniciada" existe en el estado de la sesión
# Y también comprueba si su valor es True.
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    opciones = ["Ventas", "Otra opción"] # Agrega más opciones si las necesitas
    seleccion = st.sidebar.selectbox("Selecciona una opción", opciones)
    # Según la opción seleccionada, mostramos el contenido correspondiente
    if seleccion == "Ventas":
        pass # Bloque de código para Ventas (anteriormente vacío)

    elif seleccion == "Otra opción":
        st.write("Has seleccionado otra opción.") # Aquí podrías agregar el contenido de
        # otras opciones
        # Si la sesión está iniciada (el usuario ha iniciado sesión),
        # llamamos a la función que muestra el contenido principal o de ventas.
        mostrar_bienvenido()
else:
    # Si la sesión no está iniciada o el estado es False,
    # llamamos a la función que muestra el formulario de inicio de sesión (login).
    login()
