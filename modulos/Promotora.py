import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import plotly.express as px

def mostrar_Promotora():
    st.title("👩‍💼 Módulo Promotora – Reportes por Grupo")

    try:
        conn = obtener_conexion()

        # Obtener lista de grupos
        df_grupos = pd.read_sql("SELECT DISTINCT ID_Grupo FROM PROMOTORA", conn)
        lista_grupos = df_grupos["ID_Grupo"].tolist()

        st.sidebar.header("📌 Filtro por Grupo")
        id_grupo = st.sidebar.selectbox("Selecciona un grupo:", lista_grupos)

        if not id_grupo:
            st.warning("Seleccione un grupo para continuar.")
            return

        # ----------------------------
        # REPORTE DE AHORROS
        # ----------------------------
        st.subheader("💰 Reporte de Ahorros")
        query_ahorros = f"""
            SELECT 
                A.ID_Ahorro,
                A.Monto_actual,
                A.Fecha_Actualizacion,
                M.Nombre,
                M.Apellido,
                M.Dui
            FROM AHORROS A
            INNER JOIN Miembro M ON A.Dui = M.Dui
            INNER JOIN PROMOTORA P ON M.ID_Grupo = P.ID_Grupo
            WHERE P.ID_Grupo = {id_grupo};
        """
        df_ahorros = pd.read_sql(query_ahorros, conn)
        st.dataframe(df_ahorros)

        if not df_ahorros.empty:
            fig = px.bar(df_ahorros, x="Nombre", y="Monto_actual",
                         title="Ahorros por Miembro")
            st.plotly_chart(fig, use_container_width=True)

        # ----------------------------
        # REPORTE DE MULTAS
        # ----------------------------
        st.subheader("⚠️ Reporte de Multas")
        query_multas = f"""
            SELECT 
                Mu.ID_Multa,
                Mu.Tipo,
                Mu.Monto,
                Mu.Fecha,
                Mu.Estado,
                M.Nombre,
                M.Apellido,
                M.Dui
            FROM MULTA Mu
            INNER JOIN Miembro M ON Mu.Dui = M.Dui
            INNER JOIN PROMOTORA P ON M.ID_Grupo = P.ID_Grupo
            WHERE P.ID_Grupo = {id_grupo};
        """
        df_multas = pd.read_sql(query_multas, conn)
        st.dataframe(df_multas)

        # ----------------------------
        # REPORTE DE PRÉSTAMOS
        # ----------------------------
        st.subheader("📄 Reporte de Préstamos")
        query_prestamos = f"""
            SELECT 
                Pr.ID_Prestamo,
                Pr.Monto,
                Pr.Intereses,
                Pr.Plazo_Meses,
                Pr.Total_cuotas,
                Pr.Saldo_restante,
                M.Nombre,
                M.Apellido,
                M.Dui
            FROM PRESTAMO Pr
            INNER JOIN Miembro M ON Pr.Dui = M.Dui
            INNER JOIN PROMOTORA P ON M.ID_Grupo = P.ID_Grupo
            WHERE P.ID_Grupo = {id_grupo};
        """
        df_prestamos = pd.read_sql(query_prestamos, conn)
        st.dataframe(df_prestamos)

        if not df_prestamos.empty:
            fig2 = px.bar(df_prestamos, x="Nombre", y="Monto",
                          title="Préstamos por Miembro")
            st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")

    finally:
        conn.close()

    if st.button("⬅ Volver al menú principal"):
        st.session_state.module = None
        st.rerun()
