import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_Prestamo():
    st.header("💰 Registrar Préstamo (Simple)")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario simple
        with st.form("form_prestamo_simple"):
            Monto = st.number_input("Monto", min_value=0.0, step=0.01, format="%.2f")
            Intereses = st.number_input("Intereses (%)", min_value=0.0, step=0.1, format="%.2f")
            Plazo_Meses = st.number_input("Plazo en Meses", min_value=1, step=1)
            Total_cuotas = st.number_input("Total de Cuotas", min_value=1, step=1)
            Saldo_restante = st.number_input("Saldo Restante", min_value=0.0, step=0.01, format="%.2f")
            ID_Promotora = st.number_input("ID_Promotora", min_value=1, step=1)
            ID_Ciclo = st.number_input("ID_Ciclo", min_value=1, step=1)
            Dui = st.number_input("Dui", min_value=1, step=1)

            enviar = st.form_submit_button("✅ Guardar préstamo")

            if enviar:

                # Validación básica
                if Monto == 0 or Intereses == 0 or Total_cuotas == 0:
                    st.warning("⚠️ Revisa los datos, hay campos obligatorios vacíos.")
                else:
                    try:
                        cursor.execute(
                            """
                            INSERT INTO PRESTAMO (
                                Monto, Intereses, Plazo_Meses, Total_cuotas,
                                Saldo_restante, ID_Promotora, ID_Ciclo, Dui
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (Monto, Intereses, Plazo_Meses, Total_cuotas,
                             Saldo_restante, ID_Promotora, ID_Ciclo, Dui)
                        )
                        con.commit()

                        st.success(f"✅ Préstamo registrado correctamente por ${Monto:,.2f}")
                        st.rerun()

                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el préstamo: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
