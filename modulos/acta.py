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

            enviar = st.form_submit_button("💾 Guardar Acta")

            if enviar:
                if contenido.strip() == "":
                    st.warning("⚠️ El contenido del acta no puede estar vacío.")
                else:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO ACTA (Tipo, Fecha, Contenido, ID_Ciclo)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (tipo, fecha, contenido, id_ciclo)
                        )
                        con.commit()
                        st.success("✅ Acta registrada correctamente")
                        st.rerun()

                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el acta: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
