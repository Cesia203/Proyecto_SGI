import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_asistencia():
    st.header("📊 Registrar Asistencia")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener miembros disponibles para el campo FK
        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()

        # Obtener multas disponibles para el campo FK
        cursor.execute("SELECT ID_Multa, Tipo, Monto FROM MULTA WHERE Estado = 'Pendiente'")
        multas = cursor.fetchall()

        # Formulario para registrar asistencia
        with st.form("form_asistencia"):
            # Campo FK para Dui (miembro)
            if miembros:
                miembro_options = {f"{miembro[1]} {miembro[2]} (DUI: {miembro[0]})": miembro[0] for miembro in miembros}
                miembro_seleccionado = st.selectbox("Miembro*", list(miembro_options.keys()))
                Dui = miembro_options[miembro_seleccionado]
            else:
                st.warning("No hay miembros activos disponibles. Debe crear un miembro primero.")
                Dui = None
            
            # Campo para Presente/Ausente
            estado_options = ["Presente", "Ausente"]
            Presente_Ausente = st.selectbox("Estado*", estado_options)
            
            # Campo para Motivo (solo visible si está ausente)
            Motivo = None
            if Presente_Ausente == "Ausente":
                Motivo = st.text_area("Motivo de la ausencia", placeholder="Ingrese el motivo de la ausencia...")
            
            # Campo FK para ID_Multa (opcional, solo si aplica)
            if multas:
                multa_options = {f"Multa {multa[0]}: {multa[1]} - ${multa[2]:.2f}": multa[0] for multa in multas}
                multa_options["Ninguna"] = None
                multa_seleccionada = st.selectbox("Multa aplicada", list(multa_options.keys()))
                ID_Multa = multa_options[multa_seleccionada]
            else:
                st.info("No hay multas pendientes disponibles")
                ID_Multa = None
            
            enviar = st.form_submit_button("✅ Registrar Asistencia")

            if enviar:
                # 1. Validación de campos obligatorios
                if not Dui or not Presente_Ausente:
                    st.warning("⚠️ Debes seleccionar un Miembro y el Estado de asistencia.")
                else:
                    try:
                        # 2. Sentencia SQL para insertar asistencia - USANDO "ASISTENCIA"
                        sql_query = """
                            INSERT INTO ASISTENCIA (Dui, Presente_Ausente, Motivo, ID_Multa) 
                            VALUES (%s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            int(Dui),
                            str(Presente_Ausente),
                            str(Motivo) if Motivo and Motivo.strip() != "" else None,
                            int(ID_Multa) if ID_Multa else None
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        estado_msg = "presente" if Presente_Ausente == "Presente" else "ausente"
                        st.success(f"✅ Asistencia registrada correctamente: Miembro marcado como {estado_msg}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la asistencia en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar asistencias existentes
def mostrar_lista_asistencias():
    st.header("📋 Lista de Asistencias")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todas las asistencias con información del miembro y multa
        cursor.execute("""
            SELECT a.ID_Asistencia, a.Dui, a.Presente_Ausente, a.Motivo, a.ID_Multa,
                   m.Nombre, m.Apellido, 
                   mul.Tipo as Tipo_Multa, mul.Monto as Monto_Multa
            FROM ASISTENCIA a
            LEFT JOIN Miembro m ON a.Dui = m.Dui
            LEFT JOIN MULTA mul ON a.ID_Multa = mul.ID_Multa
            ORDER BY a.ID_Asistencia DESC
        """)
        
        asistencias = cursor.fetchall()
        
        if asistencias:
            # Mostrar las asistencias en una lista expandible
            st.subheader("Registros de Asistencia")
            
            for asistencia in asistencias:
                color_icono = "✅" if asistencia[2] == "Presente" else "❌"
                with st.expander(f"{color_icono} {asistencia[5]} {asistencia[6]} - {asistencia[2]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Asistencia:** {asistencia[0]}")
                        st.write(f"**Estado:** {asistencia[2]}")
                        st.write(f"**Miembro:** {asistencia[5]} {asistencia[6]}")
                        st.write(f"**DUI:** {asistencia[1]}")
                        
                        if asistencia[4]:  # Si hay multa aplicada
                            st.write(f"**Multa aplicada:** {asistencia[7]} - ${asistencia[8]:.2f}")
                        else:
                            st.write("**Multa aplicada:** Ninguna")
                    
                    with col2:
                        if asistencia[3]:  # Si hay motivo
                            st.write("**Motivo:**")
                            st.write(asistencia[3])
                        else:
                            st.write("**Motivo:** No especificado")
                    
                    # Botones de acción
                    col_act1, col_act2 = st.columns(2)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{asistencia[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{asistencia[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay registros de asistencia aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de asistencias: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar asistencias
def buscar_asistencias():
    st.header("🔍 Buscar Asistencias")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2 = st.columns(2)
        
        with col1:
            estado_busqueda = st.selectbox("Estado", ["Todos"] + ["Presente", "Ausente"])
        
        with col2:
            # Buscar por miembro
            cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
            miembros = cursor.fetchall()
            miembro_options = {f"{miembro[1]} {miembro[2]}": miembro[0] for miembro in miembros}
            miembro_busqueda = st.selectbox("Miembro", ["Todos"] + list(miembro_options.keys()))
        
        # Buscar por multa aplicada
        cursor.execute("SELECT ID_Multa, Tipo FROM MULTA")
        multas = cursor.fetchall()
        multa_options = {f"Multa {multa[0]}: {multa[1]}": multa[0] for multa in multas}
        multa_busqueda = st.selectbox("Multa aplicada", ["Todas"] + list(multa_options.keys()))
        
        buscar = st.button("🔍 Buscar Asistencias")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT a.ID_Asistencia, a.Dui, a.Presente_Ausente, a.Motivo, a.ID_Multa,
                       m.Nombre, m.Apellido, 
                       mul.Tipo as Tipo_Multa, mul.Monto as Monto_Multa
                FROM ASISTENCIA a
                LEFT JOIN Miembro m ON a.Dui = m.Dui
                LEFT JOIN MULTA mul ON a.ID_Multa = mul.ID_Multa
                WHERE 1=1
            """
            params = []
            
            if estado_busqueda != "Todos":
                query += " AND a.Presente_Ausente = %s"
                params.append(estado_busqueda)
            
            if miembro_busqueda != "Todos":
                query += " AND a.Dui = %s"
                params.append(miembro_options[miembro_busqueda])
            
            if multa_busqueda != "Todas":
                query += " AND a.ID_Multa = %s"
                params.append(multa_options[multa_busqueda])
            elif multa_busqueda == "Todas":
                # Para incluir tanto registros con multa como sin multa
                pass
            
            query += " ORDER BY a.ID_Asistencia DESC"
            
            cursor.execute(query, params)
            asistencias_encontradas = cursor.fetchall()
            
            if asistencias_encontradas:
                st.success(f"✅ Se encontraron {len(asistencias_encontradas)} registro(s) de asistencia")
                
                for asistencia in asistencias_encontradas:
                    color_icono = "✅" if asistencia[2] == "Presente" else "❌"
                    with st.expander(f"{color_icono} {asistencia[5]} {asistencia[6]} - {asistencia[2]}"):
                        st.write(f"**ID:** {asistencia[0]} | **Estado:** {asistencia[2]}")
                        if asistencia[3]:
                            st.write(f"**Motivo:** {asistencia[3]}")
                        if asistencia[4]:
                            st.write(f"**Multa:** {asistencia[7]} - ${asistencia[8]:.2f}")
            else:
                st.warning("🔍 No se encontraron registros de asistencia con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_asistencias():
    """
    Función principal para gestionar asistencias
    """
    tab1, tab2, tab3 = st.tabs(["📊 Registrar Asistencia", "📋 Ver Asistencias", "🔍 Buscar Asistencias"])
    
    with tab1:
        mostrar_asistencia()
    
    with tab2:
        mostrar_lista_asistencias()
    
    with tab3:
        buscar_asistencias()