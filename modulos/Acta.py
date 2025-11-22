import streamlit as st
from modulos.config.conexion import obtener_conexion

def Acta():
    st.header("📄 Registrar Acta")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener ciclos disponibles para el campo FK - USANDO "CICLO"
        cursor.execute("SELECT ID_Ciclo, Fecha_inicio, Fecha_fin FROM CICLO WHERE Estado = 'Activo'")
        ciclos = cursor.fetchall()

        # Formulario para registrar acta
        with st.form("form_acta"):
            # Variables del formulario
            Tipo = st.selectbox("Tipo de Acta*", ["Reunión", "Asamblea", "Decisión", "Otro"])
            Fecha = st.date_input("Fecha del Acta*")
            
            # Campo para Contenido (área de texto más grande)
            Contenido = st.text_area("Contenido*", height=200, 
                                   placeholder="Ingrese el contenido completo del acta...")
            
            # Campo FK para ID_Ciclo
            if ciclos:
                ciclo_options = {f"Ciclo {ciclo[0]}: {ciclo[1]} a {ciclo[2]}": ciclo[0] for ciclo in ciclos}
                ciclo_seleccionado = st.selectbox("Ciclo*", list(ciclo_options.keys()))
                ID_Ciclo = ciclo_options[ciclo_seleccionado]
            else:
                st.warning("No hay ciclos activos disponibles. Debe crear un ciclo primero.")
                ID_Ciclo = None
            
            enviar = st.form_submit_button("✅ Registrar Acta")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Tipo.strip() == "" or not Fecha or 
                    Contenido.strip() == "" or not ID_Ciclo):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar acta - USANDO "ACTA"
                        sql_query = """
                            INSERT INTO ACTA (Tipo, Fecha, Contenido, ID_Ciclo) 
                            VALUES (%s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            str(Tipo),
                            Fecha,
                            str(Contenido),
                            int(ID_Ciclo)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Acta registrada correctamente: {Tipo} - {Fecha}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el acta en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar actas existentes
def mostrar_lista_actas():
    st.header("📋 Lista de Actas")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todas las actas con información del ciclo - USANDO "ACTA" y "CICLO"
        cursor.execute("""
            SELECT a.ID_Acta, a.Tipo, a.Fecha, a.Contenido, 
                   c.ID_Ciclo, c.Fecha_inicio, c.Fecha_fin
            FROM ACTA a
            LEFT JOIN CICLO c ON a.ID_Ciclo = c.ID_Ciclo
            ORDER BY a.Fecha DESC, a.ID_Acta DESC
        """)
        
        actas = cursor.fetchall()
        
        if actas:
            # Mostrar las actas en una lista expandible
            st.subheader("Actas Registradas")
          for acta in actas:
                # Crear un resumen del contenido (primeros 100 caracteres)
                contenido_resumen = acta[3][:100] + "..." if len(acta[3]) > 100 else acta[3]
                
                with st.expander(f"📄 {acta[1]} - {acta[2]} (Ciclo: {acta[4]})"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Acta:** {acta[0]}")
                        st.write(f"**Tipo:** {acta[1]}")
                        st.write(f"**Fecha:** {acta[2]}")
                        st.write(f"**Ciclo:** {acta[4]}")
                        st.write(f"**Periodo Ciclo:** {acta[5]} a {acta[6]}")
                    
                    with col2:
                        st.write("**Contenido:**")
                        st.write(acta[3])
# Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{acta[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("👁️ Ver Completo", key=f"ver_{acta[0]}"):
                            # Mostrar contenido completo en un modal
                            with st.expander("📖 Contenido Completo del Acta", expanded=True):
                                st.text_area("Contenido", acta[3], height=300, key=f"contenido_{acta[0]}")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{acta[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay actas registradas aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de actas: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()
          # Función para buscar actas
def buscar_actas():
    st.header("🔍 Buscar Actas")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_busqueda = st.selectbox("Tipo", ["Todos"] + ["Reunión", "Asamblea", "Decisión", "Otro"])
        
        with col2:
            fecha_inicio = st.date_input("Fecha desde")
        
        with col3:
            fecha_fin = st.date_input("Fecha hasta")
        
        buscar = st.button("🔍 Buscar Actas")
        
        if buscar:
            # Construir consulta dinámica - USANDO "ACTA" y "CICLO"
            query = """
                SELECT a.ID_Acta, a.Tipo, a.Fecha, a.Contenido, 
                       c.ID_Ciclo, c.Fecha_inicio, c.Fecha_fin
                FROM ACTA a
                LEFT JOIN CICLO c ON a.ID_Ciclo = c.ID_Ciclo
                WHERE 1=1
            """
            params = []
            
            if tipo_busqueda != "Todos":
                query += " AND a.Tipo = %s"
                params.append(tipo_busqueda)
            
            if fecha_inicio:
                query += " AND a.Fecha >= %s"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND a.Fecha <= %s"
                params.append(fecha_fin)
            
            query += " ORDER BY a.Fecha DESC"
            
            cursor.execute(query, params)
            actas_encontradas = cursor.fetchall()
            
            if actas_encontradas:
                st.success(f"✅ Se encontraron {len(actas_encontradas)} acta(s)")
                
                for acta in actas_encontradas:
                    with st.expander(f"📄 {acta[1]} - {acta[2]}"):
                        st.write(f"**ID:** {acta[0]} | **Ciclo:** {acta[4]}")
                        st.write("**Contenido:**")
                        st.write(acta[3][:500] + "..." if len(acta[3]) > 500 else acta[3])
            else:
                st.warning("🔍 No se encontraron actas con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_actas():
    """
    Función principal para gestionar actas
    """
    tab1, tab2, tab3 = st.tabs(["📝 Registrar Nueva Acta", "📋 Ver Actas Existentes", "🔍 Buscar Actas"])
    
    with tab1:
        mostrar_acta()
    
    with tab2:
        mostrar_lista_actas()
    
    with tab3:
        buscar_actas()
