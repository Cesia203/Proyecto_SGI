import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_reunion():
    st.header("📅 Registrar Reunión")

    try:
        # Intentar obtener la conexión
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario
        with st.form("form_reunion"):

            Fecha = st.date_input("Fecha de la reunión")
            Dia = st.text_input("Día")
            Distrito = st.text_input("Distrito")
            ID_Grupo = st.text_input("ID_Grupo")
            ID_Asistencia = st.text_input("ID de Asistencia")
            Tipo = st.text_input("Tipo de reunión")

            enviar = st.form_submit_button("✅ Registrar Reunión")

            if enviar:
                # Validación básica
                if str(Dia).strip() == "" or str(Distrito).strip() == "" or str(ID_Grupo).strip() == "":
                    st.warning("⚠️ Debes completar al menos Día, Distrito y Grupo.")
                else:
                    try:
                        # Conversión de ID_Asistencia si viene como número
                        id_asistencia_val = int(ID_Asistencia) if ID_Asistencia.strip() != "" else None

                        # Consulta SQL
                        sql_query = """
                            INSERT INTO REUNION (Fecha, Dia, Distrito, ID_Grupo, ID_Asistencia, Tipo)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """

                        values = (
                            str(Fecha),     
                            str(Dia),
                            str(Distrito),
                            str(ID_Grupo),
                            id_asistencia_val,
                            str(Tipo)
                        )

                        cursor.execute(sql_query, values)
                        con.commit()

                        st.success(f"📌 Reunión registrada correctamente para el día {Dia} ({Fecha}).")
                        st.rerun()

                    except ValueError:
                        st.error("❌ Error: El ID de Asistencia debe ser numérico.")
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la reunión: {e}")

    except Exception as e:
        st.error(f"❌ Error de conexión o error general: {e}")

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()
