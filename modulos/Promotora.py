import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_promotora():
    st.header("👨‍💼 Registrar Promotora")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar la promotora
        with st.form("form_promotora"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre")
                apellido = st.text_input("Apellido")
                telefono = st.text_input("Teléfono")
            
            with col2:
                correo = st.text_input("Correo electrónico")
                distrito = st.text_input("Distrito")
            
            enviar = st.form_submit_button("✅ Guardar promotora")

            if enviar:
                # Validaciones
                if nombre.strip() == "":
                    st.warning("⚠️ Debes ingresar el nombre.")
                elif apellido.strip() == "":
                    st.warning("⚠️ Debes ingresar el apellido.")
                else:
                    try:
                        cursor.execute(
                            "INSERT INTO PROMOTORA (Nombre, Apellido, Telefono, Correo, Distrito) VALUES (%s, %s, %s, %s, %s)",
                            (
                                nombre, 
                                apellido, 
                                telefono if telefono.strip() else None, 
                                correo if correo.strip() else None, 
                                distrito if distrito.strip() else None
                            )
                        )
                        con.commit()
                        st.success(f"✅ Promotora registrada correctamente: {nombre} {apellido}")
                        st.rerun()
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la promotora: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
trp-qowh-stb
