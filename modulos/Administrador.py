# modulos/Administrador.py
import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

# Importación segura de plotly
try:
    import plotly.express as px
except Exception:
    px = None

def mostrar_Administrador():
    st.title("🧑‍💼 Módulo Administrador – Reportes por Distrito")

    conn = None
    try:
        conn = obtener_conexion()

        # Obtener lista de distritos desde Miembro
        df_distritos = pd.read_sql_query("SELECT DISTINCT Distrito FROM Miembro ORDER BY Distrito", conn)

        if df_distritos.empty:
            st.warning("No se encontraron distritos en la tabla Miembro.")
            return

        lista_distritos = df_distritos["Distrito"].tolist()

        st.sidebar.header("📌 Filtro por Distrito")
        col1, col2 = st.columns([2, 1])
        with col1:
            distrito = st.selectbox("Selecciona un distrito:", ["-- Seleccionar --"] + lista_distritos)
        with col2:
            if st.button("🔄 Refrescar"):
                st.experimental_rerun()

        if distrito is None or distrito == "-- Seleccionar --":
            st.info("Seleccione un distrito para ver los reportes.")
            return

        # ---------------------------------
        #          REPORTE AHORROS
        # ---------------------------------
        st.subheader("💰 Reporte de Ahorros (por Distrito)")
        query_ahorros = """
            SELECT 
                A.ID_Ahorro,
                A.Monto_actual,
                A.Fecha_Actualizacion,
                M.Nombre,
                M.Apellido,
                M.Dui,
                M.Distrito
            FROM AHORROS A
            INNER JOIN Miembro M ON A.Dui = M.Dui
            WHERE M.Distrito = %s
            ORDER BY A.Fecha_Actualizacion DESC
        """
        df_ahorros = pd.read_sql_query(query_ahorros, conn, params=[distrito])

        if df_ahorros.empty:
            st.info("No se encontraron ahorros para este distrito.")
        else:
            st.dataframe(df_ahorros)

            if px is not None:
                fig = px.bar(
                    df_ahorros,
                    x="Nombre",
                    y="Monto_actual",
                    hover_data=["Apellido", "Dui"],
                    title=f"Ahorros por Miembro – Distrito {distrito}",
                    labels={"Monto_actual": "Monto actual"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.bar_chart(df_ahorros.set_index("Nombre")["Monto_actual"])

        # ---------------------------------
        #          REPORTE MULTAS
        # ---------------------------------
        st.subheader("⚠️ Reporte de Multas (por Distrito)")
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
                M.Dui,
                M.Distrito
            FROM MULTA Mu
            INNER JOIN Miembro M ON Mu.Dui = M.Dui
            WHERE M.Distrito = %s
            ORDER BY Mu.Fecha DESC
        """
        df_multas = pd.read_sql_query(query_multas, conn, params=[distrito])

        if df_multas.empty:
            st.info("No se encontraron multas para este distrito.")
        else:
            st.dataframe(df_multas)

            estados = df_multas["Estado"].value_counts().rename_axis("Estado").reset_index(name="Cantidad")
            st.write("Multas por Estado:")
            st.dataframe(estados)

            if px is not None:
                fig_m = px.pie(
                    estados,
                    names="Estado",
                    values="Cantidad",
                    title=f"Distribución de Multas – Distrito {distrito}"
                )
                st.plotly_chart(fig_m, use_container_width=True)

        # ---------------------------------
        #          REPORTE PRÉSTAMOS
        # ---------------------------------
        st.subheader("📄 Reporte de Préstamos (por Distrito)")
        query_prestamos = """
            SELECT 
                Pr.ID_Prestamo,
                Pr.Monto,
                Pr.Intereses,
                Pr.Plazo_Meses,
                Pr.Total_cuotas,
                Pr.Saldo_restante,
                Pr.Fecha_creacion,
                M.Nombre,
                M.Apellido,
                M.Dui,
                M.Distrito
            FROM PRESTAMO Pr
            INNER JOIN Miembro M ON Pr.Dui = M.Dui
            WHERE M.Distrito = %s
            ORDER BY Pr.Fecha_creacion DESC
        """
        df_prestamos = pd.read_sql_query(query_prestamos, conn, params=[distrito])

        if df_prestamos.empty:
            st.info("No se encontraron préstamos para este distrito.")
        else:
            st.dataframe(df_prestamos)

            if px is not None:
                fig2 = px.bar(
                    df_prestamos,
                    x="Nombre",
                    y="Monto",
                    hover_data=["Apellido", "Dui"],
                    title=f"Préstamos por Miembro – Distrito {distrito}",
                    labels={"Monto": "Monto préstamo"}
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.bar_chart(df_prestamos.set_index("Nombre")["Monto"])

        # ---------------------------------
        #           RESUMEN RÁPIDO
        # ---------------------------------
        st.markdown("---")
        st.subheader("📊 Resumen del Distrito")

        total_ahorros = df_ahorros["Monto_actual"].sum() if not df_ahorros.empty else 0
        total_multas = df_multas["Monto"].sum() if not df_multas.empty else 0
        total_prestamos = df_prestamos["Monto"].sum() if not df_prestamos.empty else 0

        st.metric(f"Total Ahorros ({distrito})", f"${total_ahorros:,.2f}")
        st.metric(f"Total Multas ({distrito})", f"${total_multas:,.2f}")
        st.metric(f"Total Préstamos ({distrito})", f"${total_prestamos:,.2f}")

    except Exception as e:
        st.error(f"❌ Error al cargar datos: {e}")

    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
