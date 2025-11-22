import streamlit as st
import datetime
# Mantener la importación de la conexión a la base de datos
from modulos.config.conexion import obtener_conexion

def mostrar_registro_ahorro():
    """
    Muestra el formulario para registrar un nuevo depósito de ahorro
    y gestiona la inserción de datos en la tabla 'Ahorro'.
    """
    st.header("💰 Registrar Depósito de Ahorro")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar ahorro
        with st.form("form_ahorro"):
            # Variables del formulario para la transacción
            dui_miembro = st.text_input("DUI del Miembro")
            monto_deposito = st.text_input("Monto del Depósito ($)")
            
            enviar = st.form_submit_button("✅ Registrar Ahorro")

            if enviar:
                # 1. Validación de campos obligatorios
                if dui_miembro.strip() == "" or monto_deposito.strip() == "":
                    st.warning("⚠️ Debes ingresar el DUI del Miembro y el Monto del Depósito.")
                else:
                    try:
                        # 2. Conversión de Dui y Monto a números
                        dui_val = int(dui_miembro)
                        monto_val = float(monto_deposito)
                        
                        # 3. Obtener la fecha y hora actual para el registro
                        fecha_actual = datetime.datetime.now()
                        
                        # NOTA IMPORTANTE:
                        # En una aplicación real, el 'Saldo_actual' debería calcularse leyendo el saldo anterior
                        # del miembro y sumándole el 'Monto_actual' (depósito).
                        # Para simplificar y solo registrar, se usará el monto del depósito para 'Saldo_actual'.
                        # La lógica de saldos debe manejarse con cuidado en el backend.
                        
                        # 4. Sentencia SQL para insertar en la tabla Ahorro
                        # Se asume que la tabla tiene las columnas: Dui, Monto_actual, Saldo_actual, Fecha_Actualizacion
                        sql_query = """
                            INSERT INTO Ahorro (Dui, Monto_actual, Saldo_actual, Fecha_Actualizacion) 
                            VALUES (%s, %s, %s, %s)
                        """
                        
                        # 5. Tupla de valores
                        values = (
                            dui_val,             # Dui
                            monto_val,           # Monto_actual (El depósito)
                            monto_val,           # Saldo_actual (Temporalmente igual al depósito. ¡Ajustar lógica de balance!)
                            fecha_actual         # Fecha_Actualizacion
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Depósito de ${monto_val:.2f} registrado correctamente para el DUI: {dui_miembro}")
                        st.rerun()
                        
                    except ValueError:
                        st.error("❌ Error: El valor del DUI debe ser un número entero y el Monto un número válido.")
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el ahorro en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Si quieres probar esta función en un script Streamlit local, puedes añadir:
# if __name__ == "__main__":
#     # Debes asegurarte de que 'obtener_conexion' esté disponible y configurado
#     mostrar_registro_ahorro()
