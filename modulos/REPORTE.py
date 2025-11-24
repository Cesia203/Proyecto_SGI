import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_reporte():
    st.header("📝 Registrar Reporte")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        with st.form("form_reporte"):

            tipo = st.text_input("Tipo de reporte")
            descripcion = st.text_area("Descripción")
            id_ciclo = st.number_input("ID del Ciclo", min_value=1, step=1)
            id_admin = st.number_input("ID del Administrador", min_value=1, step=1)

            enviar = st.form_submit_button("✅ Guardar Reporte")

            if enviar:
                if tipo.strip() == "":
                    st.warning("⚠️ Debes ingresar el tipo de reporte.")
                elif descripcion.strip() == "":
                    st.warning("⚠️ Debes ingresar una descripción.")
                else:
                    try:
                        sql_query = """
                            INSERT INTO REPORTES (Tipo, Descripcion, ID_Ciclo, ID_Admin)
                            VALUES (%s, %s, %s, %s)
                        """

                        values = (
                            tipo,
                            descripcion,
                            int(id_ciclo),
                            int(id_admin)
                        )

                        cursor.execute(sql_query, values)
                        con.commit()

                        st.success("📝 Reporte registrado correctamente.")
                        st.rerun()

                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el reporte: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
