import streamlit as st
from modulos.config.conexion import obtener_conexion

def Administrador():
    st.header("👨‍💼 Registrar Administrador")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener miembros disponibles para el campo FK
        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()

        # Obtener distritos disponibles para el campo FK
        cursor.execute("SELECT ID_Distrito, Nombre, Lugar FROM DISTRITO")
        distritos = cursor.fetchall()

        # Formulario para registrar administrador
        with st.form("form_administrador"):
            # Campos principales
            Nombre = st.text_input("Nombre*")
            Apellido = st.text_input("Apellido*")
            Correo = st.text_input("Correo Electrónico*")
            
            # Campo para Rol
            rol_options = ["Super Admin", "Administrador", "Coordinador", "Supervisor"]
            Rol = st.selectbox("Rol*", rol_options)
            
            # Campo FK para Dui (miembro)
            if miembros:
                miembro_options = {f"{miembro[1]} {miembro[2]} (DUI: {miembro[0]})": miembro[0] for miembro in miembros}
                miembro_options["No asociado a miembro"] = None
                miembro_seleccionado = st.selectbox("Miembro Asociado", list(miembro_options.keys()))
                Dui = miembro_options[miembro_seleccionado]
            else:
                st.warning("No hay miembros activos disponibles.")
                Dui = None
            
            # Campo FK para ID_Distrito
            if distritos:
                distrito_options = {f"{distrito[1]} - {distrito[2]}": distrito[0] for distrito in distritos}
                distrito_seleccionado = st.selectbox("Distrito*", list(distrito_options.keys()))
                ID_Distrito = distrito_options[distrito_seleccionado]
            else:
                st.warning("No hay distritos disponibles. Debe crear un distrito primero.")
                ID_Distrito = None
            
            enviar = st.form_submit_button("✅ Registrar Administrador")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Nombre.strip() == "" or Apellido.strip() == "" or 
                    Correo.strip() == "" or Rol.strip() == "" or not ID_Distrito):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar administrador - USANDO "ADMINISTRADOR"
                        sql_query = """
                            INSERT INTO ADMINISTRADOR (Nombre, Apellido, Correo, Rol, Dui, ID_Distrito) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            str(Nombre),
                            str(Apellido),
                            str(Correo),
                            str(Rol),
                            int(Dui) if Dui else None,
                            int(ID_Distrito)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Administrador registrado correctamente: {Nombre} {Apellido}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el administrador en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar administradores existentes
def mostrar_lista_administradores():
    st.header("📋 Lista de Administradores")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todos los administradores con información relacionada
        cursor.execute("""
            SELECT a.ID_Admin, a.Nombre, a.Apellido, a.Correo, a.Rol, a.Dui, a.ID_Distrito,
                   m.Nombre as Miembro_Nombre, m.Apellido as Miembro_Apellido,
                   d.Nombre as Distrito_Nombre, d.Lugar as Distrito_Lugar
            FROM ADMINISTRADOR a
            LEFT JOIN Miembro m ON a.Dui = m.Dui
            LEFT JOIN DISTRITO d ON a.ID_Distrito = d.ID_Distrito
            ORDER BY a.Nombre, a.Apellido
        """)
        
        administradores = cursor.fetchall()
        
        if administradores:
            # Mostrar los administradores en una lista expandible
            st.subheader("Administradores Registrados")
            
            for admin in administradores:
                icono_rol = {
                    "Super Admin": "👑",
                    "Administrador": "👨‍💼",
                    "Coordinador": "📋",
                    "Supervisor": "👀"
                }.get(admin[4], "👤")
                
                with st.expander(f"{icono_rol} {admin[1]} {admin[2]} - {admin[4]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Admin:** {admin[0]}")
                        st.write(f"**Nombre:** {admin[1]}")
                        st.write(f"**Apellido:** {admin[2]}")
                        st.write(f"**Correo:** {admin[3]}")
                        st.write(f"**Rol:** {admin[4]}")
                    
                    with col2:
                        if admin[5]:  # Si está asociado a un miembro
                            st.write(f"**Miembro Asociado:** {admin[7]} {admin[8]}")
                            st.write(f"**DUI Miembro:** {admin[5]}")
                        else:
                            st.write("**Miembro Asociado:** No asociado")
                        
                        st.write(f"**Distrito:** {admin[9]}")
                        st.write(f"**Ubicación:** {admin[10]}")
                        st.write(f"**ID Distrito:** {admin[6]}")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{admin[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("🔑 Permisos", key=f"permisos_{admin[0]}"):
                            st.info("🔐 Funcionalidad de permisos en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{admin[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay administradores registrados aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de administradores: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar administradores
def buscar_administradores():
    st.header("🔍 Buscar Administradores")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2 = st.columns(2)
        
        with col1:
            rol_options = ["Todos"] + ["Super Admin", "Administrador", "Coordinador", "Supervisor"]
            rol_busqueda = st.selectbox("Rol", rol_options)
        
        with col2:
            # Buscar por distrito
            cursor.execute("SELECT ID_Distrito, Nombre FROM DISTRITO")
            distritos = cursor.fetchall()
            distrito_options = {f"{distrito[1]}": distrito[0] for distrito in distritos}
            distrito_busqueda = st.selectbox("Distrito", ["Todos"] + list(distrito_options.keys()))
        
        # Búsqueda por nombre o apellido
        nombre_busqueda = st.text_input("Buscar por nombre o apellido")
        
        # Filtro por asociación con miembro
        asociacion_options = ["Todos", "Con miembro", "Sin miembro"]
        asociacion_busqueda = st.selectbox("Asociación con miembro", asociacion_options)
        
        buscar = st.button("🔍 Buscar Administradores")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT a.ID_Admin, a.Nombre, a.Apellido, a.Correo, a.Rol,
                       m.Nombre as Miembro_Nombre, m.Apellido as Miembro_Apellido,
                       d.Nombre as Distrito_Nombre
                FROM ADMINISTRADOR a
                LEFT JOIN Miembro m ON a.Dui = m.Dui
                LEFT JOIN DISTRITO d ON a.ID_Distrito = d.ID_Distrito
                WHERE 1=1
            """
            params = []
            
            if rol_busqueda != "Todos":
                query += " AND a.Rol = %s"
                params.append(rol_busqueda)
            
            if distrito_busqueda != "Todos":
                query += " AND a.ID_Distrito = %s"
                params.append(distrito_options[distrito_busqueda])
            
            if nombre_busqueda.strip() != "":
                query += " AND (a.Nombre LIKE %s OR a.Apellido LIKE %s)"
                params.append(f"%{nombre_busqueda}%")
                params.append(f"%{nombre_busqueda}%")
            
            if asociacion_busqueda == "Con miembro":
                query += " AND a.Dui IS NOT NULL"
            elif asociacion_busqueda == "Sin miembro":
                query += " AND a.Dui IS NULL"
            
            query += " ORDER BY a.Nombre, a.Apellido"
            
            cursor.execute(query, params)
            administradores_encontrados = cursor.fetchall()
            
            if administradores_encontrados:
                st.success(f"✅ Se encontraron {len(administradores_encontrados)} administrador(es)")
                
                for admin in administradores_encontrados:
                    icono_rol = {
                        "Super Admin": "👑",
                        "Administrador": "👨‍💼",
                        "Coordinador": "📋",
                        "Supervisor": "👀"
                    }.get(admin[4], "👤")
                    
                    with st.expander(f"{icono_rol} {admin[1]} {admin[2]} - {admin[4]}"):
                        st.write(f"**ID:** {admin[0]} | **Correo:** {admin[3]}")
                        st.write(f"**Distrito:** {admin[6]}")
                        if admin[5]:
                            st.write(f"**Miembro Asociado:** {admin[5]} {admin[6]}")
                        else:
                            st.write("**Miembro Asociado:** No asociado")
            else:
                st.warning("🔍 No se encontraron administradores con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para estadísticas de administradores
def estadisticas_administradores():
    st.header("📊 Estadísticas de Administradores")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_administradores,
                COUNT(DISTINCT Rol) as roles_diferentes,
                COUNT(DISTINCT ID_Distrito) as distritos_cubiertos,
                COUNT(Dui) as administradores_con_miembro,
                (COUNT(*) - COUNT(Dui)) as administradores_sin_miembro
            FROM ADMINISTRADOR
        """)
        
        stats_general = cursor.fetchone()
        
        # Consulta para administradores por rol
        cursor.execute("""
            SELECT Rol, COUNT(*) as cantidad
            FROM ADMINISTRADOR
            GROUP BY Rol
            ORDER BY cantidad DESC
        """)
        
        stats_rol = cursor.fetchall()
        
        # Consulta para administradores por distrito
        cursor.execute("""
            SELECT d.Nombre, COUNT(a.ID_Admin) as cantidad_administradores
            FROM DISTRITO d
            LEFT JOIN ADMINISTRADOR a ON d.ID_Distrito = a.ID_Distrito
            GROUP BY d.ID_Distrito, d.Nombre
            ORDER BY cantidad_administradores DESC
        """)
        
        stats_distrito = cursor.fetchall()
        
        if stats_general and stats_general[0] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Administradores", f"{stats_general[0]}")
                st.metric("Roles Diferentes", f"{stats_general[1]}")
            
            with col2:
                st.metric("Distritos Cubiertos", f"{stats_general[2]}")
                st.metric("Con Miembro", f"{stats_general[3]}")
            
            with col3:
                st.metric("Sin Miembro", f"{stats_general[4]}")
            
            # Estadísticas por rol
            st.subheader("Administradores por Rol")
            for rol in stats_rol:
                col_r1, col_r2 = st.columns([3, 1])
                with col_r1:
                    icono = {
                        "Super Admin": "👑",
                        "Administrador": "👨‍💼",
                        "Coordinador": "📋",
                        "Supervisor": "👀"
                    }.get(rol[0], "👤")
                    st.write(f"{icono} **{rol[0]}**")
                with col_r2:
                    st.write(f"{rol[1]} administradores")
            
            # Estadísticas por distrito
            st.subheader("Administradores por Distrito")
            for distrito in stats_distrito:
                if distrito[1] > 0:
                    col_d1, col_d2 = st.columns([3, 1])
                    with col_d1:
                        st.write(f"**{distrito[0]}**")
                    with col_d2:
                        st.write(f"{distrito[1]} administradores")
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
def gestionar_administradores():
    """
    Función principal para gestionar administradores
    """
    tab1, tab2, tab3, tab4 = st.tabs(["👨‍💼 Registrar Administrador", "📋 Ver Administradores", "🔍 Buscar Administradores", "📊 Estadísticas"])
    
    with tab1:
        mostrar_administrador()
    
    with tab2:
        mostrar_lista_administradores()
    
    with tab3:
        buscar_administradores()
    
    with tab4:
        estadisticas_administradores()
