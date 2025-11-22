import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import date

def reunion():
    st.header("📅 Registrar Reunión")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # 1. Obtener lista de distritos únicos desde la tabla GRUPOS (asumimos que existe esta columna)
        cursor.execute("SELECT DISTINCT Distrito FROM GRUPOS WHERE Distrito IS NOT NULL AND Distrito != '' ORDER BY Distrito")
        distritos = [d[0] for d in cursor.fetchall()]

        # 2. Obtener TODA la información de grupos para filtrado dinámico
        cursor.execute("SELECT ID_Grupo, Nombre, Distrito FROM GRUPOS WHERE Estado = 'Activo'")
        all_grupos = cursor.fetchall()

        # Obtener asistencias disponibles para el campo FK (se mantiene el original)
        cursor.execute("SELECT ID_Asistencia, Dui FROM ASISTENCIA")
        asistencias = cursor.fetchall()

        # Formulario para registrar reunión
        with st.form("form_reunion"):
            # Campos principales
            Fecha = st.date_input("Fecha de la Reunión*", value=date.today())
            
            # Campo para Día
            dia_options = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            Dia = st.selectbox("Día de la Reunión*", dia_options)
            
            # --- CAMBIO 1: Lugar cambiado a Distrito ---
            Distrito = None
            if distritos:
                Distrito = st.selectbox("Distrito*", ["Seleccione un Distrito"] + distritos)
            else:
                st.warning("No se encontraron distritos en la DB para filtrar grupos. Ingrese el distrito manualmente.")
                Distrito = st.text_input("Distrito*")
                

            # --- CAMBIO 2: Grupo dinámico basado en Distrito ---
            ID_Grupo = None
            if Distrito and Distrito != "Seleccione un Distrito":
                # Filtrar grupos basados en el distrito seleccionado
                grupos_filtrados = [g for g in all_grupos if g[2] == Distrito]
                
                if grupos_filtrados:
                    grupo_options = {f"{grupo[1]} (ID: {grupo[0]})": grupo[0] for grupo in grupos_filtrados}
                    grupo_seleccionado = st.selectbox("Grupo*", list(grupo_options.keys()))
                    ID_Grupo = grupo_options[grupo_seleccionado]
                else:
                    st.info(f"No hay grupos activos disponibles en el distrito: {Distrito}")
            elif Distrito == "Seleccione un Distrito":
                 st.info("Seleccione un Distrito para cargar los Grupos.")
            
            # --- CAMBIO 3: Opción de cantidad de miembros ---
            num_miembros = st.number_input("Cantidad de Miembros que Asisten*", min_value=0, max_value=50, step=1, key="num_miembros_input")
            miembros_asistencia = []

            # --- CAMBIO 4: Desplegar lista de ID de Miembros ---
            if num_miembros > 0:
                st.subheader(f"DUI/ID de los {int(num_miembros)} Miembros")
                for i in range(int(num_miembros)):
                    # Usamos una clave única para cada input
                    member_id = st.text_input(f"DUI/ID del Miembro {i+1}*", key=f"member_id_{i}")
                    miembros_asistencia.append(member_id)

            # Campo FK para ID_Asistencia (Se mantiene la opción individual/extraordinaria)
            if asistencias:
                asistencia_options = {f"Asistencia {asistencia[0]} (DUI: {asistencia[1]})": asistencia[0] for asistencia in asistencias}
                asistencia_options["Ninguna"] = None
                asistencia_seleccionada = st.selectbox("Asistencia Extraordinaria/Ordinaria (Asistencia individual - FK)", list(asistencia_options.keys()))
                ID_Asistencia = asistencia_options[asistencia_seleccionada]
            else:
                st.info("No hay asistencias registradas disponibles")
                ID_Asistencia = None
            
            
            enviar = st.form_submit_button("✅ Registrar Reunión")

            if enviar:
                # 1. Validación de campos obligatorios
                miembros_vacios = [m for m in miembros_asistencia if m.strip() == ""]
                
                # Validación principal
                if (not Fecha or not Dia or not Distrito or Distrito == "Seleccione un Distrito" or not ID_Grupo):
                    st.warning("⚠️ Debes completar los campos de Fecha, Día, Distrito y Grupo obligatorios (*).")
                # Validación de asistencia
                elif num_miembros > 0 and miembros_vacios:
                    st.warning(f"⚠️ Debes ingresar el DUI/ID para los {len(miembros_vacios)} miembros restantes.")
                else:
                    try:
                        # 2. Sentencia SQL corregida: reemplaza 'Lugar' por 'Distrito' en el INSERT
                        # Asumimos que la tabla REUNION tiene ahora la columna 'Distrito'
                        sql_query = """
                            INSERT INTO REUNION (Fecha, Dia, Distrito, ID_Grupo, ID_Asistencia)  
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            Fecha,
                            str(Dia),
                            str(Distrito),  # Ahora usamos la variable Distrito
                            int(ID_Grupo),
                            int(ID_Asistencia) if ID_Asistencia else None
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Manejo de los miembros de asistencia (solo se muestra la lista)
                        miembros_registrados_msg = ""
                        if miembros_asistencia:
                            miembros_registrados_msg = f" (Asistencia capturada: {', '.join(miembros_asistencia)})"
                            # NOTA: En una implementación completa, aquí se insertaría esta lista en una tabla de Asistencia_Miembros
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Reunión registrada correctamente: {Fecha} - {Dia}. Distrito: {Distrito}{miembros_registrados_msg}")
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

# Función para mostrar reuniones existentes (actualizada para mostrar Distrito)
def mostrar_lista_reuniones():
    st.header("📋 Lista de Reuniones")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todas las reuniones con información relacionada (cambiado r.Lugar a r.Distrito)
        cursor.execute("""
            SELECT r.ID_Reunion, r.Fecha, r.Dia, r.Distrito, r.ID_Grupo, r.ID_Asistencia,
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
                # El índice 3 ahora es Distrito (antes Lugar)
                with st.expander(f"📅 {reunion[2]} - {reunion[1]} - {reunion[6]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Reunión:** {reunion[0]}")
                        st.write(f"**Fecha:** {reunion[1]}")
                        st.write(f"**Día:** {reunion[2]}")
                        st.write(f"**Distrito:** {reunion[3]}") # CAMBIO
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

