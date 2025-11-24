import streamlit as st
import pandas as pd
from datetime import date
from modulos.config.conexion import obtener_conexion

def mostrar_ciclo():
    st.header("🔄 Cierre de Ciclo por Grupo")

    try:
        con = obtener_conexion()

        # --------------------------------------------------
        # LISTA DE GRUPOS
        # --------------------------------------------------
        df_grupos = pd.read_sql_query(
            "SELECT DISTINCT Grupo FROM Miembro ORDER BY Grupo",
            con
        )

        if df_grupos.empty:
            st.warning("No hay grupos registrados.")
            return

        grupos = df_grupos["Grupo"].tolist()

        grupo_sel = st.selectbox("Seleccione un grupo", ["-- Seleccionar --"] + grupos)

        if grupo_sel == "-- Seleccionar --":
            return

        st.subheader(f"📘 Datos del grupo: {grupo_sel}")

        # ==================================================
        # INFORMACIÓN BASE DEL GRUPO
        # ==================================================
        sql_miembros = """
            SELECT Dui, Nombre, Apellido
            FROM Miembro
            WHERE Grupo = %s
        """
        df_miembros = pd.read_sql_query(sql_miembros, con, params=[grupo_sel])

        if df_miembros.empty:
            st.warning("Este grupo no tiene miembros.")
            return

        total_miembros = len(df_miembros)

        # ==================================================
        # SALDO AHORRADO POR MIEMBRO
        # ==================================================
        sql_ahorros = """
            SELECT A.Dui, A.Monto_actual
            FROM AHORROS A
            INNER JOIN Miembro M ON A.Dui = M.Dui
            WHERE M.Grupo = %s
        """
        df_ahorros = pd.read_sql_query(sql_ahorros, con, params=[grupo_sel])

        df_ahorros = df_ahorros.merge(df_miembros, on="Dui", how="right")
        df_ahorros["Monto_actual"] = df_ahorros["Monto_actual"].fillna(0)

        total_ahorros_grupo = df_ahorros["Monto_actual"].sum()

        # ==================================================
        # MULTAS PAGADAS
        # ==================================================
        sql_multas = """
            SELECT M.Monto
            FROM MULTA M
            INNER JOIN Miembro Mi ON M.Dui = Mi.Dui
            WHERE Mi.Grupo = %s AND M.Estado = 'Pagada'
        """
        df_multas = pd.read_sql_query(sql_multas, con, params=[grupo_sel])
        total_multas = df_multas["Monto"].sum() if not df_multas.empty else 0

        # ==================================================
        # INTERESES PAGADOS DE PRÉSTAMOS
        # ==================================================
        sql_intereses = """
            SELECT Pa.Monto
            FROM PAGO Pa
            INNER JOIN PRESTAMO Pr ON Pa.ID_Prestamo = Pr.ID_Prestamo
            INNER JOIN Miembro Mi ON Pr.Dui = Mi.Dui
            WHERE Mi.Grupo = %s
        """
        df_intereses = pd.read_sql_query(sql_intereses, con, params=[grupo_sel])
        total_intereses = df_intereses["Monto"].sum() if not df_intereses.empty else 0

        # ==================================================
        # TOTAL ABSOLUTO DEL CICLO
        # ==================================================
        total_absoluto = total_ahorros_grupo + total_multas + total_intereses
        total_por_miembro = total_absoluto / total_miembros

        # ==================================================
        # MOSTRAR RESULTADOS
        # ==================================================
        st.markdown("## 🧮 Resumen del Cierre del Ciclo")

        st.write(f"👥 Total de miembros: **{total_miembros}**")
        st.write(f"💰 Total ahorrado del grupo: **${total_ahorros_grupo:,.2f}**")
        st.write(f"🔔 Total obtenido por multas: **${total_multas:,.2f}**")
        st.write(f"🏦 Total obtenido por intereses de préstamos: **${total_intereses:,.2f}**")

        st.subheader(f"🔹 Total absoluto del ciclo: **${total_absoluto:,.2f}**")
        st.subheader(f"🔹 Total correspondiente a cada miembro: **${total_por_miembro:,.2f}**")

        st.markdown("---")
        st.markdown("## 📝 Asignar saldo inicial para el siguiente ciclo")

        # ==================================================
        # FORMULARIO PARA EL SIGUIENTE CICLO
        # ==================================================
        saldos = {}

        with st.form("form_saldo_ciclo"):

            st.write("Ingrese manualmente el ID del ciclo nuevo:")
            id_ciclo = st.number_input(
                "ID del nuevo ciclo",
                min_value=1,
                step=1,
                key="id_ciclo"
            )

            st.write("Ingrese el saldo inicial del siguiente ciclo para cada miembro:")

            for idx, row in df_miembros.iterrows():
                nombre = f"{row['Nombre']} {row['Apellido']}"
                dui = row["Dui"]

                saldo = st.number_input(
                    f"Saldo inicial para {nombre} ({dui})",
                    min_value=0.00,
                    step=0.01,
                    key=f"saldo_{dui}"
                )

                saldos[dui] = saldo

            enviar = st.form_submit_button("💾 Guardar saldos del nuevo ciclo")

            if enviar:
                try:
                    cursor = con.cursor()

                    for dui, saldo_ini in saldos.items():
                        sql_insert = """
                            INSERT INTO SALDO_CICLO (ID_Ciclo, Dui, Saldo_Inicial, Fecha_Registro)
                            VALUES (%s, %s, %s, %s)
                        """

                        cursor.execute(
                            sql_insert,
                            (id_ciclo, dui, saldo_ini, date.today())
                        )

                    con.commit()
                    st.success("✅ Saldos del siguiente ciclo registrados correctamente.")
                    st.rerun()

                except Exception as e:
                    con.rollback()
                    st.error(f"❌ Error al guardar saldos: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if 'con' in locals():
            con.close()
