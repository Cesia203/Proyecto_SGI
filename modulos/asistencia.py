import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_asistencia():
    st.header("📝 Registrar Asistencia")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        with st.form("form_asistencia"):

            Dui = st.text_input("DUI del miembro")
            presente_opciones = ["Presente", "Ausente"]
            PresenteAusente = st.selectbox("Estado", presente_opciones)

            Motivo = st.text_input("Motivo (si está ausente)")
            ID_Multa = st.number_input("ID de Multa (si aplica)", min_value=0, step=1)

            enviar = st.form_submit_button("✅ Guardar Asistencia")

            if enviar:
                if Dui.strip() == "":
                    st.warning("⚠️ Debes ingresar el DUI del miembro.")
                else:
                    try:
                        dui_val = int(Dui)  # Validación del DUI

                        sql_query = """
                            INSERT INTO ASISTENCIA (Dui, PresenteAusente, Motivo, ID_Multa)
                            VALUES (%s, %s, %s, %s)
                        """

                        values = (
                            dui_val,
                            PresenteAusente,
                            Motivo if Motivo.strip() != "" else None,
                            int(ID_Multa) if ID_Multa != 0 else None
                        )

                        cursor.execute(sql_query, values)
                        con.commit()

                        st.success("📝 Asistencia registrada correctamente.")
                        st.rerun()

                    except ValueError:
                        st.error("❌ El DUI debe ser un número entero.")
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la asistencia: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
