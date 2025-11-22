import streamlit as st
from modulos.config.conexion import obtener_conexion

# Renombrado de la función para registro (Originalmente incompleta)
def registrar_ahorro():
    st.header("💰 Registrar Nuevo Ahorro")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        # Obtener miembros activos para el selectbox
        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()
        miembro_options = {f"{miembro[1]} {miembro[2]} - {miembro[0]}": miembro[0] for miembro in miembros}
        
        if not miembros:
            st.warning("⚠️ No hay miembros activos para registrar ahorros.")
            return

        with st.form("form_ahorro"):
            # Selectbox para el miembro
            miembro_seleccionado = st.selectbox("Seleccione Miembro", list(miembro_options.keys()), key="reg_miembro")
            
            # Campos de monto y saldo inicial
            monto_actual = st.number_input("Monto Inicial", min_value=1.00, step=1.00, format="%.2f", key="reg_monto")
            saldo_actual = st.number_input("Saldo Inicial", min_value=1.00, step=1.00, format="%.2f", key="reg_saldo")
            
            fecha_actualizacion = st.date_input("Fecha de Registro", key="reg_fecha")
            
            submitted = st.form_submit_button("Guardar Ahorro", type="primary")

            if submitted:
                dui = miembro_options[miembro_seleccionado]
                
                # Insertar el nuevo registro de ahorro
                cursor.execute(
                    "INSERT INTO AHORROS (Monto_actual, Saldo_actual, Fecha_actualizacion, Dui) VALUES (%s, %s, %s, %s)",
                    (monto_actual, saldo_actual, fecha_actualizacion, dui)
                )
                con.commit()
                st.success(f"✅ Ahorro registrado exitosamente para {miembro_seleccionado}.")
                st.info(f"Monto: ${monto_actual:.2f}, Saldo: ${saldo_actual:.2f}")

    except Exception as e:
        st.error(f"❌ Error al registrar el ahorro: {e}")
    finally:
        # Cerrar conexión
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar ahorros existentes
def mostrar_lista_ahorros():
    st.header("📋 Lista de Ahorros")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todos los ahorros con información del miembro
        cursor.execute("""
            SELECT a.ID_Ahorro, a.Monto_actual, a.Saldo_actual, a.Fecha_actualizacion, a.Dui,
                    m.Nombre, m.Apellido
            FROM AHORROS a
            LEFT JOIN Miembro m ON a.Dui = m.Dui
            ORDER BY a.Fecha_actualizacion DESC, a.ID_Ahorro DESC
        """)
        
        ahorros = cursor.fetchall()
        
        if ahorros:
            # Mostrar los ahorros en una lista expandible
            st.subheader("Registros de Ahorros")
            
            for ahorro in ahorros:
                with st.expander(f"💰 {ahorro[5]} {ahorro[6]} - ${ahorro[1]:.2f}"):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.write(f"**ID Ahorro:** {ahorro[0]}")
                        st.write(f"**Monto Actual:** ${ahorro[1]:.2f}")
                        st.write(f"**Saldo Actual:** ${ahorro[2]:.2f}")
                        st.write(f"**Fecha Actualización:** {ahorro[3]}")
                    
                    with col2:
                        st.write(f"**Miembro:** {ahorro[5]} {ahorro[6]}")
                        st.write(f"**DUI:** {ahorro[4]}")
                        
                        # Calcular diferencia entre monto y saldo
                        diferencia = ahorro[1] - ahorro[2]
                        if diferencia > 0:
                            st.write(f"**Diferencia:** -${diferencia:.2f}")
                        elif diferencia < 0:
                            st.write(f"**Diferencia:** +${abs(diferencia):.2f}")
                        else:
                            st.write(f"**Diferencia:** $0.00")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{ahorro[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("💳 Depositar", key=f"depositar_{ahorro[0]}"):
                            st.info("💰 Funcionalidad de depósito en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{ahorro[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay registros de ahorros aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de ahorros: {e}")
    finally:
        # CORRECCIÓN: locales() a locals()
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar ahorros
def buscar_ahorros():
    st.header("🔍 Buscar Ahorros")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Buscar por miembro
            cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
            miembros = cursor.fetchall()
            miembro_options = {f"{miembro[1]} {miembro[2]}": miembro[0] for miembro in miembros}
            miembro_busqueda = st.selectbox("Miembro", ["Todos"] + list(miembro_options.keys()))
        
        with col2:
            # Filtro por rango de montos
            monto_min = st.number_input("Monto mínimo", min_value=0.0, step=1.0, value=0.0)
            monto_max = st.number_input("Monto máximo", min_value=0.0, step=1.0, value=10000.0)
        
        # Filtro por fecha
        col3, col4 = st.columns(2)
        with col3:
            fecha_desde = st.date_input("Fecha desde")
        with col4:
            fecha_hasta = st.date_input("Fecha hasta")
        
        buscar = st.button("🔍 Buscar Ahorros")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT a.ID_Ahorro, a.Monto_actual, a.Saldo_actual, a.Fecha_actualizacion, a.Dui,
                        m.Nombre, m.Apellido
                FROM AHORROS a
                LEFT JOIN Miembro m ON a.Dui = m.Dui
                WHERE 1=1
            """
            params = []
            
            if miembro_busqueda != "Todos":
                query += " AND a.Dui = %s"
                params.append(miembro_options[miembro_busqueda])
            
            if monto_min > 0:
                query += " AND a.Monto_actual >= %s"
                params.append(monto_min)
            
            if monto_max < 10000:
                query += " AND a.Monto_actual <= %s"
                params.append(monto_max)
            
            if fecha_desde:
                query += " AND a.Fecha_actualizacion >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND a.Fecha_actualizacion <= %s"
                params.append(fecha_hasta)
            
            query += " ORDER BY a.Monto_actual DESC"
            
            cursor.execute(query, params)
            ahorros_encontrados = cursor.fetchall()
            
            if ahorros_encontrados:
                # Calcular totales
                total_monto = sum(ahorro[1] for ahorro in ahorros_encontrados)
                total_saldo = sum(ahorro[2] for ahorro in ahorros_encontrados)
                
                st.success(f"✅ Se encontraron {len(ahorros_encontrados)} registro(s) de ahorros")
                st.info(f"**Total Monto:** ${total_monto:.2f} | **Total Saldo:** ${total_saldo:.2f}")
                
                for ahorro in ahorros_encontrados:
                    with st.expander(f"💰 {ahorro[5]} {ahorro[6]} - ${ahorro[1]:.2f}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**ID:** {ahorro[0]}")
                            st.write(f"**Monto Actual:** ${ahorro[1]:.2f}")
                            st.write(f"**Saldo Actual:** ${ahorro[2]:.2f}")
                        with col2:
                            st.write(f"**Fecha:** {ahorro[3]}")
                            st.write(f"**DUI:** {ahorro[4]}")
            else:
                st.warning("🔍 No se encontraron registros de ahorros con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para resumen de ahorros
def resumen_ahorros():
    st.header("📊 Resumen de Ahorros")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ahorros,
                SUM(Monto_actual) as total_monto,
                SUM(Saldo_actual) as total_saldo,
                AVG(Monto_actual) as promedio_monto,
                MAX(Monto_actual) as maximo_monto,
                MIN(Monto_actual) as minimo_monto
            FROM AHORROS
        """)
        
        stats = cursor.fetchone()
        
        if stats and stats[0] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Ahorros", f"{stats[0]}")
                st.metric("Monto Total", f"${stats[1]:.2f}")
            
            with col2:
                st.metric("Saldo Total", f"${stats[2]:.2f}")
                st.metric("Promedio por Ahorro", f"${stats[3]:.2f}")
            
            with col3:
                st.metric("Monto Máximo", f"${stats[4]:.2f}")
                st.metric("Monto Mínimo", f"${stats[5]:.2f}")
            
            # Diferencia total entre monto y saldo
            diferencia_total = stats[1] - stats[2]
            if diferencia_total != 0:
                st.info(f"**Diferencia total entre Monto y Saldo:** ${diferencia_total:.2f}")
        else:
            st.info("📊 No hay datos suficientes para mostrar estadísticas.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar el resumen: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas (renombrada de 'gestionar_ahorros' a 'mostrar_ahorro'
# para que coincida con la importación en app.py)
def mostrar_ahorro():
    """
    Función principal para gestionar ahorros.
    Organiza la vista de gestión de ahorros en pestañas.
    """
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Registrar Ahorro", "📋 Ver Ahorros", "🔍 Buscar Ahorros", "📊 Resumen"])
    
    with tab1:
        registrar_ahorro()
    
    with tab2:
        mostrar_lista_ahorros()
    
    with tab3:
        buscar_ahorros()
    
    with tab4:
        resumen_ahorros(
