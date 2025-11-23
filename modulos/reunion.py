import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_reunion():
    st.header("📅 Registrar Reunión")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar reunión
        with st.form("form_reunion"):
            fecha = st.date_input("Fecha de la reunión")
            dia = st.text_input("Día (ej: Lunes, Martes...)")
            distrito = st.text_input("Distrito")
            id_grupo = st.number_input("ID del Grupo", min_value=1, step=1)
            id_asistencia = st.number_input("ID de Asistencia", min_value=1, step=1)
            tipo = st.selectbox("Tipo de reunión", ["Ordinaria", "Extraordinaria"])

            enviar = st.form_submit_button("✅ Guardar reunión")

            if enviar:
                # Validaciones básicas
                if dia.strip() == "" or distrito.strip() == "":
                    st.warning("⚠️ Todos los campos de texto deben llenarse.")
                else:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO REUNION (Fecha, Dia, Distrito, ID_Grupo, ID_Asistencia, Tipo)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (fecha, dia, distrito, int(id_grupo), int(id_asistencia), tipo)
                        )
                        con.commit()
                        st.success("✅ Reunión registrada correctamente")
                        st.rerun()
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la reunión: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
pdz-hudk-dcm
