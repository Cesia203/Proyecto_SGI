import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_Prestamo():
    st.header("💰 Registrar Préstamo")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        # Obtener datos FK
        cursor.execute("SELECT ID_Promotora, Nombre FROM PROMOTORA WHERE Estado = 'Activa'")
        promotoras = cursor.fetchall()

        cursor.execute("SELECT ID_Ciclo, Fecha_inicio, Fecha_fin FROM CICLO WHERE Estado = 'Activo'")
        ciclos = cursor.fetchall()

        cursor.execute("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Estado = 'Activo'")
        miembros = cursor.fetchall()

        with st.form("form_prestamo"):

            Monto = st.number_input("Monto del Préstamo*", min_value=0.0, step=0.01, format="%.2f")
            Intereses = st.number_input("Tasa de Interés (%)*", min_value=0.0, max_value=100.0, step=0.1, format="%.1f")
            Plazo_Meses = st.number_input("Plazo en Meses*", min_value=1, max_value=360, step=1)
            Total_cuotas = st.number_input("Total de Cuotas*", min_value=1, max_value=360, step=1)
            Saldo_restante = st.number_input("Saldo Restante*", min_value=0.0, step=0.01, format="%.2f", value=0.0)

            # ❌ CAMPO ESTADO ELIMINADO

            # Promotora
            if promotoras:
                promotora_options = {f"{p[1]} (ID: {p[0]})": p[0] for p in promotoras}
                ID_Promotora = promotora_options[
                    st.selectbox("Promotora*", list(promotora_options.keys()))
                ]
            else:
                st.warning("No hay promotoras activas disponibles.")
                ID_Promotora = None

            # Ciclo
            if ciclos:
                ciclo_options = {f"Ciclo {c[0]}: {c[1]} a {c[2]}": c[0] for c in ciclos}
                ID_Ciclo = ciclo_options[
                    st.selectbox("Ciclo*", list(ciclo_options.keys()))
                ]
            else:
                st.warning("No hay ciclos activos disponibles.")
                ID_Ciclo = None

            # Miembro Solicitante
            if miembros:
                miembro_options = {f"{m[1]} {m[2]} (DUI: {m[0]})": m[0] for m in miembros}
                Dui = miembro_options[
                    st.selectbox("Miembro Solicitante*", list(miembro_options.keys()))
                ]
            else:
                st.warning("No hay miembros activos disponibles.")
                Dui = None

            enviar = st.form_submit_button("✅ Registrar Préstamo")

            if enviar:
                if (Monto is None or Intereses is None or Plazo_Meses is None or Total_cuotas is None or 
                    Saldo_restante is None or not ID_Promotora or not ID_Ciclo or not Dui):
                    st.warning("⚠️ Debes completar todos los campos obligatorios (*)")

                elif Saldo_restante > Monto:
                    st.warning("⚠️ El saldo restante no puede ser mayor al monto del préstamo.")
                
                else:
                    try:
                        # ❗ Estado eliminado del INSERT
                        sql_query = """
                            INSERT INTO PRESTAMO (
                                Monto, Intereses, Plazo_Meses, Total_cuotas,
                                Saldo_restante, ID_Promotora, ID_Ciclo, Dui
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        values = (
                            float(Monto),
                            float(Intereses),
                            int(Plazo_Meses),
                            int(Total_cuotas),
                            float(Saldo_restante),
                            int(ID_Promotora),
                            int(ID_Ciclo),
                            int(Dui)
                        )

                        cursor.execute(sql_query, values)
                        con.commit()

                        interes_monto = (Monto * Intereses) / 100
                        total_pagar = Monto + interes_monto
                        valor_cuota = total_pagar / Total_cuotas if Total_cuotas > 0 else 0

                        st.success(f"✅ Préstamo registrado correctamente: ${Monto:,.2f}")
                        st.info(f"""
                        **Resumen del Préstamo:**
                        - **Monto:** ${Monto:,.2f}
                        - **Intereses ({Intereses}%):** ${interes_monto:,.2f}
                        - **Total a Pagar:** ${total_pagar:,.2f}
                        - **Valor Cuota:** ${valor_cuota:,.2f}
                        - **Saldo Restante:** ${Saldo_restante:,.2f}
                        """)

                        st.rerun()

                    except Exception as e:
                        con.rollback()
                        st.error(f"❌ Error al registrar el préstamo en la base de datos: {e}")

    except Exception as e:
        st.error(f"❌ Error al conectar a la base de datos: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'con' in locals(): con.close()
