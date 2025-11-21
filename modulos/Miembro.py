import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_Miembro():
    st.header("🛒 Registrar miembro")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar miembro
        with st.form("form_venta"):
           Nombre = st.text_input("Nombre ")
          Apellido = st.text_input("Apellido")
          Direccion = st.text_input("Direccion")
          Rol = st.text_input("Rol")
          Grupo = st.text_input("AGrupo")
          Distrito = st.text_input("Apellido")
     
          
            Dui = st.number_input("Cantidad", min_value=1, step=8)



          
            enviar = st.form_submit_button("✅ Miembro registrado")

            if enviar:
                if producto.strip() == "":
                    st.warning("⚠️ Debes ingresar informacion")
                else:
                    try:
                        cursor.execute(
                            "INSERT INTO Miembro (Dui, Nombre, Apellido, Direccion, Rol, Grupo, Distrito) VALUES (%s, %s)",
                            (Dui, str(Nombre),str(Apellido),str(Direccion),str(Rol),str(Grupo),str(Direccion))
                        )
                        con.commit()
                        st.success(f"✅ Venta registrada correctamente: {producto} (Cantidad: {cantidad})")
                        st.rerun()
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar : {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
