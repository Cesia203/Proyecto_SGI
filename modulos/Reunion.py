import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_reunion():
    st.header("📅 Registrar Reunión")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener grupos disponibles para el campo FK
        cursor.execute("SELECT ID_Grupo, Nombre FROM GRUPOS WHERE Estado = 'Activo'")
        grupos = cursor.fetchall()

        # Obtener asistencias disponibles para el campo FK
        cursor.execute("SELECT ID_Asistencia, Dui FROM ASISTENCIA")
        asistencias = cursor.fetchall()

        # Formulario para registrar reunión
        with st.form("form_reunion"):
            # Campos principales
            Fecha = st.date_input("Fecha de la Reunión*")
            
            # Campo para Día
            dia_options = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            Dia = st.selectbox("Día de la Reunión*", dia_options)
            
            Lugar = st.text_input("Lugar de la Reunión*")
            
            # Campo FK para ID_Grupo
            if grupos:
                grupo_options = {f"{grupo[1]} (ID: {grupo[0]})": grupo[0] for grupo in grupos}
                grupo_seleccionado = st.selectbox("Grupo*", list(grupo_options.keys()))
                ID_Grupo = grupo_options[grupo_seleccionado]
            else:
                st.warning("No hay grupos activos disponibles. Debe crear un grupo primero.")
                ID_Grupo = None
            
            # Campo FK para ID_Asistencia
            if asistencias:
                asistencia_options = {f"Asistencia {asistencia[0]} (DUI: {asistencia[1]})": asistencia[0] for asistencia in asistencias}
                asistencia_options["Ninguna"] = None
                asistencia_seleccionada = st.selectbox("Asistencia Extraordinaria/Ordinaria", list(asistencia_options.keys()))
                ID_Asistencia = asistencia_options[asistencia_seleccionada]
            else:
                st.info("No hay asistencias registradas disponibles")
                ID_Asistencia = None
            
            enviar = st.form_submit_button("✅ Registrar Reunión")

            if enviar:
                # 1. Validación de campos obligatorios
                if (not Fecha or not Dia or Lugar.strip() == "" or not ID_Grupo):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar reunión - USANDO "REUNION"
                        sql_query = """
                            INSERT INTO REUNION (Fecha, Dia, Lugar, ID_Grupo, ID_Asistencia) 
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            Fecha,
                            str(Dia),
                            str(Lugar),
                            int(ID_Grupo),
                            int(ID_Asistencia) if ID_Asistencia else None
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Reunión registrada correctamente: {Fecha} - {Dia}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la reunión en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar reuniones existentes
def mostrar_lista_reuniones():
    st.header("📋 Lista de Reuniones")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todas las reuniones con información relacionada
        cursor.execute("""
            SELECT r.ID_Reunion, r.Fecha, r.Dia, r.Lugar, r.ID_Grupo, r.ID_Asistencia,
                   g.Nombre as Grupo_Nombre,
                   a.Dui as Asistencia_Dui, m.Nombre as Miembro_Nombre, m.Apellido as Miembro_Apellido
            FROM REUNION r
            LEFT JOIN GRUPOS g ON r.ID_Grupo = g.ID_Grupo
            LEFT JOIN ASISTENCIA a ON r.ID_Asistencia = a.ID_Asistencia
            LEFT JOIN Miembro m ON a.Dui = m.Dui
            ORDER BY r.Fecha DESC, r.ID_Reunion DESC
        """)
        
        reuniones = cursor.fetchall()
        
        if reuniones:
            # Mostrar las reuniones en una lista expandible
            st.subheader("Reuniones Registradas")
            
            for reunion in reuniones:
                with st.expander(f"📅 {reunion[2]} - {reunion[1]} - {reunion[6]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Reunión:** {reunion[0]}")
                        st.write(f"**Fecha:** {reunion[1]}")
                        st.write(f"**Día:** {reunion[2]}")
                        st.write(f"**Lugar:** {reunion[3]}")
                        st.write(f"**ID Grupo:** {reunion[4]}")
                        st.write(f"**Grupo:** {reunion[6]}")
                    
                    with col2:
                        if reunion[5]:  # Si hay asistencia relacionada
                            st.write(f"**ID Asistencia:** {reunion[5]}")
                            st.write(f"**DUI Miembro:** {reunion[7]}")
                            if reunion[8] and reunion[9]:
                                st.write(f"**Miembro Asistencia:** {reunion[8]} {reunion[9]}")
                            else:
                                st.write("**Miembro Asistencia:** No disponible")
                        else:
                            st.write("**Asistencia Extraordinaria:** No asignada")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{reunion[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("👥 Asistencia", key=f"asistencia_{reunion[0]}"):
                            st.info("📊 Funcionalidad de gestión de asistencia en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{reunion[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay reuniones registradas aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de reuniones: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar reuniones
def buscar_reuniones():
    st.header("🔍 Buscar Reuniones")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Buscar por día
            dia_options = ["Todos"] + ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            dia_busqueda = st.selectbox("Día", dia_options)
        
        with col2:
            fecha_desde = st.date_input("Fecha desde")
        
        with col3:
            fecha_hasta = st.date_input("Fecha hasta")
        
        # Buscar por grupo
        cursor.execute("SELECT ID_Grupo, Nombre FROM GRUPOS")
        grupos = cursor.fetchall()
        grupo_options = {f"{grupo[1]}": grupo[0] for grupo in grupos}
        grupo_busqueda = st.selectbox("Grupo", ["Todos"] + list(grupo_options.keys()))
        
        buscar = st.button("🔍 Buscar Reuniones")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT r.ID_Reunion, r.Fecha, r.Dia, r.Lugar, 
                       g.Nombre as Grupo_Nombre
                FROM REUNION r
                LEFT JOIN GRUPOS g ON r.ID_Grupo = g.ID_Grupo
                WHERE 1=1
            """
            params = []
            
            if dia_busqueda != "Todos":
                query += " AND r.Dia = %s"
                params.append(dia_busqueda)
            
            if fecha_desde:
                query += " AND r.Fecha >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND r.Fecha <= %s"
                params.append(fecha_hasta)
            
            if grupo_busqueda != "Todos":
                query += " AND r.ID_Grupo = %s"
                params.append(grupo_options[grupo_busqueda])
            
            query += " ORDER BY r.Fecha DESC"
            
            cursor.execute(query, params)
            reuniones_encontradas = cursor.fetchall()
            
            if reuniones_encontradas:
                st.success(f"✅ Se encontraron {len(reuniones_encontradas)} reunión(es)")
                
                for reunion in reuniones_encontradas:
                    with st.expander(f"📅 {reunion[2]} - {reunion[1]} - {reunion[4]}"):
                        st.write(f"**ID:** {reunion[0]} | **Lugar:** {reunion[3]}")
                        st.write(f"**Grupo:** {reunion[4]}")
            else:
                st.warning("🔍 No se encontraron reuniones con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para calendario de reuniones
def calendario_reuniones():
    st.header("📅 Calendario de Reuniones")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener reuniones de los próximos 30 días
        cursor.execute("""
            SELECT r.Fecha, r.Dia, r.Lugar, g.Nombre as Grupo_Nombre
            FROM REUNION r
            LEFT JOIN GRUPOS g ON r.ID_Grupo = g.ID_Grupo
            WHERE r.Fecha >= CURDATE() AND r.Fecha <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            ORDER BY r.Fecha
        """)
        
        reuniones_proximas = cursor.fetchall()
        
        if reuniones_proximas:
            st.subheader("Próximas Reuniones (30 días)")
            
            for reunion in reuniones_proximas:
                st.write(f"**📅 {reunion[0]} - {reunion[1]}**")
                st.write(f"**Grupo:** {reunion[3]} | **Lugar:** {reunion[2]}")
                st.write("---")
        else:
            st.info("📅 No hay reuniones programadas para los próximos 30 días.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar el calendario: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_reuniones():
    """
    Función principal para gestionar reuniones
    """
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Registrar Reunión", "📋 Ver Reuniones", "🔍 Buscar Reuniones", "📅 Calendario"])
    
    with tab1:
        mostrar_reunion()
    
    with tab2:
        mostrar_lista_reuniones()
    
    with tab3:
        buscar_reuniones()
    
    with tab4:
        calendario_reuniones()