import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_Pago():
    st.header("💵 Registrar Pago")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar el pago
        with st.form("form_pago"):
            Fecha = st.date_input("📅 Fecha del pago")
            Monto = st.number_input("💲 Monto pagado", min_value=0.01, format="%.2f")
            Interes_pagado = st.number_input("💰 Interés pagado", min_value=0.00, format="%.2f")
            Multa_aplicada = st.selectbox("⚠️ ¿Multa aplicada?", ["Sí", "No"])
            Saldo_restante = st.number_input("💵 Saldo restante", min_value=0.00, format="%.2f")
            ID_Prestamo = st.number_input("🔢 ID del préstamo", min_value=1, step=1)

            enviar = st.form_submit_button("✅ Guardar Pago")

            if enviar:
                try:
                    cursor.execute(
                        """
                        INSERT INTO PAGO 
                        (Fecha, Monto, Interes_pagado, Multa_aplicada, Saldo_restante, ID_Prestamo)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (Fecha, Monto, Interes_pagado, Multa_aplicada, Saldo_restante, ID_Prestamo)
                    )
                    con.commit()
                    st.success("✅ Pago registrado correctamente.")
                    st.rerun()

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al registrar el pago: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
