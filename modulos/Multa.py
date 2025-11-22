import streamlit as st
from modulos.config.conexion import obtener_conexion

def Multa():
    st.header("💰 Registrar Multa")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener miembros disponibles para el campo FK
        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()

        # Formulario para registrar multa
        with st.form("form_multa"):
            # Variables del formulario
            Tipo = st.text_input("Tipo de Multa*")
            
            Monto = st.number_input(
                "Monto*", 
                min_value=0.0, 
                step=0.01,
                format="%.2f"
            )
            
            Descripccion = st.text_area("Descripción", placeholder="Ingrese la descripción de la multa...")
            
            Fecha = st.date_input("Fecha de la Multa*")
            
            # Campo para Estado con opciones predefinidas
            estado_options = ["Pendiente", "Pagada", "Cancelada", "Vencida"]
            Estado = st.selectbox("Estado*", estado_options)
            
            # Campo FK para Dui (referencia directa a Miembro)
            if miembros:
                miembro_options = {f"{miembro[1]} {miembro[2]} (DUI: {miembro[0]})": miembro[0] for miembro in miembros}
                miembro_seleccionado = st.selectbox("Miembro*", list(miembro_options.keys()))
                Dui = miembro_options[miembro_seleccionado]
            else:
                st.warning("No hay miembros activos disponibles. Debe crear un miembro primero.")
                Dui = None
            
            enviar = st.form_submit_button("✅ Registrar Multa")

            if enviar:
                # 1. Validación de campos obligatorios
                if (Tipo.strip() == "" or Monto is None or 
                    not Fecha or Estado.strip() == "" or not Dui):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")
                else:
                    try:
                        # 2. Sentencia SQL para insertar multa - USANDO "MULTA" con "Dui"
                        sql_query = """
                            INSERT INTO MULTA (Tipo, Monto, Descripccion, Fecha, Estado, Dui) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        
                        # 3. Tupla de valores
                        values = (
                            str(Tipo),
                            float(Monto),
                            str(Descripccion) if Descripccion.strip() != "" else None,
                            Fecha,
                            str(Estado),
                            int(Dui)  # Aquí se guarda el DUI directamente
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Multa registrada correctamente: {Tipo} - ${Monto:.2f}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar la multa en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar multas existentes
def mostrar_lista_multas():
    st.header("📋 Lista de Multas")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todas las multas con información del miembro
        cursor.execute("""
            SELECT m.ID_Multa, m.Tipo, m.Monto, m.Descripccion, m.Fecha, m.Estado,
                   mi.Dui, mi.Nombre, mi.Apellido
            FROM MULTA m
            LEFT JOIN Miembro mi ON m.Dui = mi.Dui
            ORDER BY m.Fecha DESC, m.ID_Multa DESC
        """)
        
        multas = cursor.fetchall()
        
        if multas:
            # Mostrar las multas en una lista expandible
            st.subheader("Multas Registradas")
            
            for multa in multas:
                with st.expander(f"💰 {multa[1]} - ${multa[2]:.2f} - {multa[4]}"):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.write(f"**ID Multa:** {multa[0]}")
                        st.write(f"**Tipo:** {multa[1]}")
                        st.write(f"**Monto:** ${multa[2]:.2f}")
                        st.write(f"**Fecha:** {multa[4]}")
                        st.write(f"**Estado:** {multa[5]}")
                        st.write(f"**Miembro:** {multa[7]} {multa[8]}")
                        st.write(f"**DUI:** {multa[6]}")
                    
                    with col2:
                        st.write("**Descripción:**")
                        if multa[3]:
                            st.write(multa[3])
                        else:
                            st.write("Sin descripción")
                    
                    # Botones de acción
                    col_act1, col_act2, col_act3 = st.columns(3)
                    with col_act1:
                        if st.button("📝 Editar", key=f"editar_{multa[0]}"):
                            st.info("🔧 Funcionalidad de edición en desarrollo...")
                    with col_act2:
                        if st.button("✅ Marcar Pagada", key=f"pagar_{multa[0]}"):
                            st.info("💵 Funcionalidad de pago en desarrollo...")
                    with col_act3:
                        if st.button("🗑️ Eliminar", key=f"eliminar_{multa[0]}"):
                            st.warning("⚠️ Funcionalidad de eliminación en desarrollo...")
        else:
            st.info("📭 No hay multas registradas aún.")
            
    except Exception as e:
        st.error(f"❌ Error al cargar la lista de multas: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función para buscar multas
def buscar_multas():
    st.header("🔍 Buscar Multas")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            estado_busqueda = st.selectbox("Estado", ["Todos"] + ["Pendiente", "Pagada", "Cancelada", "Vencida"])
        
        with col2:
            fecha_inicio = st.date_input("Fecha desde")
        
        with col3:
            fecha_fin = st.date_input("Fecha hasta")
        
        # Buscar por miembro
        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()
        miembro_options = {f"{miembro[1]} {miembro[2]}": miembro[0] for miembro in miembros}
        miembro_busqueda = st.selectbox("Miembro", ["Todos"] + list(miembro_options.keys()))
        
        buscar = st.button("🔍 Buscar Multas")
        
        if buscar:
            # Construir consulta dinámica
            query = """
                SELECT m.ID_Multa, m.Tipo, m.Monto, m.Descripccion, m.Fecha, m.Estado,
                       mi.Dui, mi.Nombre, mi.Apellido
                FROM MULTA m
                LEFT JOIN Miembro mi ON m.Dui = mi.Dui
                WHERE 1=1
            """
            params = []
            
            if estado_busqueda != "Todos":
                query += " AND m.Estado = %s"
                params.append(estado_busqueda)
            
            if fecha_inicio:
                query += " AND m.Fecha >= %s"
                params.append(fecha_inicio)
            
            if fecha_fin:
                query += " AND m.Fecha <= %s"
                params.append(fecha_fin)
            
            if miembro_busqueda != "Todos":
                query += " AND m.Dui = %s"
                params.append(miembro_options[miembro_busqueda])
            
            query += " ORDER BY m.Fecha DESC"
            
            cursor.execute(query, params)
            multas_encontradas = cursor.fetchall()
            
            if multas_encontradas:
                st.success(f"✅ Se encontraron {len(multas_encontradas)} multa(s)")
                
                for multa in multas_encontradas:
                    with st.expander(f"💰 {multa[1]} - ${multa[2]:.2f} - {multa[4]}"):
                        st.write(f"**ID:** {multa[0]} | **Estado:** {multa[5]} | **Miembro:** {multa[7]} {multa[8]}")
                        st.write("**Descripción:**")
                        st.write(multa[3] if multa[3] else "Sin descripción")
            else:
                st.warning("🔍 No se encontraron multas con los criterios especificados.")
                
    except Exception as e:
        st.error(f"❌ Error en la búsqueda: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función principal que combina todas las vistas
def gestionar_multas():
    """
    Función principal para gestionar multas
    """
    tab1, tab2, tab3 = st.tabs(["💰 Registrar Nueva Multa", "📋 Ver Multas Existentes", "🔍 Buscar Multas"])
    
    with tab1:
        mostrar_multa()
    
    with tab2:
        mostrar_lista_multas()
    
    with tab3:
        buscar_multas()