# Función para buscar reuniones (actualizada para buscar y mostrar Distrito)
def buscar_reuniones():
    st.header("🔍 Buscar Reuniones")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        # Obtener lista de distritos para búsqueda
        cursor.execute("SELECT DISTINCT Distrito FROM GRUPOS WHERE Distrito IS NOT NULL AND Distrito != '' ORDER BY Distrito")
        distritos_busqueda = [d[0] for d in cursor.fetchall()]

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

        # Nuevo campo de búsqueda por Distrito
        distrito_busqueda = st.selectbox("Distrito", ["Todos"] + distritos_busqueda)
        
        buscar = st.button("🔍 Buscar Reuniones")
        
        if buscar:
            # Construir consulta dinámica (cambiado r.Lugar a r.Distrito)
            query = """
                SELECT r.ID_Reunion, r.Fecha, r.Dia, r.Distrito,  
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

            # Nuevo filtro por Distrito
            if distrito_busqueda != "Todos":
                query += " AND r.Distrito = %s"
                params.append(distrito_busqueda)
            
            query += " ORDER BY r.Fecha DESC"
            
            cursor.execute(query, params)
            reuniones_encontradas = cursor.fetchall()
            
            if reuniones_encontradas:
                st.success(f"✅ Se encontraron {len(reuniones_encontradas)} reunión(es)")
                
                for reunion in reuniones_encontradas:
                    # El índice 3 ahora es Distrito
                    with st.expander(f"📅 {reunion[2]} - {reunion[1]} - {reunion[4]}"):
                        st.write(f"**ID:** {reunion[0]} | **Distrito:** {reunion[3]}") # CAMBIO
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

# Función para calendario de reuniones (actualizada para mostrar Distrito)
def calendario_reuniones():
    st.header("📅 Calendario de Reuniones")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener reuniones de los próximos 30 días (cambiado r.Lugar a r.Distrito)
        cursor.execute("""
            SELECT r.Fecha, r.Dia, r.Distrito, g.Nombre as Grupo_Nombre
            FROM REUNION r
            LEFT JOIN GRUPOS g ON r.ID_Grupo = g.ID_Grupo
            WHERE r.Fecha >= CURDATE() AND r.Fecha <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
            ORDER BY r.Fecha
        """)
        
        reuniones_proximas = cursor.fetchall()
        
        if reuniones_proximas:
            st.subheader("Próximas Reuniones (30 días)")
            
            for reunion in reuniones_proximas:
                # El índice 2 ahora es Distrito
                st.write(f"**📅 {reunion[0]} - {reunion[1]}**")
                st.write(f"**Grupo:** {reunion[3]} | **Distrito:** {reunion[2]}") # CAMBIO
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
