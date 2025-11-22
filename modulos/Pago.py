import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_pago():
    st.header("💳 Registrar Pago")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Primero obtenemos los préstamos disponibles para el dropdown
        cursor.execute("SELECT ID_Prestamo FROM PRESTAMO")
        prestamos = cursor.fetchall()
        opciones_prestamos = [str(prestamo[0]) for prestamo in prestamos] if prestamos else []

        # Formulario para registrar pago
        with st.form("form_pago"):
            # Variables del formulario
            Fecha = st.date_input("Fecha del pago")
            Monto = st.number_input("Monto", min_value=0.0, format="%.2f")
            Interes_pagado = st.number_input("Interés pagado", min_value=0.0, format="%.2f")
            Multa_aplicada = st.selectbox("Multa aplicada", ["si", "no"])
            Saldo_restante = st.number_input("Saldo restante", min_value=0.0, format="%.2f")
            
            # Dropdown para seleccionar el préstamo
            if opciones_prestamos:
                ID_Prestamo = st.selectbox("Préstamo asociado", opciones_prestamos)
            else:
                st.warning("No hay préstamos disponibles en el sistema")
                ID_Prestamo = None
            
            enviar = st.form_submit_button("✅ Registrar Pago")

            if enviar:
                # 1. Validación de campos obligatorios
                if not Fecha or Monto <= 0 or not ID_Prestamo:
                    st.warning("⚠️ Debes completar al menos Fecha, Monto y seleccionar un Préstamo.")
                else:
                    try:
                        # 2. Sentencia SQL para insertar pago
                        sql_query = """
                            INSERT INTO PAGO (Fecha, Monto, Interes_pagado, Multa_aplicada, Saldo_restante, ID_Prestamo) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            Fecha,
                            float(Monto),
                            float(Interes_pagado),
                            str(Multa_aplicada),
                            float(Saldo_restante),
                            int(ID_Prestamo)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Pago registrado correctamente: ${Monto:.2f} para préstamo {ID_Prestamo}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el pago en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para visualizar pagos existentes
def mostrar_lista_pagos():
    st.header("📋 Lista de Pagos Registrados")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT p.ID_Pago, p.Fecha, p.Monto, p.Interes_pagado, 
                   p.Multa_aplicada, p.Saldo_restante, p.ID_Prestamo
            FROM PAGO p
            ORDER BY p.Fecha DESC
        """)
        
        pagos = cursor.fetchall()
        
        if pagos:
            st.subheader(f"Total de pagos: {len(pagos)}")
            
            for pago in pagos:
                with st.expander(f"Pago ID: {pago[0]} - ${pago[2]:.2f} - {pago[1]}"):
                    st.write(f"**ID Pago:** {pago[0]}")
                    st.write(f"**Fecha:** {pago[1]}")
                    st.write(f"**Monto:** ${pago[2]:.2f}")
                    st.write(f"**Interés pagado:** ${pago[3]:.2f}")
                    st.write(f"**Multa aplicada:** {pago[4]}")
                    st.write(f"**Saldo restante:** ${pago[5]:.2f}")
                    st.write(f"**ID Préstamo:** {pago[6]}")
        else:
            st.info("📭 No hay pagos registrados en el sistema")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de pagos: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal para gestionar pagos
def gestionar_pagos():
    st.title("🏦 Sistema de Gestión de Pagos")
    
    tab1, tab2 = st.tabs(["📝 Registrar Pago", "📋 Ver Pagos Existentes"])
    
    with tab1:
        mostrar_pago()
    
    with tab2:
        mostrar_lista_pagos()

# Para usar en tu aplicación principal
if __name__ == "__main__":
    gestionar_pagos()