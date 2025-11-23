import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_grupos():
    st.header("👥 Registrar Grupo")
    
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        
        # Formulario para registrar el grupo
        with st.form("form_grupo"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre del grupo")
                fecha_inicio = st.date_input("Fecha de inicio")
                tasa_interes = st.number_input("Tasa de interés (%)", min_value=0.0, format="%.2f")
                tipo_multa = st.text_input("Tipo de multa")
                frecuencia_reuniones = st.selectbox(
                    "Frecuencia de reuniones",
                    ["", "Diaria", "Semanal", "Quincenal", "Mensual"]
                )
            
            with col2:
                id_ciclo = st.number_input("ID Ciclo", min_value=0, step=1, value=0)
                dui = st.text_input("DUI")
                estado = st.selectbox(
                    "Estado",
                    ["", "Activo", "Inactivo", "Suspendido", "Finalizado"]
                )
                id_promotora = st.number_input("ID Promotora", min_value=0, step=1, value=0)
                distrito = st.number_input("Distrito", min_value=1, step=1)
            
            politicas_prestamo = st.text_area("Políticas de préstamo")
            
            enviar = st.form_submit_button("✅ Guardar grupo")
            
            if enviar:
                # Validaciones
                if nombre.strip() == "":
                    st.warning("⚠️ Debes ingresar el nombre del grupo.")
                elif not fecha_inicio:
                    st.warning("⚠️ Debes seleccionar la fecha de inicio.")
                elif distrito <= 0:
                    st.warning("⚠️ Debes ingresar un distrito válido.")
                else:
                    try:
                        cursor.execute(
                            """INSERT INTO GRUPOS 
                            (Nombre, Fecha_inicio, Tasa_interes, Tipo_multa, Frecuencia_reuniones, 
                             ID_Ciclo, Dui, Políticas_prestamo, Estado, ID_Promotora, Distrito) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                nombre, 
                                fecha_inicio, 
                                tasa_interes, 
                                tipo_multa if tipo_multa.strip() else None, 
                                frecuencia_reuniones if frecuencia_reuniones else None,
                                id_ciclo if id_ciclo > 0 else None, 
                                dui if dui.strip() else None,
                                politicas_prestamo if politicas_prestamo.strip() else None,
                                estado if estado else None,
                                id_promotora if id_promotora > 0 else None,
                                distrito
                            )
                        )
                        con.commit()
                        st.success(f"✅ Grupo '{nombre}' registrado correctamente")
                        st.rerun()
                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el grupo: {e}")
                        
    except Exception as e:
        st.error(f"❌ Error general: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()
