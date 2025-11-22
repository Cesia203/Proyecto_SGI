import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_prestamo():
    st.header("💰 Registrar Préstamo")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener datos para los campos FK
        cursor.execute("SELECT ID_Promotora, Nombre FROM PROMOTORA WHERE Estado = 'Activa'")
        promotoras = cursor.fetchall()

        cursor.execute("SELECT ID_Ciclo, Fecha_inicio, Fecha_fin FROM CICLO WHERE Estado = 'Activo'")
        ciclos = cursor.fetchall()

        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()

        # Formulario para registrar préstamo
        with st.form("form_prestamo"):
            # Campos principales
            Monto = st.number_input(
                "Monto del Préstamo*", 
                min_value=0.0, 
                step=0.01,
                format="%.2f"
            )
            
            Intereses = st.number_input(
                "Tasa de Interés (%)*", 
                min_value=0.0, 
                max_value=100.0,
                step=0.1,
                format="%.1f"
            )
            
            Plazo_Meses = st.number_input(
                "Plazo en Meses*", 
                min_value=1, 
                max_value=360,
                step=1
            )
            
            Total_cuotas = st.number_input(
                "Total de Cuotas*", 
                min_value=1, 
                max_value=360,
                step=1
            )
            
            Saldo_restante = st.number_input(
                "Saldo Restante*", 
                min_value=0.0, 
                step=0.01,
                format="%.2f",
                value=0.0
            )
            
            # Campo para Estado
            estado_options = ["Activo", "Pagado", "Mora", "Cancelado", "Vencido"]
            Estado = st.selectbox("Estado del Préstamo*", estado_options)
            
            # Campos FK
            # ID_Promotora
            if promotoras:
                promotora_options = {f"{promotora[1]} (ID: {promotora[0]})": promotora[0] for promotora in promotoras}
                promotora_seleccionada = st.selectbox("Promotora*", list(promotora_options.keys()))
                ID_Promotora = promotora_options[promotora_seleccionada]
            else:
                st.warning("No hay promotoras activas disponibles.")
                ID_Promotora = None
            
            # ID_Ciclo
            if ciclos:
                ciclo_options = {f"Ciclo {ciclo[0]}: {ciclo[1]} a {ciclo[2]}": ciclo[0] for ciclo in ciclos}
                ciclo_seleccionado = st.selectbox("Ciclo*", list(ciclo_options.keys()))
                ID_Ciclo = ciclo_options[ciclo_seleccionado]
            else:
                st.warning("No hay ciclos activos disponibles.")
                ID_Ciclo = None
            
            # Dui (miembro)
            if miembros:
                miembro_options = {f"{miembro[1]} {miembro[2]} (DUI: {miembro[0]})": miembro[0] for miembro in miembros}
                miembro_seleccionado = st.selectbox("Miembro Solicitante*", list(miembro_options.keys()))
                Dui = miembro_options[miembro_seleccionado]
            else:
                st.warning("No hay miembros activos disponibles.")
                Dui = None
            
            enviar = st.form_submit_button("✅ Registrar Préstamo")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Monto is None or Intereses is None or Plazo_Meses is None or 
                    Total_cuotas is None or Saldo_restante is None or Estado.strip() == "" or
                    not ID_Promotora or not ID_Ciclo or not Dui):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                
                # 2. Validación de montos
                elif Saldo_restante > Monto:
                    st.warning("⚠️ El saldo restante no puede ser mayor al monto del préstamo.")
                
                else:
                    try:
                        # 3. Sentencia SQL para insertar préstamo - USANDO "PRESTAMO"
                        sql_query = """
                            INSERT INTO PRESTAMO (
                                Monto, Intereses, Plazo_Meses, Total_cuotas, 
                                Saldo_restante, Estado, ID_Promotora, ID_Ciclo, Dui
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        # 4. Tupla de valores
                        values = (
                            float(Monto),
                            float(Intereses),
                            int(Plazo_Meses),
                            int(Total_cuotas),
                            float(Saldo_restante),
                            str(Estado),
                            int(ID_Promotora),
                            int(ID_Ciclo),
                            int(Dui)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Calcular información adicional
                        interes_monto = (Monto * Intereses) / 100
                        total_pagar = Monto + interes_monto
                        valor_cuota = total_pagar / Total_cuotas if Total_cuotas > 0 else 0
                        
                        # Mensaje de éxito con información del préstamo
                        st.success(f"✅ Préstamo registrado correctamente: ${Monto:,.2f}")
                        st.info(f"""
                        **Resumen del Préstamo:**
                        - **Monto:** ${Monto:,.2f}
                        - **Intereses ({Intereses}%):** ${interes_monto:,.2f}
                        - **Total a Pagar:** ${total_pagar:,.2f}
                        - **Valor Cuota:** ${valor_cuota:,.2f}
                        - **Saldo Restante:** ${Saldo_restante:,.2f}
                        """)
                        
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el préstamo en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar préstamos existentes
def mostrar_lista_prestamos():
    st.header("📋 Lista de Préstamos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todos los préstamos con información relacionada
        cursor.execute("""
            SELECT p.ID_Prestamo, p.Monto, p.Intereses, p.Plazo_Meses, p.Total_cuotas, 
                   p.Saldo_restante, p.Estado, p.ID_Promotora, p.ID_Ciclo, p.Dui,
                   pr.Nombre as Promotora_Nombre,
                   c.Fecha_inicio as Ciclo_Inicio, c.Fecha_fin as Ciclo_Fin,
                   m.Nombre as Miembro_Nombre, m.Apellido as Miembro_Apellido
            FROM PRESTAMO p
            LEFT JOIN PROMOTORA pr ON p.ID_Promotora = pr.ID_Promotora
            LEFT JOIN CICLO c ON p.ID_Ciclo = c.ID_Ciclo
            LEFT JOIN Miembro m ON p.Dui = m.Dui
            ORDER BY p.ID_Prestamo DESC
        """)
        
        prestamos = cursor.fetchall()
        
        if prestamos:
            # Mostrar los préstamos en una lista expandible
            st.subheader("Préstamos Registrados")
            
            # Calcular totales
            total_prestamos = sum(prestamo[1] for prestamo in prestamos)
            total_saldo = sum(prestamo[5] for prestamo in prestamos)
            st.info(f"**Total préstamos:** ${total_prestamos:,.2f} | **Saldo pendiente:** ${total_saldo:,.2f}")
            
            for prestamo in prestamos:
                estado_icono = {
                    "Activo": "🟢",
                    "Pagado": "✅",
                    "Mora": "🔴",
                    "Cancelado": "⚫",
                    "Vencido": "⏰"
                }.get(prestamo[6], "⚪")
                
                with st.expander(f"{estado_icono} ${prestamo[1]:,.2f} - {prestamo[13]} {prestamo[14]} - {prestamo[6]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Préstamo:** {prestamo[0]}")
                        st.write(f"**Monto:** ${prestamo[1]:,.2f}")
                        st.write(f"**Interés:** {prestamo[2]}%")
                        st.write(f"**Plazo:** {prestamo[3]} meses")
                        st.write(f"**Total Cuotas:** {prestamo[4]}")
                        st.write(f"**Saldo Restante:** ${prestamo[5]:,.2f}")
                        st.write(f"**Estado:** {prestamo[6]}")
                    
                    with col2:
                        st.write(f"**Promotora:** {prestamo[10]}")
                        st.write(f"**ID Promotora:** {prestamo[7]}")
                        st.write(f"**Ciclo:** {prestamo[11]} a {prestamo[12]}")
                        st.write(f"**ID Ciclo:** {prestamo[8]}")
                        st.write(f"**Miembro:** {prestamo[13]} {prestamo[14]}")
                        st.write(f"**DUI:** {prestamo[9]}")
                        
                        # Calcular información adicional
                        interes_monto = (prestamo[1] * prestamo[2]) / 100
                        total_pagar = prestamo[1] + interes_monto
                        valor_cuota = total_pagar / prestamo[4] if prestamo[4] > 0 else 0
                        porcentaje_pagado = ((prestamo[1] - prestamo[5]) / prestamo[1]) * 100 if prestamo[1] > 0 else 0
                        
                        st.write(f"**Total a Pagar:** ${total_pagar:,.2f}")
                        st.write(f"**Valor Cuota:** ${valor_cuota:,.2f}")
                        st.write(f"**Porcentaje Pagado:** {porcentaje_pagado:.1f}%")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{prestamo[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("💵 Pago", key=f"pago_{prestamo[0]}"):
                            st.info("💰 Funcionalidad de pago en desarrollo...")
                    with col_act3:
                        if st.button("📊 Cuotas", key=f"cuotas_{prestamo[0]}"):
                            st.info("📅 Funcionalidad de cuotas en desarrollo...")
                    with col_act4:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{prestamo[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay préstamos registrados aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de préstamos: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar préstamos
def buscar_prestamos():
    st.header("🔍 Buscar Préstamos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estado_options = ["Todos"] + ["Activo", "Pagado", "Mora", "Cancelado", "Vencido"]
            estado_busqueda = st.selectbox("Estado", estado_options)
        
        with col2:
            # Buscar por miembro
            cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro")
            miembros = cursor.fetchall()
            miembro_options = {f"{miembro[1]} {miembro[2]}": miembro[0] for miembro in miembros}
            miembro_busqueda = st.selectbox("Miembro", ["Todos"] + list(miembro_options.keys()))
        
        with col3:
            # Buscar por promotora
            cursor.execute("SELECT ID_Promotora, Nombre FROM PROMOTORA")
            promotoras = cursor.fetchall()
            promotora_options = {f"{promotora[1]}": promotora[0] for promotora in promotoras}
            promotora_busqueda = st.selectbox("Promotora", ["Todas"] + list(promotora_options.keys()))
        
        # Filtros por monto
        col4, col5 = st.columns(2)
        with col4:
            monto_min = st.number_input("Monto mínimo", min_value=0.0, step=100.0, value=0.0)
        with col5:
            monto_max = st.number_input("Monto máximo", min_value=0.0, step=100.0, value=10000.0)
        
        buscar = st.button("🔍 Buscar Préstamos")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT p.ID_Prestamo, p.Monto, p.Intereses, p.Saldo_restante, p.Estado,
                       m.Nombre, m.Apellido,
                       pr.Nombre as Promotora_Nombre
                FROM PRESTAMO p
                LEFT JOIN Miembro m ON p.Dui = m.Dui
                LEFT JOIN PROMOTORA pr ON p.ID_Promotora = pr.ID_Promotora
                WHERE 1=1
            """
            params = []
            
            if estado_busqueda != "Todos":
                query += " AND p.Estado = %s"
                params.append(estado_busqueda)
            
            if miembro_busqueda != "Todos":
                query += " AND p.Dui = %s"
                params.append(miembro_options[miembro_busqueda])
            
            if promotora_busqueda != "Todas":
                query += " AND p.ID_Promotora = %s"
                params.append(promotora_options[promotora_busqueda])
            
            if monto_min > 0:
                query += " AND p.Monto >= %s"
                params.append(monto_min)
            
            if monto_max < 10000:
                query += " AND p.Monto <= %s"
                params.append(monto_max)
            
            query += " ORDER BY p.Monto DESC"
            
            cursor.execute(query, params)
            prestamos_encontrados = cursor.fetchall()
            
            if prestamos_encontrados:
                total_encontrado = sum(prestamo[1] for prestamo in prestamos_encontrados)
                saldo_encontrado = sum(prestamo[3] for prestamo in prestamos_encontrados)
                
                st.success(f"✅ Se encontraron {len(prestamos_encontrados)} préstamo(s)")
                st.info(f"**Total:** ${total_encontrado:,.2f} | **Saldo pendiente:** ${saldo_encontrado:,.2f}")
                
                for prestamo in prestamos_encontrados:
                    estado_icono = {
                        "Activo": "🟢",
                        "Pagado": "✅",
                        "Mora": "🔴",
                        "Cancelado": "⚫",
                        "Vencido": "⏰"
                    }.get(prestamo[4], "⚪")
                    
                    with st.expander(f"{estado_icono} ${prestamo[1]:,.2f} - {prestamo[5]} {prestamo[6]}"):
                        st.write(f"**ID:** {prestamo[0]} | **Interés:** {prestamo[2]}%")
                        st.write(f"**Saldo:** ${prestamo[3]:,.2f} | **Estado:** {prestamo[4]}")
                        st.write(f"**Promotora:** {prestamo[7]}")
            else:
                st.warning("🔍 No se encontraron préstamos con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para estadísticas de préstamos
def estadisticas_prestamos():
    st.header("📊 Estadísticas de Préstamos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_prestamos,
                SUM(Monto) as total_monto,
                SUM(Saldo_restante) as total_saldo,
                AVG(Monto) as promedio_monto,
                MAX(Monto) as maximo_monto,
                MIN(Monto) as minimo_monto,
                COUNT(DISTINCT Dui) as miembros_con_prestamo
            FROM PRESTAMO
        """)
        
        stats_general = cursor.fetchone()
        
        # Consulta para préstamos por estado
        cursor.execute("""
            SELECT Estado, COUNT(*) as cantidad, SUM(Monto) as total_monto, SUM(Saldo_restante) as total_saldo
            FROM PRESTAMO
            GROUP BY Estado
            ORDER BY total_monto DESC
        """)
        
        stats_estado = cursor.fetchall()
        
        if stats_general and stats_general[0] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Préstamos", f"{stats_general[0]}")
                st.metric("Monto Total", f"${stats_general[1]:,.2f}")
            
            with col2:
                st.metric("Saldo Pendiente", f"${stats_general[2]:,.2f}")
                st.metric("Promedio Préstamo", f"${stats_general[3]:,.2f}")
            
            with col3:
                st.metric("Préstamo Máximo", f"${stats_general[4]:,.2f}")
                st.metric("Miembros con Préstamo", f"{stats_general[6]}")
            
            # Estadísticas por estado
            st.subheader("Préstamos por Estado")
            for estado in stats_estado:
                col_e1, col_e2, col_e3, col_e4 = st.columns(4)
                with col_e1:
                    icono = {
                        "Activo": "🟢",
                        "Pagado": "✅",
                        "Mora": "🔴",
                        "Cancelado": "⚫",
                        "Vencido": "⏰"
                    }.get(estado[0], "⚪")
                    st.write(f"{icono} **{estado[0]}**")
                with col_e2:
                    st.write(f"{estado[1]} préstamos")
                with col_e3:
                    st.write(f"${estado[2]:,.2f}")
                with col_e4:
                    st.write(f"${estado[3]:,.2f}")
        else:
            st.info("📊 No hay datos suficientes para mostrar estadísticas.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar las estadísticas: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_prestamos():
    """
    Función principal para gestionar préstamos
    """
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Registrar Préstamo", "📋 Ver Préstamos", "🔍 Buscar Préstamos", "📊 Estadísticas"])
    
    with tab1:
        mostrar_prestamo()
    
    with tab2:
        mostrar_lista_prestamos()
    
    with tab3:
        buscar_prestamos()
    
    with tab4:
        estadisticas_prestamos()