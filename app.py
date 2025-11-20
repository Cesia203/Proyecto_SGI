import streamlit as st
from modulos.bienvenido import mostrar_bienvenido # Importamos la función mostrar_bienvenido del módulo bienvenido

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
    
    opciones = ["Inicio", "Directiva", "Promotora", "Administrador"]
    iconos = {
        "Inicio": "🏠",       # Casa
        "Directiva": "📈",    # Gráfico de barras
        "Promotora": "👤",    # Usuario/Persona
        "Administrador": "⚙️" # Engranaje
    }
    
    # Preparamos las opciones para mostrar con el icono al lado
    opciones_display = [f"{iconos[op]} {op}" for op in opciones]

    # --- Código para centrar las opciones en un "marco" ---
    # Creamos columnas: una estrecha a la izquierda, una ancha en el centro (para el menú), y otra estrecha a la derecha.
    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        # Usamos st.radio para que las opciones aparezcan centradas y la inyección CSS las estiliza como cuadros.
        # El título "OPCIONES" ahora se centrará y estará en negrita gracias al CSS inyectado.
        seleccion_display = st.radio(
            "OPCIONES",
            opciones_display,
            key="main_menu_selection",
            horizontal=True
        )
        
        # Obtenemos la selección real (sin el icono) para la lógica condicional
        # Esto extrae la última palabra de la cadena (ej: "🏠 Inicio" -> "Inicio")
        seleccion = seleccion_display.split()[-1] 
    # --- Fin del código para centrar y enmarcar ---

    # Mostramos el contenido de la sección seleccionada fuera de las columnas.
    st.markdown("---") # Separador visual

    if seleccion == "Directiva":
        st.header(f"{iconos['Directiva']} Sección Directiva")
        st.write("Panel de control y herramientas para la Directiva.")
        pass # Bloque de código para Directiva

    elif seleccion == "Inicio":
        st.header(f"{iconos['Inicio']} Inicio del Sistema")
        st.write("Has seleccionado la página de inicio.")
        # Llamamos a la función que muestra el contenido principal.
        mostrar_bienvenido()
        
    elif seleccion == "Promotora":
        st.header(f"{iconos['Promotora']} Sección Promotora")
        st.write("Contenido específico y herramientas para el rol de Promotora.")
        pass

    elif seleccion == "Administrador":
        st.header(f"{iconos['Administrador']} Sección Administrador")
        st.write("Contenido de gestión y configuración para el Administrador.")
        pass
else:
    # Si la sesión no está iniciada o el estado es False,
    # llamamos a la función que muestra el formulario de inicio de sesión (login).
    login()
