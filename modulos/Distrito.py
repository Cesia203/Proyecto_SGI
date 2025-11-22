import streamlit as st
from modulos.config.conexion import obtener_conexion

def Distrito():
    st.header("🗺️ Registrar Distrito")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener grupos disponibles para el campo FK
        cursor.execute("SELECT ID_Grupo, Nombre FROM GRUPOS WHERE Estado = 'Activo'")
        grupos = cursor.fetchall()

        # Formulario para registrar distrito
        with st.form("form_distrito"):
            # Campos principales
            Nombre = st.text_input("Nombre del Distrito*")
            Lugar = st.text_input("Lugar/Ubicación*")
            
            # Campo FK para ID_Grupo
            if grupos:
                grupo_options = {f"{grupo[1]} (ID: {grupo[0]})": grupo[0] for grupo in grupos}
                grupo_seleccionado = st.selectbox("Grupo*", list(grupo_options.keys()))
                ID_Grupo = grupo_options[grupo_seleccionado]
            else:
                st.warning("No hay grupos activos disponibles. Debe crear un grupo primero.")
                ID_Grupo = None
            
            enviar = st.form_submit_button("✅ Registrar Distrito")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Nombre.strip() == "" or Lugar.strip() == "" or not ID_Grupo):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar distrito - USANDO "DISTRITO"
                        sql_query = """
                            INSERT INTO DISTRITO (Nombre, Lugar, ID_Grupo) 
                            VALUES (%s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            str(Nombre),
                            str(Lugar),
                            int(ID_Grupo)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Distrito registrado correctamente: {Nombre} - {Lugar}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el distrito en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar distritos existentes
def mostrar_lista_distritos():
    st.header("📋 Lista de Distritos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todos los distritos con información del grupo
        cursor.execute("""
            SELECT d.ID_Distrito, d.Nombre, d.Lugar, d.ID_Grupo,
                   g.Nombre as Grupo_Nombre, g.Estado as Grupo_Estado
            FROM DISTRITO d
            LEFT JOIN GRUPOS g ON d.ID_Grupo = g.ID_Grupo
            ORDER BY d.Nombre ASC
        """)
        
        distritos = cursor.fetchall()
        
        if distritos:
            # Mostrar los distritos en una lista expandible
            st.subheader("Distritos Registrados")
            
            for distrito in distritos:
                with st.expander(f"🗺️ {distrito[1]} - {distrito[4]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Distrito:** {distrito[0]}")
                        st.write(f"**Nombre:** {distrito[1]}")
                        st.write(f"**Lugar:** {distrito[2]}")
                        st.write(f"**ID Grupo:** {distrito[3]}")
                    
                    with col2:
                        st.write(f"**Grupo:** {distrito[4]}")
                        st.write(f"**Estado Grupo:** {distrito[5]}")
                        
                        # Contar miembros en este distrito
                        cursor.execute("""
                            SELECT COUNT(*) 
                            FROM Miembro 
                            WHERE Distrito = %s
                        """, (distrito[1],))
                        total_miembros = cursor.fetchone()[0]
                        st.write(f"**Miembros en distrito:** {total_miembros}")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{distrito[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("👥 Ver Miembros", key=f"miembros_{distrito[0]}"):
                            st.info("👥 Funcionalidad de visualización de miembros en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{distrito[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay distritos registrados aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de distritos: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar distritos
def buscar_distritos():
    st.header("🔍 Buscar Distritos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Buscar por grupo
            cursor.execute("SELECT ID_Grupo, Nombre FROM GRUPOS")
            grupos = cursor.fetchall()
            grupo_options = {f"{grupo[1]}": grupo[0] for grupo in grupos}
            grupo_busqueda = st.selectbox("Grupo", ["Todos"] + list(grupo_options.keys()))
        
        with col2:
            # Buscar por lugar
            cursor.execute("SELECT DISTINCT Lugar FROM DISTRITO")
            lugares = cursor.fetchall()
            lugar_options = [lugar[0] for lugar in lugares]
            lugar_busqueda = st.selectbox("Lugar", ["Todos"] + lugar_options)
        
        # Búsqueda por nombre
        nombre_busqueda = st.text_input("Buscar por nombre")
        
        buscar = st.button("🔍 Buscar Distritos")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT d.ID_Distrito, d.Nombre, d.Lugar, 
                       g.Nombre as Grupo_Nombre
                FROM DISTRITO d
                LEFT JOIN GRUPOS g ON d.ID_Grupo = g.ID_Grupo
                WHERE 1=1
            """
            params = []
            
            if grupo_busqueda != "Todos":
                query += " AND d.ID_Grupo = %s"
                params.append(grupo_options[grupo_busqueda])
            
            if lugar_busqueda != "Todos":
                query += " AND d.Lugar = %s"
                params.append(lugar_busqueda)
            
            if nombre_busqueda.strip() != "":
                query += " AND d.Nombre LIKE %s"
                params.append(f"%{nombre_busqueda}%")
            
            query += " ORDER BY d.Nombre ASC"
            
            cursor.execute(query, params)
            distritos_encontrados = cursor.fetchall()
            
            if distritos_encontrados:
                st.success(f"✅ Se encontraron {len(distritos_encontrados)} distrito(s)")
                
                for distrito in distritos_encontrados:
                    with st.expander(f"🗺️ {distrito[1]} - {distrito[3]}"):
                        st.write(f"**ID:** {distrito[0]} | **Lugar:** {distrito[2]}")
                        
                        # Contar miembros para este distrito
                        cursor.execute("SELECT COUNT(*) FROM Miembro WHERE Distrito = %s", (distrito[1],))
                        total_miembros = cursor.fetchone()[0]
                        st.write(f"**Total miembros:** {total_miembros}")
            else:
                st.warning("🔍 No se encontraron distritos con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para estadísticas de distritos
def estadisticas_distritos():
    st.header("📊 Estadísticas de Distritos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_distritos,
                COUNT(DISTINCT Lugar) as lugares_unicos,
                COUNT(DISTINCT ID_Grupo) as grupos_con_distritos
            FROM DISTRITO
        """)
        
        stats_general = cursor.fetchone()
        
        # Consulta para distritos por grupo
        cursor.execute("""
            SELECT g.Nombre, COUNT(d.ID_Distrito) as total_distritos
            FROM GRUPOS g
            LEFT JOIN DISTRITO d ON g.ID_Grupo = d.ID_Grupo
            GROUP BY g.ID_Grupo, g.Nombre
            ORDER BY total_distritos DESC
        """)
        
        stats_grupo = cursor.fetchall()
        
        # Consulta para miembros por distrito
        cursor.execute("""
            SELECT d.Nombre, COUNT(m.Dui) as total_miembros
            FROM DISTRITO d
            LEFT JOIN Miembro m ON d.Nombre = m.Distrito
            GROUP BY d.ID_Distrito, d.Nombre
            ORDER BY total_miembros DESC
        """)
        
        stats_miembros = cursor.fetchall()
        
        if stats_general and stats_general[0] > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Distritos", f"{stats_general[0]}")
            
            with col2:
                st.metric("Lugares Únicos", f"{stats_general[1]}")
            
            with col3:
                st.metric("Grupos con Distritos", f"{stats_general[2]}")
            
            # Estadísticas por grupo
            st.subheader("Distritos por Grupo")
            for grupo in stats_grupo:
                col_g1, col_g2 = st.columns([3, 1])
                with col_g1:
                    st.write(f"**{grupo[0]}**")
                with col_g2:
                    st.write(f"{grupo[1]} distritos")
            
            # Estadísticas de miembros por distrito
            st.subheader("Miembros por Distrito")
            for distrito in stats_miembros:
                if distrito[1] > 0:
                    col_m1, col_m2 = st.columns([3, 1])
                    with col_m1:
                        st.write(f"**{distrito[0]}**")
                    with col_m2:
                        st.write(f"{distrito[1]} miembros")
        else:
            st.info("📊 No hay datos suficientes para mostrar estadísticas.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar las estadísticas: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para mapa de distritos
def mapa_distritos():
    st.header("🗺️ Mapa de Distritos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener distritos con información de ubicación
        cursor.execute("""
            SELECT d.Nombre, d.Lugar, g.Nombre as Grupo_Nombre,
                   COUNT(m.Dui) as total_miembros
            FROM DISTRITO d
            LEFT JOIN GRUPOS g ON d.ID_Grupo = g.ID_Grupo
            LEFT JOIN Miembro m ON d.Nombre = m.Distrito
            GROUP BY d.ID_Distrito, d.Nombre, d.Lugar, g.Nombre
            ORDER BY total_miembros DESC
        """)
        
        distritos = cursor.fetchall()
        
        if distritos:
            st.subheader("Distritos y su Distribución")
            
            for distrito in distritos:
                with st.expander(f"📍 {distrito[0]} - {distrito[1]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Distrito:** {distrito[0]}")
                        st.write(f"**Lugar:** {distrito[1]}")
                        st.write(f"**Grupo:** {distrito[2]}")
                    
                    with col2:
                        st.write(f"**Total Miembros:** {distrito[3]}")
                        
                        # Mostrar algunos miembros del distrito
                        if distrito[3] > 0:
                            cursor.execute("""
                                SELECT Nombre, Apellido, Dui 
                                FROM Miembro 
                                WHERE Distrito = %s 
                                LIMIT 5
                            """, (distrito[0],))
                            miembros = cursor.fetchall()
                            
                            st.write("**Algunos miembros:**")
                            for miembro in miembros:
                                st.write(f"- {miembro[0]} {miembro[1]} (DUI: {miembro[2]})")
        else:
            st.info("🗺️ No hay distritos para mostrar en el mapa.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar el mapa de distritos: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_distritos():
    """
    Función principal para gestionar distritos
    """
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Registrar Distrito", "📋 Ver Distritos", "🔍 Buscar Distritos", "📊 Estadísticas", "🗺️ Mapa"])
    
    with tab1:
        mostrar_distrito()
    
    with tab2:
        mostrar_lista_distritos()
    
    with tab3:
        buscar_distritos()
    
    with tab4:
        estadisticas_distritos()
    
    with tab5:
        mapa_distritos()
