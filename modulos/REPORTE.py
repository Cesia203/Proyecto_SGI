import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_reporte():
    st.header("📊 Generar Reporte")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener ciclos disponibles para el campo FK
        cursor.execute("SELECT ID_Ciclo, Fecha_inicio, Fecha_fin FROM CICLO WHERE Estado = 'Activo'")
        ciclos = cursor.fetchall()

        # Obtener administradores disponibles para el campo FK
        cursor.execute("SELECT ID_Admin, Nombre FROM ADMINISTRADOR WHERE Estado = 'Activo'")
        administradores = cursor.fetchall()

        # Formulario para generar reporte
        with st.form("form_reporte"):
            # Campos principales
            tipo_options = ["Financiero", "Asistencia", "Ahorros", "Multas", "Aportes", "General", "Personalizado"]
            Tipo = st.selectbox("Tipo de Reporte*", tipo_options)
            
            Fecha_generacion = st.date_input("Fecha de Generación*")
            
            Descripccion = st.text_area("Descripción del Reporte*", 
                                      placeholder="Ingrese la descripción o propósito del reporte...",
                                      height=100)
            
            # Campo FK para ID_Ciclo
            if ciclos:
                ciclo_options = {f"Ciclo {ciclo[0]}: {ciclo[1]} a {ciclo[2]}": ciclo[0] for ciclo in ciclos}
                ciclo_seleccionado = st.selectbox("Ciclo*", list(ciclo_options.keys()))
                ID_Ciclo = ciclo_options[ciclo_seleccionado]
            else:
                st.warning("No hay ciclos activos disponibles. Debe crear un ciclo primero.")
                ID_Ciclo = None
            
            # Campo FK para ID_Admin
            if administradores:
                admin_options = {f"{admin[1]} (ID: {admin[0]})": admin[0] for admin in administradores}
                admin_seleccionado = st.selectbox("Administrador Generador*", list(admin_options.keys()))
                ID_Admin = admin_options[admin_seleccionado]
            else:
                st.warning("No hay administradores activos disponibles.")
                ID_Admin = None
            
            enviar = st.form_submit_button("✅ Generar Reporte")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Tipo.strip() == "" or not Fecha_generacion or 
                    Descripccion.strip() == "" or not ID_Ciclo or not ID_Admin):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar reporte - USANDO "REPORTE"
                        sql_query = """
                            INSERT INTO REPORTE (Tipo, Fecha_generacion, Descripccion, ID_Ciclo, ID_Admin) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            str(Tipo),
                            Fecha_generacion,
                            str(Descripccion),
                            int(ID_Ciclo),
                            int(ID_Admin)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Reporte generado correctamente: {Tipo} - {Fecha_generacion}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al generar el reporte en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar reportes existentes
def mostrar_lista_reportes():
    st.header("📋 Lista de Reportes")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todos los reportes con información relacionada
        cursor.execute("""
            SELECT r.ID_Reporte, r.Tipo, r.Fecha_generacion, r.Descripccion, r.ID_Ciclo, r.ID_Admin,
                   c.Fecha_inicio as Ciclo_Inicio, c.Fecha_fin as Ciclo_Fin,
                   a.Nombre as Admin_Nombre
            FROM REPORTE r
            LEFT JOIN CICLO c ON r.ID_Ciclo = c.ID_Ciclo
            LEFT JOIN ADMINISTRADOR a ON r.ID_Admin = a.ID_Admin
            ORDER BY r.Fecha_generacion DESC, r.ID_Reporte DESC
        """)
        
        reportes = cursor.fetchall()
        
        if reportes:
            # Mostrar los reportes en una lista expandible
            st.subheader("Reportes Generados")
            
            for reporte in reportes:
                icono_tipo = {
                    "Financiero": "💰",
                    "Asistencia": "📊",
                    "Ahorros": "🏦",
                    "Multas": "⚖️",
                    "Aportes": "💵",
                    "General": "📈",
                    "Personalizado": "🔧"
                }.get(reporte[1], "📄")
                
                with st.expander(f"{icono_tipo} {reporte[1]} - {reporte[2]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Reporte:** {reporte[0]}")
                        st.write(f"**Tipo:** {reporte[1]}")
                        st.write(f"**Fecha Generación:** {reporte[2]}")
                        st.write(f"**ID Ciclo:** {reporte[4]}")
                        st.write(f"**ID Admin:** {reporte[5]}")
                    
                    with col2:
                        st.write(f"**Ciclo:** {reporte[6]} a {reporte[7]}")
                        st.write(f"**Administrador:** {reporte[8]}")
                        st.write("**Descripción:**")
                        st.write(reporte[3])
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3, col_act4 = st.columns(4)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{reporte[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("📥 Descargar", key=f"descargar_{reporte[0]}"):
                            st.info("💾 Funcionalidad de descarga en desarrollo...")
                    with col_act3:
                        if st.button("👁️ Ver Detalle", key=f"ver_{reporte[0]}"):
                            st.info("🔍 Funcionalidad de visualización en desarrollo...")
                    with col_act4:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{reporte[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay reportes generados aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de reportes: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar reportes
def buscar_reportes():
    st.header("🔍 Buscar Reportes")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_options = ["Todos"] + ["Financiero", "Asistencia", "Ahorros", "Multas", "Aportes", "General", "Personalizado"]
            tipo_busqueda = st.selectbox("Tipo", tipo_options)
        
        with col2:
            fecha_desde = st.date_input("Fecha desde")
        
        with col3:
            fecha_hasta = st.date_input("Fecha hasta")
        
        # Buscar por ciclo
        cursor.execute("SELECT ID_Ciclo, Fecha_inicio FROM CICLO ORDER BY Fecha_inicio DESC")
        ciclos = cursor.fetchall()
        ciclo_options = {f"Ciclo {ciclo[0]}": ciclo[0] for ciclo in ciclos}
        ciclo_busqueda = st.selectbox("Ciclo", ["Todos"] + list(ciclo_options.keys()))
        
        # Buscar por administrador
        cursor.execute("SELECT ID_Admin, Nombre FROM ADMINISTRADOR")
        administradores = cursor.fetchall()
        admin_options = {f"{admin[1]}": admin[0] for admin in administradores}
        admin_busqueda = st.selectbox("Administrador", ["Todos"] + list(admin_options.keys()))
        
        buscar = st.button("🔍 Buscar Reportes")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT r.ID_Reporte, r.Tipo, r.Fecha_generacion, r.Descripccion,
                       c.Fecha_inicio as Ciclo_Inicio, c.Fecha_fin as Ciclo_Fin,
                       a.Nombre as Admin_Nombre
                FROM REPORTE r
                LEFT JOIN CICLO c ON r.ID_Ciclo = c.ID_Ciclo
                LEFT JOIN ADMINISTRADOR a ON r.ID_Admin = a.ID_Admin
                WHERE 1=1
            """
            params = []
            
            if tipo_busqueda != "Todos":
                query += " AND r.Tipo = %s"
                params.append(tipo_busqueda)
            
            if fecha_desde:
                query += " AND r.Fecha_generacion >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND r.Fecha_generacion <= %s"
                params.append(fecha_hasta)
            
            if ciclo_busqueda != "Todos":
                query += " AND r.ID_Ciclo = %s"
                params.append(ciclo_options[ciclo_busqueda])
            
            if admin_busqueda != "Todos":
                query += " AND r.ID_Admin = %s"
                params.append(admin_options[admin_busqueda])
            
            query += " ORDER BY r.Fecha_generacion DESC"
            
            cursor.execute(query, params)
            reportes_encontrados = cursor.fetchall()
            
            if reportes_encontrados:
                st.success(f"✅ Se encontraron {len(reportes_encontrados)} reporte(s)")
                
                for reporte in reportes_encontrados:
                    icono_tipo = {
                        "Financiero": "💰",
                        "Asistencia": "📊",
                        "Ahorros": "🏦",
                        "Multas": "⚖️",
                        "Aportes": "💵",
                        "General": "📈",
                        "Personalizado": "🔧"
                    }.get(reporte[1], "📄")
                    
                    with st.expander(f"{icono_tipo} {reporte[1]} - {reporte[2]}"):
                        st.write(f"**ID:** {reporte[0]} | **Administrador:** {reporte[6]}")
                        st.write(f"**Ciclo:** {reporte[4]} a {reporte[5]}")
                        st.write(f"**Descripción:** {reporte[3]}")
            else:
                st.warning("🔍 No se encontraron reportes con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para estadísticas de reportes
def estadisticas_reportes():
    st.header("📈 Estadísticas de Reportes")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reportes,
                COUNT(DISTINCT Tipo) as tipos_diferentes,
                COUNT(DISTINCT ID_Admin) as administradores_generadores,
                MIN(Fecha_generacion) as fecha_primer_reporte,
                MAX(Fecha_generacion) as fecha_ultimo_reporte
            FROM REPORTE
        """)
        
        stats_general = cursor.fetchone()
        
        # Consulta para reportes por tipo
        cursor.execute("""
            SELECT Tipo, COUNT(*) as cantidad
            FROM REPORTE
            GROUP BY Tipo
            ORDER BY cantidad DESC
        """)
        
        stats_tipo = cursor.fetchall()
        
        # Consulta para reportes por administrador
        cursor.execute("""
            SELECT a.Nombre, COUNT(r.ID_Reporte) as cantidad_reportes
            FROM ADMINISTRADOR a
            LEFT JOIN REPORTE r ON a.ID_Admin = r.ID_Admin
            GROUP BY a.ID_Admin, a.Nombre
            ORDER BY cantidad_reportes DESC
        """)
        
        stats_admin = cursor.fetchall()
        
        if stats_general and stats_general[0] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Reportes", f"{stats_general[0]}")
                st.metric("Tipos Diferentes", f"{stats_general[1]}")
            
            with col2:
                st.metric("Administradores", f"{stats_general[2]}")
                if stats_general[3]:
                    st.metric("Primer Reporte", f"{stats_general[3]}")
            
            with col3:
                if stats_general[4]:
                    st.metric("Último Reporte", f"{stats_general[4]}")
            
            # Estadísticas por tipo
            st.subheader("Reportes por Tipo")
            for tipo in stats_tipo:
                col_t1, col_t2 = st.columns([3, 1])
                with col_t1:
                    icono = {
                        "Financiero": "💰",
                        "Asistencia": "📊",
                        "Ahorros": "🏦",
                        "Multas": "⚖️",
                        "Aportes": "💵",
                        "General": "📈",
                        "Personalizado": "🔧"
                    }.get(tipo[0], "📄")
                    st.write(f"{icono} **{tipo[0]}**")
                with col_t2:
                    st.write(f"{tipo[1]} reportes")
            
            # Estadísticas por administrador
            st.subheader("Reportes por Administrador")
            for admin in stats_admin:
                if admin[1] > 0:
                    col_a1, col_a2 = st.columns([3, 1])
                    with col_a1:
                        st.write(f"**{admin[0]}**")
                    with col_a2:
                        st.write(f"{admin[1]} reportes")
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
def gestionar_reportes():
    """
    Función principal para gestionar reportes
    """
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Generar Reporte", "📋 Ver Reportes", "🔍 Buscar Reportes", "📈 Estadísticas"])
    
    with tab1:
        mostrar_reporte()
    
    with tab2:
        mostrar_lista_reportes()
    
    with tab3:
        buscar_reportes()
    
    with tab4:
        estadisticas_reportes()