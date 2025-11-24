import streamlit as st
from datetime import date
from modulos.config.conexion import obtener_conexion

def registrar_ciclo():
    st.header("🔄 Registrar Ciclo")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        with st.form("form_ciclo"):

            fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
            fecha_fin = st.date_input("Fecha de fin (opcional)", value=None)

            estado = st.selectbox(
                "Estado del ciclo",
                ["Activo", "Finalizado", "Pendiente"]
            )

            utilidad_total = st.number_input(
                "Utilidad total (opcional)",
                min_value=0.00,
                step=0.01,
                format="%.2f"
            )

            enviar = st.form_submit_button("💾 Guardar Ciclo")

            if enviar:
                try:
                    # Fecha fin permite NULL
                    fecha_fin_val = fecha_fin if fecha_fin is not None else None

                    # Utilidad permite NULL
                    utilidad_val = float(utilidad_total) if utilidad_total > 0 else None

                    sql_query = """
                        INSERT INTO CICLO (Fecha_inicio, Fecha_fin, Estado, Utilidad_Total)
                        VALUES (%s, %s, %s, %s)
                    """

                    values = (
                        fecha_inicio,
                        fecha_fin_val,
                        estado,
                        utilidad_val
                    )

                    cursor.execute(sql_query, values)
                    con.commit()

                    st.success("🔄 Ciclo registrado exitosamente.")
                    st.rerun()

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al registrar el ciclo: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "con" in locals():
            con.close()
