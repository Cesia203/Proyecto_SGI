import streamlit as st
from modulos.config.conexion import obtener_conexion

def Directiva():
    st.header("👑 Registrar Directiva")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener grupos disponibles para el campo FK
        cursor.execute("SELECT ID_Grupo, Nombre FROM GRUPOS WHERE Estado = 'Activo'")
        grupos = cursor.fetchall()

        # Formulario para registrar directiva
        with st.form("form_directiva"):
            # Campos principales
            Fecha_inicio = st.date_input("Fecha de Inicio*")
            Fecha_fin = st.date_input("Fecha de Fin*")
            
            # Campo para Estado
            estado_options = ["Activa", "Inactiva"]
            Estado = st.selectbox("Estado*", estado_options)
            
            # Campo FK para ID_Grupo
            if grupos:
                grupo_options = {f"{grupo[1]} (ID: {grupo[0]})": grupo[0] for grupo in grupos}
                grupo_seleccionado = st.selectbox("Grupo*", list(grupo_options.keys()))
                ID_Grupo = grupo_options[grupo_seleccionado]
            else:
                st.warning("No hay grupos activos disponibles. Debe crear un grupo primero.")
                ID_Grupo = None
            
            enviar = st.form_submit_button("✅ Registrar Directiva")

            if enviar:
                # 1. Validación de campos obligatorios
                if (not Fecha_inicio or not Fecha_fin or 
                    Estado.strip() == "" or not ID_Grupo):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                
                # 2. Validación de fechas
                elif Fecha_inicio >= Fecha_fin:
                    st.warning("⚠️ La Fecha de Fin debe ser posterior a la Fecha de Inicio.")
                
                else:
                    try:
                        # 3. Sentencia SQL para insertar directiva - USANDO "DIRECTIVA"
                        sql_query = """
                            INSERT INTO DIRECTIVA (Fecha_inicio, Fecha_fin, Estado, ID_Grupo) 
                            VALUES (%s, %s, %s, %s)
                        """
                        
                        # 4. Tupla de valores
                        values = (
                            Fecha_inicio,
                            Fecha_fin,
                            str(Estado),
                            int(ID_Grupo)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Directiva registrada correctamente: {Fecha_inicio} a {Fecha_fin}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la directiva en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar directivas existentes
def mostrar_lista_directivas():
    st.header("📋 Lista de Directivas")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todas las directivas con información del grupo
        cursor.execute("""
            SELECT d.ID_Directiva, d.Fecha_inicio, d.Fecha_fin, d.Estado, d.ID_Grupo,
                   g.Nombre as Grupo_Nombre
            FROM DIRECTIVA d
            LEFT JOIN GRUPOS g ON d.ID_Grupo = g.ID_Grupo
            ORDER BY d.Fecha_inicio DESC, d.ID_Directiva DESC
        """)
        
        directivas = cursor.fetchall()
        
        if directivas:
            # Mostrar las directivas en una lista expandible
            st.subheader("Directivas Registradas")
            
            for directiva in directivas:
                estado_icono = "🟢" if directiva[3] == "Activa" else "🔴"
                with st.expander(f"{estado_icono} {directiva[5]} - {directiva[1]} a {directiva[2]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Directiva:** {directiva[0]}")
                        st.write(f"**Fecha Inicio:** {directiva[1]}")
                        st.write(f"**Fecha Fin:** {directiva[2]}")
                        st.write(f"**Estado:** {directiva[3]}")
                        st.write(f"**ID Grupo:** {directiva[4]}")
                    
                    with col2:
                        st.write(f"**Grupo:** {directiva[5]}")
                        
                        # Calcular días restantes si está activa
                        if directiva[3] == "Activa":
                            cursor.execute("SELECT DATEDIFF(%s, CURDATE())", (directiva[2],))
                            dias_restantes = cursor.fetchone()[0]
                            if dias_restantes > 0:
                                st.write(f"**Días restantes:** {dias_restantes} días")
                            elif dias_restantes == 0:
                                st.warning("⚠️ La directiva vence hoy")
                            else:
                                st.error("❌ La directiva está vencida")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{directiva[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if directiva[3] == "Activa":
                            if st.button("🔴 Desactivar", key=f"desactivar_{directiva[0]}"):
                                st.info("🔄 Funcionalidad de cambio de estado en desarrollo...")
                        else:
                            if st.button("🟢 Activar", key=f"activar_{directiva[0]}"):
                                st.info("🔄 Funcionalidad de cambio de estado en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{directiva[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay directivas registradas aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de directivas: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar directivas
def buscar_directivas():
    st.header("🔍 Buscar Directivas")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estado_busqueda = st.selectbox("Estado", ["Todos"] + ["Activa", "Inactiva"])
        
        with col2:
            fecha_desde = st.date_input("Fecha inicio desde")
        
        with col3:
            fecha_hasta = st.date_input("Fecha inicio hasta")
        
        # Buscar por grupo
        cursor.execute("SELECT ID_Grupo, Nombre FROM GRUPOS")
        grupos = cursor.fetchall()
        grupo_options = {f"{grupo[1]}": grupo[0] for grupo in grupos}
        grupo_busqueda = st.selectbox("Grupo", ["Todos"] + list(grupo_options.keys()))
        
        # Filtro por vigencia
        vigencia_options = ["Todos", "Vigentes", "Vencidas", "Por vencer"]
        vigencia_busqueda = st.selectbox("Vigencia", vigencia_options)
        
        buscar = st.button("🔍 Buscar Directivas")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT d.ID_Directiva, d.Fecha_inicio, d.Fecha_fin, d.Estado, 
                       g.Nombre as Grupo_Nombre
                FROM DIRECTIVA d
                LEFT JOIN GRUPOS g ON d.ID_Grupo = g.ID_Grupo
                WHERE 1=1
            """
            params = []
            
            if estado_busqueda != "Todos":
                query += " AND d.Estado = %s"
                params.append(estado_busqueda)
            
            if fecha_desde:
                query += " AND d.Fecha_inicio >= %s"
                params.append(fecha_desde)
            
            if fecha_hasta:
                query += " AND d.Fecha_inicio <= %s"
                params.append(fecha_hasta)
            
            if grupo_busqueda != "Todos":
                query += " AND d.ID_Grupo = %s"
                params.append(grupo_options[grupo_busqueda])
            
            if vigencia_busqueda == "Vigentes":
                query += " AND d.Estado = 'Activa' AND d.Fecha_fin >= CURDATE()"
            elif vigencia_busqueda == "Vencidas":
                query += " AND (d.Estado = 'Inactiva' OR d.Fecha_fin < CURDATE())"
            elif vigencia_busqueda == "Por vencer":
                query += " AND d.Estado = 'Activa' AND d.Fecha_fin BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)"
            
            query += " ORDER BY d.Fecha_inicio DESC"
            
            cursor.execute(query, params)
            directivas_encontradas = cursor.fetchall()
            
            if directivas_encontradas:
                st.success(f"✅ Se encontraron {len(directivas_encontradas)} directiva(s)")
                
                for directiva in directivas_encontradas:
                    estado_icono = "🟢" if directiva[3] == "Activa" else "🔴"
                    with st.expander(f"{estado_icono} {directiva[4]} - {directiva[1]} a {directiva[2]}"):
                        st.write(f"**ID:** {directiva[0]} | **Estado:** {directiva[3]}")
                        st.write(f"**Período:** {directiva[1]} a {directiva[2]}")
            else:
                st.warning("🔍 No se encontraron directivas con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para directivas vigentes
def directivas_vigentes():
    st.header("🟢 Directivas Vigentes")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener directivas activas y vigentes
        cursor.execute("""
            SELECT d.ID_Directiva, d.Fecha_inicio, d.Fecha_fin, d.ID_Grupo,
                   g.Nombre as Grupo_Nombre,
                   DATEDIFF(d.Fecha_fin, CURDATE()) as Dias_restantes
            FROM DIRECTIVA d
            LEFT JOIN GRUPOS g ON d.ID_Grupo = g.ID_Grupo
            WHERE d.Estado = 'Activa' AND d.Fecha_fin >= CURDATE()
            ORDER BY Dias_restantes ASC
        """)
        
        directivas_vigentes = cursor.fetchall()
        
        if directivas_vigentes:
            st.subheader("Directivas Activas y Vigentes")
            
            for directiva in directivas_vigentes:
                # Determinar color según días restantes
                if directiva[5] <= 7:
                    color = "🔴"  # Crítico
                elif directiva[5] <= 30:
                    color = "🟡"  # Advertencia
                else:
                    color = "🟢"  # Normal
                
                with st.expander(f"{color} {directiva[4]} - Vence en {directiva[5]} días"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID Directiva:** {directiva[0]}")
                        st.write(f"**Fecha Inicio:** {directiva[1]}")
                        st.write(f"**Fecha Fin:** {directiva[2]}")
                    
                    with col2:
                        st.write(f"**Grupo:** {directiva[4]}")
                        st.write(f"**ID Grupo:** {directiva[3]}")
                        
                        if directiva[5] <= 7:
                            st.error(f"⏰ **Vence pronto!** ({directiva[5]} días)")
                        elif directiva[5] <= 30:
                            st.warning(f"⚠️ **Vence en** {directiva[5]} días")
                        else:
                            st.success(f"✅ **Vigente** ({directiva[5]} días restantes)")
        else:
            st.info("📭 No hay directivas vigentes en este momento.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar las directivas vigentes: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_directivas():
    """
    Función principal para gestionar directivas
    """
    tab1, tab2, tab3, tab4 = st.tabs(["👑 Registrar Directiva", "📋 Ver Directivas", "🔍 Buscar Directivas", "🟢 Vigentes"])
    
    with tab1:
        mostrar_directiva()
    
    with tab2:
        mostrar_lista_directivas()
    
    with tab3:
        buscar_directivas()
    
    with tab4:
        directivas_vigentes()
