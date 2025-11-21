import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_miembro():
    st.header("📝 Registrar Miembro")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar miembro
        with st.form("form_miembro"):
            # Variables del formulario
            # El campo mostrado al usuario sigue siendo 'Dirección' (con tilde)
            Dui = st.text_input("DUI")
            Nombre = st.text_input("Nombre")
            Apellido = st.text_input("Apellido")
            # 👈 La variable Python se llama 'Direccion' (sin tilde)
            Dirección = st.text_input("Dirección") 
            Rol = st.text_input("Rol")
            Grupo = st.text_input("Grupo")
            Distrito = st.text_input("Distrito")
            
            enviar = st.form_submit_button("✅ Registrar")

            if enviar:
                # 1. Validación de campos obligatorios
                if Nombre.strip() == "" or Apellido.strip() == "" or Dui.strip() == "":
                    st.warning("⚠️ Debes ingresar al menos el Nombre, Apellido y DUI.")
                else:
                    try:
                        # 2. Conversión de Dui
                        dui_val = int(Dui)
                        
                        # 3. Sentencia SQL corregida: usando 'Direccion' (sin tilde)
                        sql_query = """
                            INSERT INTO Miembro (Dui, Nombre, Apellido, Dirección, Rol, Grupo, Distrito) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        # 4. Tupla de valores (usando la variable 'Direccion' sin tilde)
                        values = (
                            dui_val,  
                            str(Nombre),  
                            str(Apellido),  
                            str(Dirección), # Usamos la variable sin tilde
                            str(Rol),  
                            str(Grupo),  
                            str(Distrito)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Miembro registrado correctamente: {Nombre} {Apellido} (DUI: {Dui})")
                        st.rerun()
                        
                    except ValueError:
                         st.error("❌ Error: El valor del DUI debe ser un número entero.")
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el miembro en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()
