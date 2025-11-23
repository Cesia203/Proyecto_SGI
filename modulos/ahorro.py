import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ahorro():
    st.header("💰 Registrar Ahorro")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        with st.form("form_ahorro"):

            Monto_actual = st.number_input("Monto actual", min_value=0.00, step=0.01, format="%.2f")
            Dui = st.text_input("DUI del miembro")

            enviar = st.form_submit_button("✅ Guardar Ahorro")

            if enviar:
                if Dui.strip() == "":
                    st.warning("⚠️ Debes ingresar el DUI del miembro.")
                else:
                    try:
                        dui_val = int(Dui)  # Validación del DUI

                        sql_query = """
                            INSERT INTO AHORROS (Monto_actual, Dui)
                            VALUES (%s, %s)
                        """

                        values = (
                            float(Monto_actual),
                            dui_val
                        )

                        cursor.execute(sql_query, values)
                        con.commit()

                        st.success("💰 Ahorro registrado correctamente.")
                        st.rerun()

                    except ValueError:
                        st.error("❌ El DUI debe ser un número entero.")
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el ahorro: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
