import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_grupo():
    st.header("👥 Registrar Grupo")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener datos para los campos FK
        cursor.execute("SELECT ID_Ciclo, Fecha_inicio, Fecha_fin FROM CICLO WHERE Estado = 'Activo'")
        ciclos = cursor.fetchall()

        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()

        cursor.execute("SELECT ID_Admin, Nombre FROM ADMINISTRADOR WHERE Estado = 'Activo'")
        administradores = cursor.fetchall()

        cursor.execute("SELECT ID_Promotora, Nombre FROM PROMOTORA WHERE Estado = 'Activo'")
        promotoras = cursor.fetchall()

        # Formulario para registrar grupo
        with st.form("form_grupo"):
            # Campos principales
            Nombre = st.text_input("Nombre del Grupo*")
            Fecha_inicio = st.date_input("Fecha de Inicio*")
            Tasa_interes = st.number_input("Tasa de Interés (%)*", min_value=0.0, max_value=100.0, step=0.1)
            
            # Campo para Tipo de multa
            tipo_multa_options = ["Fijo", "Porcentaje", "Ninguna"]
            Tipo_multa = st.selectbox("Tipo de Multa*", tipo_multa_options)
            
            # Campo para Frecuencia de reuniones
            frecuencia_options = ["Diaria", "Semanal", "Quincenal", "Mensual"]
            Frecuencia_reuniones = st.selectbox("Frecuencia de Reuniones*", frecuencia_options)
            
            # Campos FK
            # ID_Ciclo
            if ciclos:
                ciclo_options = {f"Ciclo {ciclo[0]}: {ciclo[1]} a {ciclo[2]}": ciclo[0] for ciclo in ciclos}
                ciclo_seleccionado = st.selectbox("Ciclo*", list(ciclo_options.keys()))
                ID_ciclo = ciclo_options[ciclo_seleccionado]
            else:
                st.warning("No hay ciclos activos disponibles")
                ID_ciclo = None
            
            # Dui (miembro)
            if miembros:
                miembro_options = {f"{miembro[1]} {miembro[2]} (DUI: {miembro[0]})": miembro[0] for miembro in miembros}
                miembro_seleccionado = st.selectbox("Líder del Grupo*", list(miembro_options.keys()))
                Dui = miembro_options[miembro_seleccionado]
            else:
                st.warning("No hay miembros activos disponibles")
                Dui = None
            
            # ID_Admin
            if administradores:
                admin_options = {f"{admin[1]}": admin[0] for admin in administradores}
                admin_seleccionado = st.selectbox("Administrador*", list(admin_options.keys()))
                ID_Admin = admin_options[admin_seleccionado]
            else:
                st.warning("No hay administradores activos disponibles")
                ID_Admin = None
            
            # ID_Promotora
            if promotoras:
                promotora_options = {f"{promotora[1]}": promotora[0] for promotora in promotoras}
                promotora_seleccionado = st.selectbox("Promotora*", list(promotora_options.keys()))
                ID_Promotora = promotora_options[promotora_seleccionado]
            else:
                st.warning("No hay promotoras activas disponibles")
                ID_Promotora = None
            
            # Campos adicionales
            Politicas_prestamo = st.text_area("Políticas de Préstamo")
            
            estado_options = ["Activo", "Inactivo", "Suspendido", "Finalizado"]
            Estado = st.selectbox("Estado*", estado_options)
            
            enviar = st.form_submit_button("✅ Registrar Grupo")
            
            if enviar:
                # Validación de campos obligatorios
                if (Nombre.strip() == "" or not Fecha_inicio or 
                    Tasa_interes is None or not ID_ciclo or 
                    not Dui or not ID_Admin or not ID_Promotora):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # Sentencia SQL para insertar el grupo
                        sql_query = """
                        INSERT INTO GRUPOS (
                            Nombre, Fecha_inicio, Tasa_interes, Tipo_multa, 
                            Frecuencia_reuniones, ID_ciclo, Dui, 
                            Politicas_prestamo, Estado, ID_Admin, ID_Promotora
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        # Tupla de valores
                        values = (
                            str(Nombre),
                            Fecha_inicio,
                            float(Tasa_interes),
                            str(Tipo_multa),
                            str(Frecuencia_reuniones),
                            int(ID_ciclo),
                            int(Dui),
                            str(Politicas_prestamo) if Politicas_prestamo else None,
                            str(Estado),
                            int(ID_Admin),
                            int(ID_Promotora)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito
                        st.success(f"✅ Grupo registrado correctamente: {Nombre}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el grupo en la base de datos: {e}")
                        
    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")
    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar grupos existentes
def mostrar_lista_grupos():
    st.header("📋 Lista de Grupos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        # Consulta para obtener todos los grupos con información relacionada
        cursor.execute("""
            SELECT g.ID_Grupo, g.Nombre, g.Fecha_inicio, g.Tasa_interes, g.Tipo_multa,
                   g.Frecuencia_reuniones, g.Politicas_prestamo, g.Estado,
                   c.ID_Ciclo, c.Fecha_inicio as Ciclo_inicio, c.Fecha_fin as Ciclo_fin,
                   m.Dui, m.Nombre as Miembro_Nombre, m.Apellido as Miembro_Apellido,
                   a.ID_Admin, a.Nombre as Admin_Nombre,
                   p.ID_Promotora, p.Nombre as Promotora_Nombre
            FROM GRUPOS g
            LEFT JOIN CICLO c ON g.ID_ciclo = c.ID_Ciclo
            LEFT JOIN Miembro m ON g.Dui = m.Dui
            LEFT JOIN ADMINISTRADOR a ON g.ID_Admin = a.ID_Admin
            LEFT JOIN PROMOTORA p ON g.ID_Promotora = p.ID_Promotora
            ORDER BY g.Fecha_inicio DESC
        """)
        
        grupos = cursor.fetchall()
        
        if grupos:
            # Mostrar los grupos en una tabla
            st.subheader("Grupos Registrados")
            for grupo in grupos:
                with st.expander(f"👥 {grupo[1]} - {grupo[7]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID Grupo:** {grupo[0]}")
                        st.write(f"**Fecha de Inicio:** {grupo[2]}")
                        st.write(f"**Tasa de Interés:** {grupo[3]}%")
                        st.write(f"**Tipo de Multa:** {grupo[4]}")
                        st.write(f"**Frecuencia Reuniones:** {grupo[5]}")
                        st.write(f"**Estado:** {grupo[7]}")
                    
                    with col2:
                        st.write(f"**Ciclo:** {grupo[8]} ({grupo[9]} a {grupo[10]})")
                        st.write(f"**Líder:** {grupo[12]} {grupo[13]}")
                        st.write(f"**DUI Líder:** {grupo[11]}")
                        st.write(f"**Administrador:** {grupo[15]}")
                        st.write(f"**Promotora:** {grupo[17]}")
                    
                    # Mostrar políticas de préstamo si existen
                    if grupo[6]:
                        st.write("**Políticas de Préstamo:**")
                        st.write(grupo[6])
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{grupo[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("👥 Miembros", key=f"miembros_{grupo[0]}"):
                            st.info("👥 Funcionalidad de gestión de miembros en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{grupo[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay grupos registrados aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de grupos: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar grupos
def buscar_grupos():
    st.header("🔍 Buscar Grupos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estado_busqueda = st.selectbox("Estado", ["Todos"] + ["Activo", "Inactivo", "Suspendido", "Finalizado"])
        
        with col2:
            # Buscar por ciclo
            cursor.execute("SELECT ID_Ciclo, Fecha_inicio FROM CICLO")
            ciclos = cursor.fetchall()
            ciclo_options = {f"Ciclo {ciclo[0]}": ciclo[0] for ciclo in ciclos}
            ciclo_busqueda = st.selectbox("Ciclo", ["Todos"] + list(ciclo_options.keys()))
        
        with col3:
            # Buscar por líder
            cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro")
            miembros = cursor.fetchall()
            miembro_options = {f"{miembro[1]} {miembro[2]}": miembro[0] for miembro in miembros}
            miembro_busqueda = st.selectbox("Líder", ["Todos"] + list(miembro_options.keys()))
        
        buscar = st.button("🔍 Buscar Grupos")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT g.ID_Grupo, g.Nombre, g.Fecha_inicio, g.Tasa_interes, g.Estado,
                       c.ID_Ciclo, m.Nombre as Lider_Nombre, m.Apellido as Lider_Apellido
                FROM GRUPOS g
                LEFT JOIN CICLO c ON g.ID_ciclo = c.ID_Ciclo
                LEFT JOIN Miembro m ON g.Dui = m.Dui
                WHERE 1=1
            """
            params = []
            
            if estado_busqueda != "Todos":
                query += " AND g.Estado = %s"
                params.append(estado_busqueda)
            
            if ciclo_busqueda != "Todos":
                query += " AND g.ID_ciclo = %s"
                params.append(ciclo_options[ciclo_busqueda])
            
            if miembro_busqueda != "Todos":
                query += " AND g.Dui = %s"
                params.append(miembro_options[miembro_busqueda])
            
            query += " ORDER BY g.Nombre"
            
            cursor.execute(query, params)
            grupos_encontrados = cursor.fetchall()
            
            if grupos_encontrados:
                st.success(f"✅ Se encontraron {len(grupos_encontrados)} grupo(s)")
                
                for grupo in grupos_encontrados:
                    with st.expander(f"👥 {grupo[1]} - {grupo[4]}"):
                        st.write(f"**ID:** {grupo[0]} | **Tasa Interés:** {grupo[3]}%")
                        st.write(f"**Fecha Inicio:** {grupo[2]} | **Ciclo:** {grupo[5]}")
                        st.write(f"**Líder:** {grupo[6]} {grupo[7]}")
            else:
                st.warning("🔍 No se encontraron grupos con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_grupos():
    """
    Función principal para gestionar grupos
    """
    tab1, tab2, tab3 = st.tabs(["👥 Registrar Grupo", "📋 Ver Grupos", "🔍 Buscar Grupos"])
    
    with tab1:
        mostrar_grupo()
    
    with tab2:
        mostrar_lista_grupos()
    
    with tab3:
        buscar_grupos()