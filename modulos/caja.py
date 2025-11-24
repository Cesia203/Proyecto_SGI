import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def mostrar_caja():
    st.header("📦 Reporte de Caja por Grupo")

    try:
        con = obtener_conexion()

        # --------------------------------------------------
        # OBTENER LISTA DE GRUPOS
        # --------------------------------------------------
        df_grupos = pd.read_sql_query(
            "SELECT DISTINCT Grupo FROM Miembro ORDER BY Grupo",
            con
        )

        if df_grupos.empty:
            st.warning("No hay grupos registrados.")
            return

        lista_grupos = df_grupos["Grupo"].tolist()

        grupo_sel = st.selectbox("Selecciona un grupo", ["-- Seleccionar --"] + lista_grupos)

        if grupo_sel == "-- Seleccionar --":
            return

        st.subheader(f"📊 Reporte Financiero del Grupo: {grupo_sel}")

        # --------------------------------------------------
        # DINERO QUE ENTRA
        # --------------------------------------------------

        # 1) Multas pagadas
        sql_multas = """
            SELECT M.Monto
            FROM MULTA M
            INNER JOIN Miembro Mi ON M.Dui = Mi.Dui
            WHERE Mi.Grupo = %s AND M.Estado = 'Pagada'
        """
        df_multas = pd.read_sql_query(sql_multas, con, params=[grupo_sel])
        total_multas = df_multas["Monto"].sum() if not df_multas.empty else 0

        # 2) Ahorros (solo aumentos del monto actual)
        sql_ahorros = """
            SELECT A.Monto_actual
            FROM AHORROS A
            INNER JOIN Miembro Mi ON A.Dui = Mi.Dui
            WHERE Mi.Grupo = %s
        """
        df_ahorros = pd.read_sql_query(sql_ahorros, con, params=[grupo_sel])

        total_ahorros_positivos = 0
        total_ahorros_negativos = 0

        if not df_ahorros.empty:
            # Asumimos que monto_actual es el saldo actual.
            # No hay tabla de movimientos, así que no podemos separar depósitos/retiros históricos.
            # Interpretación:
            # - Si sube → depósito (entra)
            # - Si baja → retiro (sale)
            difs = df_ahorros["Monto_actual"].diff().fillna(0)

            total_ahorros_positivos = difs[difs > 0].sum()
            total_ahorros_negativos = abs(difs[difs < 0].sum())

        # 3) Pagos de préstamo
        sql_pago_prestamo = """
            SELECT Pa.Monto_pago
            FROM PAGO Pa
            INNER JOIN PRESTAMO Pr ON Pa.ID_Prestamo = Pr.ID_Prestamo
            INNER JOIN Miembro Mi ON Pr.Dui = Mi.Dui
            WHERE Mi.Grupo = %s
        """
        df_pagos = pd.read_sql_query(sql_pago_prestamo, con, params=[grupo_sel])
        total_pagos_prestamo = df_pagos["Monto_pago"].sum() if not df_pagos.empty else 0

        # TOTAL ENTRA
        total_entra = total_multas + total_ahorros_positivos + total_pagos_prestamo

        # --------------------------------------------------
        # DINERO QUE SALE
        # --------------------------------------------------

        # 1) Retiros de ahorro (cuando el monto baja)
        total_retiros = total_ahorros_negativos

        # 2) Desembolsos (Monto del préstamo)
        sql_prestamos = """
            SELECT Pr.Monto
            FROM PRESTAMO Pr
            INNER JOIN Miembro Mi ON Pr.Dui = Mi.Dui
            WHERE Mi.Grupo = %s
        """
        df_prestamos = pd.read_sql_query(sql_prestamos, con, params=[grupo_sel])
        total_desembolsos = df_prestamos["Monto"].sum() if not df_prestamos.empty else 0

        # TOTAL SALE
        total_sale = total_retiros + total_desembolsos

        # --------------------------------------------------
        # SALDO FINAL
        # --------------------------------------------------
        saldo_final = total_entra - total_sale

        # --------------------------------------------------
        # MOSTRAR RESULTADOS
        # --------------------------------------------------
        st.markdown("## 💰 Dinero que entra")
        st.write(f"✔ Multas pagadas: **${total_multas:,.2f}**")
        st.write(f"✔ Depósitos de ahorro: **${total_ahorros_positivos:,.2f}**")
        st.write(f"✔ Pagos de préstamo: **${total_pagos_prestamo:,.2f}**")
        st.subheader(f"🟦 Total dinero que entra: **${total_entra:,.2f}**")

        st.markdown("---")

        st.markdown("## 💸 Dinero que sale")
        st.write(f"✔ Retiros de ahorro: **${total_retiros:,.2f}**")
        st.write(f"✔ Desembolsos de préstamo: **${total_desembolsos:,.2f}**")
        st.subheader(f"🟥 Total dinero que sale: **${total_sale:,.2f}**")

        st.markdown("---")

        st.markdown("## 🧮 Saldo Final en Caja")
        st.metric("Saldo actual del grupo", f"${saldo_final:,.2f}")

    except Exception as e:
        st.error(f"❌ Error: {e}")

    finally:
        if 'con' in locals():
            con.close()
