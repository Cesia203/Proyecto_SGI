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
            Dui = st.text_input("DUI")
            Nombre = st.text_input("Nombre")
            Apellido = st.text_input("Apellido")
            # Usamos 'Direccion' (sin tilde) para la variable Python y la sentencia SQL
            Direccion = st.text_input("Dirección") 
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
                            INSERT INTO Miembro (Dui, Nombre, Apellido, Direccion, Rol, Grupo, Distrito) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        # 4. Tupla de valores
                        values = (
                            dui_val,  
                            str(Nombre),  
                            str(Apellido),  
                            str(Direccion), 
                            str(Rol),  
                            str(Grupo),  
                            str(Distrito)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # 🚨 NUEVA LÓGICA: Guardar el estado de éxito para mostrar el botón
                        st.session_state['registro_exitoso'] = True
                        st.session_state['miembro_nombre'] = f"{Nombre} {Apellido} (DUI: {Dui})"
                        
                        # Importante: No se usa st.rerun() aquí para que el usuario pueda ver el mensaje
                        
                    except ValueError:
                         st.error("❌ Error: El valor del DUI debe ser un número entero.")
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el miembro en la base de datos: {e}")

        # 🚨 LÓGICA DEL BOTÓN "REGISTRAR OTRO MIEMBRO" (fuera del formulario)
        if 'registro_exitoso' in st.session_state and st.session_state['registro_exitoso']:
            st.success(f"✅ Miembro registrado correctamente: {st.session_state['miembro_nombre']}")
            
            # Botón explícito para registrar otro usuario
            if st.button("➕ Registrar otro miembro"):
                # Limpiar el estado de éxito y recargar la aplicación para limpiar el formulario
                st.session_state['registro_exitoso'] = False
                del st.session_state['miembro_nombre']
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()
