import streamlit as st
from modulos.config.conexion import obtener_conexion

def Aporte():
    st.header("💰 Registrar Aporte")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener miembros disponibles para el campo FK
        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()

        # Obtener reuniones disponibles para el campo FK
        cursor.execute("""
            SELECT r.ID_Reunion, r.Fecha, r.Dia, g.Nombre 
            FROM REUNION r 
            LEFT JOIN GRUPOS g ON r.ID_Grupo = g.ID_Grupo 
            ORDER BY r.Fecha DESC
        """)
        reuniones = cursor.fetchall()

        # Formulario para registrar aporte
        with st.form("form_aporte"):
            # Campos principales
            Monto = st.number_input(
                "Monto del Aporte*", 
                min_value=0.0, 
                step=0.01,
                format="%.2f"
            )
            
            Fecha = st.date_input("Fecha del Aporte*")
            
            # Campo para Tipo
            tipo_options = ["Ordinario", "Extraordinario", "Voluntario", "Especial"]
            Tipo = st.selectbox("Tipo de Aporte*", tipo_options)
            
            # Campo FK para Dui (miembro)
            if miembros:
                miembro_options = {f"{miembro[1]} {miembro[2]} (DUI: {miembro[0]})": miembro[0] for miembro in miembros}
                miembro_seleccionado = st.selectbox("Miembro*", list(miembro_options.keys()))
                Dui = miembro_options[miembro_seleccionado]
            else:
                st.warning("No hay miembros activos disponibles. Debe crear un miembro primero.")
                Dui = None
            
            # Campo FK para ID_Reunion
            if reuniones:
                reunion_options = {f"Reunión {reunion[0]} - {reunion[1]} ({reunion[2]}) - {reunion[3]}": reunion[0] for reunion in reuniones}
                reunion_options["No asociado a reunión"] = None
                reunion_seleccionada = st.selectbox("Reunión asociada", list(reunion_options.keys()))
                ID_Reunion = reunion_options[reunion_seleccionada]
            else:
                st.info("No hay reuniones registradas disponibles")
                ID_Reunion = None
            
            enviar = st.form_submit_button("✅ Registrar Aporte")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Monto is None or not Fecha or 
                    Tipo.strip() == "" or not Dui):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar aporte - USANDO "APORTE"
                        sql_query = """
                            INSERT INTO APORTE (Monto, Fecha, Tipo, Dui, ID_Reunion) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            float(Monto),
                            Fecha,
                            str(Tipo),
                            int(Dui),
                            int(ID_Reunion) if ID_Reunion else None
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Aporte registrado correctamente: ${Monto:.2f} - {Tipo}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el aporte en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar aportes existentes
def mostrar_lista_aportes():
    st.header("📋 Lista de Aportes")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todos los aportes con información relacionada
        cursor.execute("""
            SELECT a.ID_Aporte, a.Monto, a.Fecha, a.Tipo, a.Dui, a.ID_Reunion,
                   m.Nombre as Miembro_Nombre, m.Apellido as Miembro_Apellido,
                   r.Fecha as Reunion_Fecha, r.Dia as Reunion_Dia, g.Nombre as Grupo_Nombre
            FROM APORTE a
            LEFT JOIN Miembro m ON a.Dui = m.Dui
            LEFT JOIN REUNION r ON a.ID_Reunion = r.ID_Reunion
            LEFT JOIN GRUPOS g ON r.ID_Grupo = g.ID_Grupo
            ORDER BY a.Fecha DESC, a.ID_Aporte DESC
        """)
        
        aportes = cursor.fetchall()
        
        if aportes:
            # Mostrar los aportes en una lista expandible
            st.subheader("Aportes Registrados")
            
            # Calcular total general
            total_general = sum(aporte[1] for aporte in aportes)
            st.info(f"**Total general de aportes: ${total_general:.2f}**")
            
            for aporte in aportes:
                with st.expander(f"💰 ${aporte[1]:.2f} - {aporte[6]} {aporte[7]} - {aporte[3]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Aporte:** {aporte[0]}")
                        st.write(f"**Monto:** ${aporte[1]:.2f}")
                        st.write(f"**Fecha:** {aporte[2]}")
                        st.write(f"**Tipo:** {aporte[3]}")
                        st.write(f"**DUI Miembro:** {aporte[4]}")
                    
                    with col2:
                        st.write(f"**Miembro:** {aporte[6]} {aporte[7]}")
                        if aporte[5]:  # Si hay reunión asociada
                            st.write(f"**Reunión ID:** {aporte[5]}")
                            st.write(f"**Fecha Reunión:** {aporte[8]}")
                            st.write(f"**Día Reunión:** {aporte[9]}")
                            st.write(f"**Grupo:** {aporte[10]}")
                        else:
                            st.write("**Reunión:** No asociado a reunión")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{aporte[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("🔄 Reembolsar", key=f"reembolsar_{aporte[0]}"):
                            st.info("💸 Funcionalidad de reembolso en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{aporte[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay aportes registrados aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de aportes: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar aportes
def buscar_aportes():
    st.header("🔍 Buscar Aportes")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Buscar por tipo
            tipo_options = ["Todos"] + ["Ordinario", "Extraordinario", "Voluntario", "Especial"]
            tipo_busqueda = st.selectbox("Tipo", tipo_options)
        
        with col2:
            fecha_desde = st.date_input("Fecha desde")
        
        with col3:
            fecha_hasta = st.date_input("Fecha hasta")
        
        # Buscar por miembro
        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()
        miembro_options = {f"{miembro[1]} {miembro[2]}": miembro[0] for miembro in miembros}
        miembro_busqueda = st.selectbox("Miembro", ["Todos"] + list(miembro_options.keys()))
        
        # Buscar por reunión
        cursor.execute("SELECT ID_Reunion, Fecha FROM REUNION ORDER BY Fecha DESC")
        reuniones = cursor.fetchall()
        reunion_options = {f"Reunión {reunion[0]} - {reunion[1]}": reunion[0] for reunion in reuniones}
        reunion_busqueda = st.selectbox("Reunión", ["Todas", "Sin reunión"] + list(reunion_options.keys()))
        
        # Filtro por monto
        col4, col5 = st.columns(2)
        with col4:
            monto_min = st.number_input("Monto mínimo", min_value=0.0, step=1.0, value=0.0)
        with col5:
            monto_max = st.number_input("Monto máximo", min_value=0.0, step=1.0, value=10000.0)
        
        buscar = st.button("🔍 Buscar Aportes")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT a.ID_Aporte, a.Monto, a.Fecha, a.Tipo, 
                       m.Nombre, m.Apellido,
                       r.Fecha as Reunion_Fecha
                FROM APORTE a
                LEFT JOIN Miembro m ON a.Dui = m.Dui
                LEFT JOIN REUNION r ON a.ID_Reunion = r.ID_Reunion
                WHERE 1=1
            """
            params = []
            
            if tipo_busqueda != "Todos":
                query += " AND a.Tipo = %s"
                params.append(tipo_busqueda)
            
            if fecha_desde:
                query += " AND a.Fecha >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND a.Fecha <= %s"
                params.append(fecha_hasta)
            
            if miembro_busqueda != "Todos":
                query += " AND a.Dui = %s"
                params.append(miembro_options[miembro_busqueda])
            
            if reunion_busqueda == "Sin reunión":
                query += " AND a.ID_Reunion IS NULL"
            elif reunion_busqueda != "Todas":
                query += " AND a.ID_Reunion = %s"
                params.append(reunion_options[reunion_busqueda])
            
            if monto_min > 0:
                query += " AND a.Monto >= %s"
                params.append(monto_min)
            
            if monto_max < 10000:
                query += " AND a.Monto <= %s"
                params.append(monto_max)
            
            query += " ORDER BY a.Monto DESC"
            
            cursor.execute(query, params)
            aportes_encontrados = cursor.fetchall()
            
            if aportes_encontrados:
                total_encontrado = sum(aporte[1] for aporte in aportes_encontrados)
                st.success(f"✅ Se encontraron {len(aportes_encontrados)} aporte(s) - Total: ${total_encontrado:.2f}")
                
                for aporte in aportes_encontrados:
                    with st.expander(f"💰 ${aporte[1]:.2f} - {aporte[4]} {aporte[5]} - {aporte[3]}"):
                        st.write(f"**ID:** {aporte[0]} | **Fecha:** {aporte[2]}")
                        if aporte[6]:
                            st.write(f"**Reunión:** {aporte[6]}")
            else:
                st.warning("🔍 No se encontraron aportes con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para estadísticas de aportes
def estadisticas_aportes():
    st.header("📊 Estadísticas de Aportes")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_aportes,
                SUM(Monto) as total_monto,
                AVG(Monto) as promedio_monto,
                MAX(Monto) as maximo_monto,
                MIN(Monto) as minimo_monto,
                COUNT(DISTINCT Dui) as miembros_aportantes
            FROM APORTE
        """)
        
        stats_general = cursor.fetchone()
        
        # Consulta para total por tipo
        cursor.execute("""
            SELECT Tipo, COUNT(*) as cantidad, SUM(Monto) as total
            FROM APORTE
            GROUP BY Tipo
            ORDER BY total DESC
        """)
        
        stats_tipo = cursor.fetchall()
        
        if stats_general and stats_general[0] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Aportes", f"{stats_general[0]}")
                st.metric("Monto Total", f"${stats_general[1]:.2f}")
            
            with col2:
                st.metric("Promedio por Aporte", f"${stats_general[2]:.2f}")
                st.metric("Miembros Aportantes", f"{stats_general[5]}")
            
            with col3:
                st.metric("Aporte Máximo", f"${stats_general[3]:.2f}")
                st.metric("Aporte Mínimo", f"${stats_general[4]:.2f}")
            
            # Estadísticas por tipo
            st.subheader("Aportes por Tipo")
            for tipo in stats_tipo:
                col_t1, col_t2, col_t3 = st.columns(3)
                with col_t1:
                    st.write(f"**{tipo[0]}**")
                with col_t2:
                    st.write(f"{tipo[1]} aportes")
                with col_t3:
                    st.write(f"${tipo[2]:.2f}")
                st.progress(tipo[2] / stats_general[1] if stats_general[1] > 0 else 0)
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
def gestionar_aportes():
    """
    Función principal para gestionar aportes
    """
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Registrar Aporte", "📋 Ver Aportes", "🔍 Buscar Aportes", "📊 Estadísticas"])
    
    with tab1:
        mostrar_aporte()
    
    with tab2:
        mostrar_lista_aportes()
    
    with tab3:
        buscar_aportes()
    
    with tab4:
        estadisticas_aportes()
