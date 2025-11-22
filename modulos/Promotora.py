import streamlit as st
from modulos.config.conexion import obtener_conexion

def Promotora():
    st.header("👩‍💼 Registrar Promotora")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener administradores disponibles para el campo FK
        cursor.execute("SELECT ID_Admin, Nombre, Apellido FROM ADMINISTRADOR WHERE Estado = 'Activo'")
        administradores = cursor.fetchall()

        # Formulario para registrar promotora
        with st.form("form_promotora"):
            # Campos principales
            Nombre = st.text_input("Nombre*")
            Apellido = st.text_input("Apellido*")
            Telefono = st.text_input("Teléfono*")
            Correo = st.text_input("Correo Electrónico*")
            Distrito = st.text_input("Distrito*")
            
            # Campo FK para ID_Admin
            if administradores:
                admin_options = {f"{admin[1]} {admin[2]} (ID: {admin[0]})": admin[0] for admin in administradores}
                admin_seleccionado = st.selectbox("Administrador Supervisor*", list(admin_options.keys()))
                ID_Admin = admin_options[admin_seleccionado]
            else:
                st.warning("No hay administradores activos disponibles. Debe crear un administrador primero.")
                ID_Admin = None
            
            enviar = st.form_submit_button("✅ Registrar Promotora")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Nombre.strip() == "" or Apellido.strip() == "" or 
                    Telefono.strip() == "" or Correo.strip() == "" or 
                    Distrito.strip() == "" or not ID_Admin):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar promotora - USANDO "PROMOTORA"
                        sql_query = """
                            INSERT INTO PROMOTORA (Nombre, Apellido, Telefono, Correo, Distrito, ID_Admin) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            str(Nombre),
                            str(Apellido),
                            str(Telefono),
                            str(Correo),
                            str(Distrito),
                            int(ID_Admin)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Promotora registrada correctamente: {Nombre} {Apellido}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la promotora en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar promotoras existentes
def mostrar_lista_promotoras():
    st.header("📋 Lista de Promotoras")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todas las promotoras con información del administrador
        cursor.execute("""
            SELECT p.ID_Promotora, p.Nombre, p.Apellido, p.Telefono, p.Correo, p.Distrito, p.ID_Admin,
                   a.Nombre as Admin_Nombre, a.Apellido as Admin_Apellido
            FROM PROMOTORA p
            LEFT JOIN ADMINISTRADOR a ON p.ID_Admin = a.ID_Admin
            ORDER BY p.Nombre, p.Apellido
        """)
        
        promotoras = cursor.fetchall()
        
        if promotoras:
            # Mostrar las promotoras en una lista expandible
            st.subheader("Promotoras Registradas")
            
            for promotora in promotoras:
                with st.expander(f"👩‍💼 {promotora[1]} {promotora[2]} - {promotora[5]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Promotora:** {promotora[0]}")
                        st.write(f"**Nombre:** {promotora[1]}")
                        st.write(f"**Apellido:** {promotora[2]}")
                        st.write(f"**Teléfono:** {promotora[3]}")
                        st.write(f"**Correo:** {promotora[4]}")
                    
                    with col2:
                        st.write(f"**Distrito:** {promotora[5]}")
                        st.write(f"**ID Admin Supervisor:** {promotora[6]}")
                        st.write(f"**Administrador Supervisor:** {promotora[7]} {promotora[8]}")
                        
                        # Contar préstamos asignados a esta promotora
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM PRESTAMO 
                            WHERE ID_Promotora = %s
                        """, (promotora[0],))
                        total_prestamos = cursor.fetchone()[0]
                        st.write(f"**Préstamos Asignados:** {total_prestamos}")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{promotora[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("💰 Préstamos", key=f"prestamos_{promotora[0]}"):
                            st.info("💵 Funcionalidad de préstamos en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{promotora[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay promotoras registradas aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de promotoras: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar promotoras
def buscar_promotoras():
    st.header("🔍 Buscar Promotoras")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Buscar por distrito
            cursor.execute("SELECT DISTINCT Distrito FROM PROMOTORA")
            distritos = cursor.fetchall()
            distrito_options = [distrito[0] for distrito in distritos]
            distrito_busqueda = st.selectbox("Distrito", ["Todos"] + distrito_options)
        
        with col2:
            # Buscar por administrador supervisor
            cursor.execute("SELECT DISTINCT a.ID_Admin, a.Nombre, a.Apellido FROM ADMINISTRADOR a JOIN PROMOTORA p ON a.ID_Admin = p.ID_Admin")
            administradores = cursor.fetchall()
            admin_options = {f"{admin[1]} {admin[2]}": admin[0] for admin in administradores}
            admin_busqueda = st.selectbox("Administrador Supervisor", ["Todos"] + list(admin_options.keys()))
        
        # Búsqueda por nombre o apellido
        nombre_busqueda = st.text_input("Buscar por nombre o apellido")
        
        buscar = st.button("🔍 Buscar Promotoras")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT p.ID_Promotora, p.Nombre, p.Apellido, p.Telefono, p.Correo, p.Distrito,
                       a.Nombre as Admin_Nombre, a.Apellido as Admin_Apellido
                FROM PROMOTORA p
                LEFT JOIN ADMINISTRADOR a ON p.ID_Admin = a.ID_Admin
                WHERE 1=1
            """
            params = []
            
            if distrito_busqueda != "Todos":
                query += " AND p.Distrito = %s"
                params.append(distrito_busqueda)
            
            if admin_busqueda != "Todos":
                query += " AND p.ID_Admin = %s"
                params.append(admin_options[admin_busqueda])
            
            if nombre_busqueda.strip() != "":
                query += " AND (p.Nombre LIKE %s OR p.Apellido LIKE %s)"
                params.append(f"%{nombre_busqueda}%")
                params.append(f"%{nombre_busqueda}%")
            
            query += " ORDER BY p.Nombre, p.Apellido"
            
            cursor.execute(query, params)
            promotoras_encontradas = cursor.fetchall()
            
            if promotoras_encontradas:
                st.success(f"✅ Se encontraron {len(promotoras_encontradas)} promotora(s)")
                
                for promotora in promotoras_encontradas:
                    with st.expander(f"👩‍💼 {promotora[1]} {promotora[2]} - {promotora[5]}"):
                        st.write(f"**ID:** {promotora[0]} | **Teléfono:** {promotora[3]}")
                        st.write(f"**Correo:** {promotora[4]} | **Supervisor:** {promotora[6]} {promotora[7]}")
                        
                        # Contar préstamos
                        cursor.execute("SELECT COUNT(*) FROM PRESTAMO WHERE ID_Promotora = %s", (promotora[0],))
                        total_prestamos = cursor.fetchone()[0]
                        st.write(f"**Préstamos Asignados:** {total_prestamos}")
            else:
                st.warning("🔍 No se encontraron promotoras con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para estadísticas de promotoras
def estadisticas_promotoras():
    st.header("📊 Estadísticas de Promotoras")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_promotoras,
                COUNT(DISTINCT Distrito) as distritos_cubiertos,
                COUNT(DISTINCT ID_Admin) as administradores_supervisores
            FROM PROMOTORA
        """)
        
        stats_general = cursor.fetchone()
        
        # Consulta para promotoras por distrito
        cursor.execute("""
            SELECT Distrito, COUNT(*) as cantidad_promotoras
            FROM PROMOTORA
            GROUP BY Distrito
            ORDER BY cantidad_promotoras DESC
        """)
        
        stats_distrito = cursor.fetchall()
        
        # Consulta para promotoras por administrador
        cursor.execute("""
            SELECT a.Nombre, a.Apellido, COUNT(p.ID_Promotora) as cantidad_promotoras
            FROM ADMINISTRADOR a
            LEFT JOIN PROMOTORA p ON a.ID_Admin = p.ID_Admin
            GROUP BY a.ID_Admin, a.Nombre, a.Apellido
            HAVING cantidad_promotoras > 0
            ORDER BY cantidad_promotoras DESC
        """)
        
        stats_admin = cursor.fetchall()
        
        # Consulta para préstamos por promotora
        cursor.execute("""
            SELECT p.Nombre, p.Apellido, COUNT(pr.ID_Prestamo) as total_prestamos,
                   COALESCE(SUM(pr.Monto), 0) as monto_total_prestamos
            FROM PROMOTORA p
            LEFT JOIN PRESTAMO pr ON p.ID_Promotora = pr.ID_Promotora
            GROUP BY p.ID_Promotora, p.Nombre, p.Apellido
            ORDER BY total_prestamos DESC
        """)
        
        stats_prestamos = cursor.fetchall()
        
        if stats_general and stats_general[0] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Promotoras", f"{stats_general[0]}")
            
            with col2:
                st.metric("Distritos Cubiertos", f"{stats_general[1]}")
            
            with col3:
                st.metric("Supervisores Activos", f"{stats_general[2]}")
            
            # Estadísticas por distrito
            st.subheader("Promotoras por Distrito")
            for distrito in stats_distrito:
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    st.write(f"**{distrito[0]}**")
                with col_d2:
                    st.write(f"{distrito[1]} promotoras")
            
            # Estadísticas por administrador
            st.subheader("Promotoras por Supervisor")
            for admin in stats_admin:
                col_a1, col_a2 = st.columns([3, 1])
                with col_a1:
                    st.write(f"**{admin[0]} {admin[1]}**")
                with col_a2:
                    st.write(f"{admin[2]} promotoras")
            
            # Estadísticas de préstamos
            st.subheader("Préstamos por Promotora")
            for promotora in stats_prestamos:
                if promotora[2] > 0:
                    col_p1, col_p2, col_p3 = st.columns([2, 1, 2])
                    with col_p1:
                        st.write(f"**{promotora[0]} {promotora[1]}**")
                    with col_p2:
                        st.write(f"{promotora[2]} préstamos")
                    with col_p3:
                        st.write(f"${promotora[3]:,.2f}")
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
def gestionar_promotoras():
    """
    Función principal para gestionar promotoras
    """
    tab1, tab2, tab3, tab4 = st.tabs(["👩‍💼 Registrar Promotora", "📋 Ver Promotoras", "🔍 Buscar Promotoras", "📊 Estadísticas"])
    
    with tab1:
        mostrar_promotora()
    
    with tab2:
        mostrar_lista_promotoras()
    
    with tab3:
        buscar_promotoras()
    
    with tab4:
        estadisticas_promotoras()
