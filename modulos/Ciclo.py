import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_ciclo():
    st.header("🔄 Registrar Ciclo")

    # Intentar obtener la conexión a la base de datos
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Formulario para registrar ciclo
        with st.form("form_ciclo"):
            # Variables del formulario
            Fecha_inicio = st.date_input("Fecha de Inicio*")
            Fecha_fin = st.date_input("Fecha de Fin*")
            
            # Campo para Estado con opciones predefinidas
            estado_options = ["Activo", "Inactivo", "Finalizado", "Planificado"]
            Estado = st.selectbox("Estado*", estado_options)
            
            # Campo para Utilidad Total
            Utilidad_total = st.number_input(
                "Utilidad Total", 
                min_value=0.0, 
                step=0.01,
                format="%.2f",
                value=0.0
            )
            
            enviar = st.form_submit_button("✅ Registrar Ciclo")

            if enviar:
                # 1. Validación de campos obligatorios
                if not Fecha_inicio or not Fecha_fin or Estado.strip() == "":
                    st.warning("⚠️ Debes ingresar la Fecha de Inicio, Fecha de Fin y Estado.")
                
                # 2. Validación de fechas
                elif Fecha_inicio >= Fecha_fin:
                    st.warning("⚠️ La Fecha de Fin debe ser posterior a la Fecha de Inicio.")
                
                else:
                    try:
                        # 3. Sentencia SQL para insertar ciclo - USANDO "CICLO"
                        sql_query = """
                            INSERT INTO CICLO (Fecha_inicio, Fecha_fin, Estado, Utilidad_Total) 
                            VALUES (%s, %s, %s, %s)
                        """
                        
                        # 4. Tupla de valores
                        values = (
                            Fecha_inicio,
                            Fecha_fin,
                            str(Estado),
                            float(Utilidad_total)
                        )
                        
                        cursor.execute(sql_query, values)
                        con.commit()
                        
                        # Mensaje de éxito y reinicio de la página
                        st.success(f"✅ Ciclo registrado correctamente: {Fecha_inicio} a {Fecha_fin} - {Estado}")
                        st.rerun()
                        
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el ciclo en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos o error general: {e}")

    finally:
        # Cierre seguro de recursos
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'con' in locals() and con:
            con.close()

# Función adicional para mostrar ciclos existentes
def mostrar_lista_ciclos():
    st.header("📋 Lista de Ciclos")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Consulta para obtener todos los ciclos - USANDO "CICLO"
        cursor.execute("""
            SELECT ID_Ciclo, Fecha_inicio, Fecha_fin, Estado, Utilidad_Total
            FROM CICLO 
            ORDER BY Fecha_inicio DESC
        """)
        
        ciclos = cursor.fetchall()
        
        if ciclos:
            # Mostrar los ciclos en una tabla
            st.subheader("Ciclos Registrados")
            
            # Crear una tabla con los datos
            for ciclo in ciclos:
                with st.expander(f"📅 Ciclo {ciclo[0]}: {ciclo[1]} a {ciclo[2]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {ciclo[0]}")
                        st.write(f"**Fecha Inicio:** {ciclo[1]}")
