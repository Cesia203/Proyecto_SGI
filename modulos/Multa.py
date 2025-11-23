import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_Multa():
    st.header("⚠️ Registrar Multa")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # FORMULARIO
        with st.form("form_multa"):
            tipo = st.text_input("Tipo de multa")
            monto = st.number_input("Monto", min_value=0.00, format="%.2f")
            descripcion = st.text_area("Descripción")
            fecha = st.date_input("Fecha de la multa")
            estado = st.selectbox("Estado", ["Pendiente", "Pagada"])
            dui = st.number_input("DUI", min_value=1, step=1)

            enviar = st.form_submit_button("💾 Guardar multa")

            if enviar:
                if tipo.strip() == "":
                    st.warning("⚠️ Debes ingresar el tipo de multa.")
                else:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO MULTA (Tipo, Monto, Descripccion, Fecha, Estado, Dui)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (tipo, monto, descripcion, fecha, estado, dui)
                        )
                        con.commit()
                        st.success("✅ Multa registrada correctamente.")
                        st.rerun()
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la multa: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
