import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_miembro():
    # El título parece más adecuado para "Registro" que para "Carrito de compras"
    st.header("📝 Registrar Miembro")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar miembro
        with st.form("form_miembro"):
            # 1. Variables del formulario
             # El Dui debería ser de 8 dígitos para un documento de identidad,
            # pero el paso (step) de 8 es inusual, se dejó en 1.
            # Se usa st.text_input y se convierte a entero si es necesario para DB.
            Dui = st.text_input("DUI")
            Nombre = st.text_input("Nombre")
            Apellido = st.text_input("Apellido")
            Direccion = st.text_input("Dirección")
            Rol = st.text_input("Rol")
            Grupo = st.text_input("Grupo") # Se corrigió 'AGrupo' por 'Grupo' para consistencia
            # ¡CUIDADO! Se repite el 'Apellido' aquí. Lo cambiamos a 'Distrito' que es el campo correcto.
            Distrito = st.text_input("Distrito")
            
           
            

            enviar = st.form_submit_button("✅ Registrar")

            if enviar:
                # 2. Validación: Usar la variable correcta (e.g., Nombre) en lugar de 'producto'
                if Nombre.strip() == "" or Apellido.strip() == "" or Dui.strip() == "":
                    st.warning("⚠️ Debes ingresar al menos el Nombre, Apellido y DUI.")
                else:
                    try:
                        # Convertir Dui a entero antes de la inserción si es necesario, 
                        # o manejarlo como string si la columna en DB es TEXT/VARCHAR. 
                        # Asumo que Dui es un número entero.
                        dui_val = int(Dui)
                        
                        # 3. y 4. Corrección de la sentencia SQL: 7 columnas = 7 marcadores (%s)
                        sql_query = """
                            INSERT INTO Miembro (Dui, Nombre, Apellido, Direccion, Rol, Grupo, Distrito) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        # 4. Corrección de la tupla de valores: Pasar las 7 variables en el orden correcto
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
                        
                        # Mensaje de éxito corregido
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
