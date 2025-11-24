import streamlit as st
from datetime import date
from modulos.config.conexion import obtener_conexion

def mostrar_acta():
    st.header("📄 Registrar Acta")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        with st.form("form_acta"):

            # Campo enum: Tipo de acta
            tipo = st.selectbox(
                "Tipo de Acta",
                ["Ordinaria", "Extraordinaria", "Especial"]
            )

            fecha = st.date_input("Fecha del Acta", value=date.today())

            contenido = st.text_area("Contenido del Acta")

            id_ciclo = st.number_input("ID Ciclo", min_value=1, step=1)
