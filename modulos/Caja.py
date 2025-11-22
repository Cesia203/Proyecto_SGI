import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_caja():
    st.header("💰 Registrar Movimiento de Caja")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtenemos las opciones para los dropdowns de llaves foráneas
        # Ciclos disponibles
        cursor.execute("SELECT ID_Ciclo FROM CICLO")
        ciclos = cursor.fetchall()
        opciones_ciclos = [str(ciclo[0]) for ciclo in ciclos] if ciclos else []

        # Ahorros disponibles
        cursor.execute("SELECT ID_Ahorro FROM AHORROS")
        ahorros = cursor.fetchall()
        opciones_ahorros = [str(ahorro[0]) for ahorro in ahorros] if ahorros else ["Ninguno"]

        # Préstamos disponibles
        cursor.execute("SELECT ID_Prestamo FROM PRESTAMO")
        prestamos = cursor.fetchall()
        opciones_prestamos = [str(prestamo[0]) for prestamo in prestamos] if prestamos else ["Ninguno"]

        # Pagos disponibles
        cursor.execute("SELECT ID_Pago FROM PAGO")
        pagos = cursor.fetchall()
        opciones_pagos = [str(pago[0]) for pago in pagos] if pagos else ["Ninguno"]

        # Formulario para registrar movimiento de caja
        with st.form("form_caja"):
            st.subheader("Datos Principales")
            Saldo_inicial = st.number_input("Saldo inicial", min_value=0.0, format="%.2f")
            Ingresos = st.number_input("Ingresos", min_value=0.0, format="%.2f", value=0.0)
            Egresos = st.number_input("Egresos", min_value=0.0, format="%.2f", value=0.0)
            Saldo_final = st.number_input("Saldo final", min_value=0.0, format="%.2f")

            st.subheader("Relaciones con otras tablas")
            # Dropdown para seleccionar el ciclo (obligatorio)
            if opciones_ciclos:
                ID_Ciclo = st.selectbox("Ciclo asociado *", opciones_ciclos)
            else:
                st.warning("No hay ciclos disponibles en el sistema")
                ID_Ciclo = None

            # Dropdowns opcionales para las otras relaciones
            ID_Ahorro = st.selectbox("Ahorro asociado (opcional)", ["Ninguno"] + opciones_ahorros)
            ID_Prestamo = st.selectbox("Préstamo asociado (opcional)", ["Ninguno"] + opciones_prestamos)
            ID_Pago = st.selectbox("Pago asociado (opcional)", ["Ninguno"] + opciones_pagos)
            
            enviar = st.form_submit_button("✅ Registrar Movimiento de Caja")

            if enviar:
                # 1. Validación de campos obligatorios
                if not ID_Ciclo or ID_Ciclo == "Ninguno":
                    st.warning("⚠️ Debes seleccionar un Ciclo asociado.")
                else:
                    try:
                        # 2. Procesar valores opcionales (convertir "Ninguno" a NULL)
                        id_ahorro_val = None if ID_Ahorro == "Ninguno" else int(ID_Ahorro)
                        id_prestamo_val = None if ID_Prestamo == "Ninguno" else int(ID_Prestamo)
                        id_pago_val = None if ID_Pago == "Ninguno" else int(ID_Pago)

                        # 3. Sentencia SQL para insertar en caja
                        sql_query = """
                            INSERT INTO CAJA (Saldo_inicial, Ingresos, Egresos, Saldo_final, 
                                            ID_Ciclo, ID_Ahorro, ID_Prestamo, ID_Pago) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        # 4. Tupla de valores
                        values = (
                            float(Saldo_inicial),
                            float(Ingresos),
                            float(Egresos),
                            float(Saldo_final),
                            int(ID_Ciclo),
                            id_ahorro_val,
                            id_prestamo_val,
                            id_pago_val
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito
                        st.success(f"✅ Movimiento de caja registrado correctamente")
                        st.success(f"💵 Saldo inicial: ${Saldo_inicial:.2f} | Ingresos: ${Ingresos:.2f} | Egresos: ${Egresos:.2f} | Saldo final: ${Saldo_final:.2f}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el movimiento de caja: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para visualizar movimientos de caja existentes
def mostrar_lista_caja():
    st.header("📋 Estado de Caja")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        cursor.execute("""
            SELECT c.ID_Caja, c.Saldo_inicial, c.Ingresos, c.Egresos, c.Saldo_final,
                   c.ID_Ciclo, c.ID_Ahorro, c.ID_Prestamo, c.ID_Pago
            FROM CAJA c
            ORDER BY c.ID_Caja DESC
        """)
        
        movimientos = cursor.fetchall()
        
        if movimientos:
            # Calcular totales
            total_ingresos = sum(mov[2] for mov in movimientos)
            total_egresos = sum(mov[3] for mov in movimientos)
            saldo_actual = movimientos[0][4] if movimientos else 0  # Último saldo final
            
            # Mostrar resumen
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Total Ingresos", f"${total_ingresos:.2f}")
            with col2:
                st.metric("💸 Total Egresos", f"${total_egresos:.2f}")
            with col3:
                st.metric("🏦 Saldo Actual", f"${saldo_actual:.2f}")
            
            st.subheader(f"Movimientos registrados: {len(movimientos)}")
            
            for mov in movimientos:
                with st.expander(f"Caja ID: {mov[0]} - Saldo: ${mov[4]:.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID Caja:** {mov[0]}")
                        st.write(f"**Saldo inicial:** ${mov[1]:.2f}")
                        st.write(f"**Ingresos:** ${mov[2]:.2f}")
                        st.write(f"**Egresos:** ${mov[3]:.2f}")
                        st.write(f"**Saldo final:** ${mov[4]:.2f}")
                    
                    with col2:
                        st.write(f"**ID Ciclo:** {mov[5]}")
                        st.write(f"**ID Ahorro:** {mov[6] if mov[6] else 'N/A'}")
                        st.write(f"**ID Préstamo:** {mov[7] if mov[7] else 'N/A'}")
                        st.write(f"**ID Pago:** {mov[8] if mov[8] else 'N/A'}")
                        
        else:
            st.info("📭 No hay movimientos de caja registrados en el sistema")
            
    except Exception as e:
        st.error(f"❌ Error al cargar los movimientos de caja: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para cálculo automático de saldo final
def calcular_saldo_automatico():
    st.sidebar.header("🧮 Calculadora de Saldo")
    
    saldo_inicial = st.sidebar.number_input("Saldo Inicial", min_value=0.0, format="%.2f")
    ingresos = st.sidebar.number_input("Ingresos del período", min_value=0.0, format="%.2f", value=0.0)
    egresos = st.sidebar.number_input("Egresos del período", min_value=0.0, format="%.2f", value=0.0)
    
    saldo_final = saldo_inicial + ingresos - egresos
    
    st.sidebar.metric("💡 Saldo Final Calculado", f"${saldo_final:.2f}")
    
    return saldo_final

# Función principal para gestionar caja
def gestionar_caja():
    st.title("🏦 Sistema de Gestión de Caja")
    
    # Mostrar calculadora en sidebar
    saldo_calculado = calcular_saldo_automatico()
    
    tab1, tab2 = st.tabs(["📝 Registrar Movimiento", "📋 Ver Estado de Caja"])
    
    with tab1:
        mostrar_caja()
    
    with tab2:
        mostrar_lista_caja()

# Para usar en tu aplicación principal
if __name__ == "__main__":
    gestionar_caja()