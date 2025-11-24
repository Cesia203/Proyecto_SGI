import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import date

def mostrar_caja():
    st.header("📦 Registrar Movimiento de Caja")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        with st.form("form_caja"):

            saldo_inicial = st.number_input("Saldo inicial", min_value=0.00, step=0.01, format="%.2f")
            ingresos = st.number_input("Ingresos", min_value=0.00, step=0.01, format="%.2f")
            egresos = st.number_input("Egresos", min_value=0.00, step=0.01, format="%.2f")
            saldo_final = st.number_input("Saldo final", min_value=0.00, step=0.01, format="%.2f")

            fecha_registro = st.date_input("Fecha de registro", value=date.today())

            id_ciclo = st.number_input("ID Ciclo", min_value=1, step=1)

            st.write("IDs opcionales (pueden quedar vacíos):")
            id_ahorro = st.text_input("ID Ahorro (opcional)")
            id_prestamo = st.text_input("ID Préstamo (opcional)")
            id_pago = st.text_input("ID Pago (opcional)")

            enviar = st.form_submit_button("💾 Guardar en Caja")

            if enviar:

                try:
                    # Convertir IDs opcionales a enteros o None
                    id_ahorro_val = int(id_ahorro) if id_ahorro.strip() else None
                    id_prestamo_val = int(id_prestamo) if id_prestamo.strip() else None
                    id_pago_val = int(id_pago) if id_pago.strip() else None

                    sql_query = """
                        INSERT INTO CAJA (
                            Saldo_inicial, Ingresos, Egresos, Saldo_final,
                            Fecha_registro, ID_Ciclo, ID_Ahorro, ID_Prestamo, ID_Pago
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    values = (
                        float(saldo_inicial),
                        float(ingresos),
                        float(egresos),
                        float(saldo_final),
                        fecha_registro,
                        int(id_ciclo),
                        id_ahorro_val,
                        id_prestamo_val,
                        id_pago_val
                    )

                    cursor.execute(sql_query, values)
                    con.commit()

                    st.success("📦 Movimiento de caja registrado correctamente.")
                    st.rerun()

                except ValueError:
                    st.error("❌ Los campos ID deben ser números enteros.")
                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al insertar datos en la caja: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
