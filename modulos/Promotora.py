# modulos/Promotora.py
import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

# Importación segura de plotly
try:
    import plotly.express as px
except Exception:
    px = None

def mostrar_Promotora():
    st.title("👩‍💼 Módulo Promotora – Reportes por Grupo")

    conn = None
    try:
        conn = obtener_conexion()

        # Obtener lista de grupos disponibles desde la tabla Miembro
        df_grupos = pd.read_sql_query("SELECT DISTINCT Grupo FROM Miembro ORDER BY Grupo", conn)
        if df_grupos.empty:
            st.warning("No se encontraron grupos en la tabla Miembro.")
            return

        lista_grupos = df_grupos["Grupo"].tolist()

        st.sidebar.header("📌 Filtro por Grupo")
        # mostramos también en el cuerpo para que sea visible sin tocar la barra lateral
        col1, col2 = st.columns([2, 1])
        with col1:
            id_grupo = st.selectbox("Selecciona un grupo:", ["-- Seleccionar --"] + lista_grupos)
        with col2:
            # botón para refrescar datos
            if st.button("🔄 Refrescar"):
                st.experimental_rerun()

        if id_grupo is None or id_grupo == "-- Seleccionar --":
            st.info("Seleccione un grupo para ver los reportes (panel izquierdo o arriba).")
            return

        # PARA CONSULTAS: usamos consultas parametrizadas
        # ----------------------------
        # REPORTE DE AHORROS
        # ----------------------------
        st.subheader("💰 Reporte de Ahorros")
        query_ahorros = """
            SELECT 
                A.ID_Ahorro,
                A.Monto_actual,
                A.Fecha_Actualizacion,
                M.Nombre,
                M.Apellido,
                M.Dui
            FROM AHORROS A
            INNER JOIN Miembro M ON A.Dui = M.Dui
            WHERE M.Grupo = %s
            ORDER BY A.Fecha_Actualizacion DESC
        """
        df_ahorros = pd.read_sql_query(query_ahorros, conn, params=[id_grupo])
        if df_ahorros.empty:
            st.info("No se encontraron registros de ahorros para este grupo.")
        else:
            st.dataframe(df_ahorros)
            # gráfico - preferimos plotly si está disponible
            if px is not None:
                fig = px.bar(df_ahorros, x="Nombre", y="Monto_actual", hover_data=["Apellido","Dui"],
                             title="Ahorros por Miembro", labels={"Monto_actual":"Monto actual"})
                st.plotly_chart(fig, use_container_width=True)
            else:
                # alternativa simple con streamlit
                st.bar_chart(df_ahorros.set_index("Nombre")["Monto_actual"])

        # ----------------------------
        # REPORTE DE MULTAS
        # ----------------------------
        st.subheader("⚠️ Reporte de Multas")
        query_multas = """
            SELECT 
                Mu.ID_Multa,
                Mu.Tipo,
                Mu.Monto,
                Mu.Descripccion,
                Mu.Fecha,
                Mu.Estado,
                M.Nombre,
                M.Apellido,
                M.Dui
            FROM MULTA Mu
            INNER JOIN Miembro M ON Mu.Dui = M.Dui
            WHERE M.Grupo = %s
            ORDER BY Mu.Fecha DESC
        """
        df_multas = pd.read_sql_query(query_multas, conn, params=[id_grupo])
        if df_multas.empty:
            st.info("No se encontraron multas para este grupo.")
        else:
            st.dataframe(df_multas)

            # Mostrar conteo de multas por estado
            estados = df_multas["Estado"].value_counts().rename_axis("Estado").reset_index(name="Cantidad")
            st.write("Multas por Estado:")
            st.dataframe(estados)

            if px is not None:
                fig_m = px.pie(estados, names="Estado", values="Cantidad", title="Distribución de Multas por Estado")
                st.plotly_chart(fig_m, use_container_width=True)

        # ----------------------------
        # REPORTE DE PRÉSTAMOS
        # ----------------------------
        st.subheader("📄 Reporte de Préstamos")
        query_prestamos = """
            SELECT 
                Pr.ID_Prestamo,
                Pr.Monto,
                Pr.Intereses,
                Pr.Plazo_Meses,
                Pr.Total_cuotas,
                Pr.Saldo_restante,
                Pr.Fecha_creación,
                M.Nombre,
                M.Apellido,
                M.Dui
            FROM PRESTAMO Pr
            INNER JOIN Miembro M ON Pr.Dui = M.Dui
            WHERE M.Grupo = %s
            ORDER BY Pr.Fecha_creación DESC
        """
        df_prestamos = pd.read_sql_query(query_prestamos, conn, params=[id_grupo])
        if df_prestamos.empty:
            st.info("No se encontraron préstamos para este grupo.")
        else:
            st.dataframe(df_prestamos)
            # gráfico de préstamos por miembro (monto)
            if px is not None:
                fig2 = px.bar(df_prestamos, x="Nombre", y="Monto", hover_data=["Apellido","Dui"],
                              title="Préstamos por Miembro", labels={"Monto":"Monto préstamo"})
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.bar_chart(df_prestamos.set_index("Nombre")["Monto"])

        # resumen rápido
        st.markdown("---")
        st.subheader("📊 Resumen rápido")
        total_ahorros = df_ahorros["Monto_actual"].sum() if not df_ahorros.empty else 0
        total_multas = df_multas["Monto"].sum() if not df_multas.empty else 0
        total_prestamos = df_prestamos["Monto"].sum() if not df_prestamos.empty else 0

        st.metric("Total Ahorros (grupo)", f"${total_ahorros:,.2f}")
        st.metric("Total Multas (grupo)", f"${total_multas:,.2f}")
        st.metric("Total Préstamos (grupo)", f"${total_prestamos:,.2f}")

    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")

    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    # botón para volver al menú (si en tu app usas session state)
    if st.button("⬅ Volver al menú principal"):
        # ejemplo: si controlas la navegación por st.session_state
        st.session_state.module = None
        st.rerun()
