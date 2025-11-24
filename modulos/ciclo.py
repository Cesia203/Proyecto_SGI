import streamlit as st
from datetime import date
import pandas as pd
from modulos.config.conexion import obtener_conexion

def mostrar_ciclo():
    """
    Módulo para registrar/gestionar ciclos y realizar el cierre de ciclo por grupo.
    - Permite: seleccionar un ciclo activo y un grupo.
    - Calcula: ahorros por miembro, total ahorros grupo, multas pagadas, pagos de préstamos (capital),
      interés cobrado proporcionalmente por préstamos, total ingreso, total fondo, monto por miembro.
    - Permite editar/ingresar manualmente el saldo inicial para cada miembro del siguiente ciclo
      y guardarlo en SALDO_CICLO. También permite crear un nuevo ciclo siguiente opcionalmente.
    """

    st.header("🔄 Cierre y Gestión de Ciclos")

    conn = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        # -------------------------
        # Selección / creación de ciclos
        # -------------------------
        # Traer ciclos (todos) para seleccionar el que se va a cerrar o gestionar
        df_ciclos = pd.read_sql_query("SELECT ID_Ciclo, Fecha_inicio, Fecha_fin, Estado FROM CICLO ORDER BY ID_Ciclo DESC", conn)
        if df_ciclos.empty:
            st.info("No hay ciclos registrados. Puedes crear uno nuevo desde el formulario abajo.")
            mostrar_form_nuevo_ciclo = True
        else:
            mostrar_form_nuevo_ciclo = False

        st.subheader("1) Selección de Ciclo")
        colc1, colc2 = st.columns([2, 2])
        with colc1:
            opciones_ciclos = ["-- Nuevo Ciclo --"] + [f"{int(r.ID_Ciclo)} | {r.Fecha_inicio} - {r.Fecha_fin or '...'} ({r.Estado})" for r in df_ciclos.itertuples()]
            seleccionado = st.selectbox("Selecciona ciclo (o crear nuevo):", opciones_ciclos)
        with colc2:
            if seleccionado != "-- Nuevo Ciclo --":
                id_ciclo_sel = int(seleccionado.split("|")[0].strip())
            else:
                id_ciclo_sel = None

        # -------------------------
        # Crear nuevo ciclo (opcional)
        # -------------------------
        st.subheader("2) Crear nuevo ciclo (opcional)")
        with st.expander("Crear un nuevo ciclo"):
            form_new = st.form("nuevo_ciclo_form")
            new_start = form_new.date_input("Fecha inicio", value=date.today())
            new_end = form_new.date_input("Fecha fin (opcional)", value=None)
            new_estado = form_new.selectbox("Estado", ["Activo", "Pendiente", "Finalizado"], index=0)
            new_utilidad = form_new.number_input("Utilidad total (opcional)", min_value=0.0, step=0.01, format="%.2f")
            crear_btn = form_new.form_submit_button("🆕 Crear Ciclo")
            if crear_btn:
                utilidad_val = float(new_utilidad) if new_utilidad > 0 else None
                try:
                    cursor.execute(
                        "INSERT INTO CICLO (Fecha_inicio, Fecha_fin, Estado, Utilidad_Total) VALUES (%s, %s, %s, %s)",
                        (new_start, new_end, new_estado, utilidad_val)
                    )
                    conn.commit()
                    st.success("Ciclo creado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error creando ciclo: {e}")

        # -------------------------
        # Selección de grupo
        # -------------------------
        st.subheader("3) Selecciona Grupo para el cierre")
        df_grupos = pd.read_sql_query("SELECT DISTINCT Grupo FROM Miembro ORDER BY Grupo", conn)
        if df_grupos.empty:
            st.warning("No hay grupos registrados en Miembro.")
            return
        grupos = df_grupos["Grupo"].tolist()
        grupo_sel = st.selectbox("Grupo:", ["-- Seleccionar --"] + grupos)
        if grupo_sel == "-- Seleccionar --":
            st.info("Selecciona un grupo para ver los cálculos del cierre.")
            return

        st.markdown("---")
        st.subheader(f"Resumen financiero para el Grupo: **{grupo_sel}** (Ciclo: {id_ciclo_sel or 'Sin especificar'})")

        # -------------------------
        # Datos: miembros del grupo
        # -------------------------
        df_miembros = pd.read_sql_query("SELECT Dui, Nombre, Apellido FROM Miembro WHERE Grupo = %s ORDER BY Nombre, Apellido", conn, params=[grupo_sel])
        if df_miembros.empty:
            st.warning("No se encontraron miembros en este grupo.")
            return
        n_miembros = len(df_miembros)

        # -------------------------
        # Ahorros individuales y total del grupo
        # -------------------------
        df_ahorros = pd.read_sql_query("""
            SELECT A.Dui, A.Monto_actual
            FROM AHORROS A
            INNER JOIN Miembro Mi ON A.Dui = Mi.Dui
            WHERE Mi.Grupo = %s
        """, conn, params=[grupo_sel])

        # Mapear montos por miembro (si no existe, 0)
        ahorros_map = {row.Dui: float(row.Monto_actual) for row in df_ahorros.itertuples()} if not df_ahorros.empty else {}
        df_miembros["Ahorro_actual"] = df_miembros["Dui"].map(ahorros_map).fillna(0.0)

        total_ahorros_grupo = df_miembros["Ahorro_actual"].sum()

        # -------------------------
        # Multas pagadas
        # -------------------------
        df_multas = pd.read_sql_query("""
            SELECT M.Monto
            FROM MULTA M
            INNER JOIN Miembro Mi ON M.Dui = Mi.Dui
            WHERE Mi.Grupo = %s AND M.Estado = 'Pagada'
        """, conn, params=[grupo_sel])
        total_multas_pagadas = float(df_multas["Monto"].sum()) if not df_multas.empty else 0.0

        # -------------------------
        # Pagos de préstamos (capital) por grupo
        # -------------------------
        df_pagos = pd.read_sql_query("""
            SELECT Pa.ID_Pago, Pa.ID_Prestamo, Pa.Monto
            FROM PAGO Pa
            INNER JOIN PRESTAMO Pr ON Pa.ID_Prestamo = Pr.ID_Prestamo
            INNER JOIN Miembro Mi ON Pr.Dui = Mi.Dui
            WHERE Mi.Grupo = %s
        """, conn, params=[grupo_sel])
        total_pagos_capital = float(df_pagos["Monto"].sum()) if not df_pagos.empty else 0.0

        # -------------------------
        # Interés cobrado proporcionalmente por préstamos del grupo
        # -------------------------
        # Para cada préstamo del grupo: obtener Monto (capital) e Intereses (total a cobrar) y sum pagos hechos
        df_prestamos = pd.read_sql_query("""
            SELECT Pr.ID_Prestamo, Pr.Monto AS Capital, Pr.Intereses AS Interes_Total
            FROM PRESTAMO Pr
            INNER JOIN Miembro Mi ON Pr.Dui = Mi.Dui
            WHERE Mi.Grupo = %s
        """, conn, params=[grupo_sel])

        total_interes_cobrado = 0.0
        if not df_prestamos.empty:
            # obtener sumas de pagos por préstamo (solo los pagos relacionados)
            pagos_por_prestamo = df_pagos.groupby("ID_Prestamo")["Monto"].sum().to_dict() if not df_pagos.empty else {}

            for row in df_prestamos.itertuples():
                prestamo_id = row.ID_Prestamo
                capital = float(row.Capital) if row.Capital is not None else 0.0
                interes_total = float(row.Interes_Total) if row.Interes_Total is not None else 0.0

                pagos_hechos = float(pagos_por_prestamo.get(prestamo_id, 0.0))
                proporcion = (pagos_hechos / capital) if capital > 0 else 0.0
                if proporcion > 1:
                    proporcion = 1.0  # no exceder 100%

                interes_cobrado = interes_total * proporcion
                total_interes_cobrado += interes_cobrado

        # -------------------------
        # Totales generales
        # -------------------------
        total_ingresos = total_multas_pagadas + total_pagos_capital + total_interes_cobrado
        total_fondo = total_ahorros_grupo + total_ingresos
        monto_por_miembro = (total_fondo / n_miembros) if n_miembros > 0 else 0.0

        # Mostrar resumen
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Ahorros (grupo)", f"${total_ahorros_grupo:,.2f}")
        col2.metric("Total Multas Pagadas", f"${total_multas_pagadas:,.2f}")
        col3.metric("Total Pagos (capital)", f"${total_pagos_capital:,.2f}")

        st.write(f"**Total intereses cobrados (proporcional):** ${total_interes_cobrado:,.2f}")
        st.write(f"**Total ingresos (multas + pagos + intereses):** ${total_ingresos:,.2f}")
        st.write(f"**Total Fondo (ahorros + ingresos):** ${total_fondo:,.2f}")
        st.write(f"**Miembros en grupo:** {n_miembros}")
        st.write(f"**Monto equivalente por miembro (Total Fondo / miembros):** ${monto_por_miembro:,.2f}")

        st.markdown("---")

        # -------------------------
        # Panel para asignar saldo inicial del siguiente ciclo (editable por miembro)
        # -------------------------
        st.subheader("Asignar / Ajustar saldo inicial para cada miembro (siguiente ciclo)")
        st.info("El valor por defecto es la porción proporcional (monto equivalente por miembro). Puedes editar manualmente cada valor antes de guardar.")

        # Preparar dataframe con valores por miembro
        df_miembros["Porcion_equivalente"] = monto_por_miembro
        df_miembros["Saldo_inicial_siguiente"] = df_miembros["Porcion_equivalente"]  # valor por defecto (editable)

        # Mostrar inputs editables por fila
        saldos_manual = {}
        for idx, row in df_miembros.iterrows():
            dui = row["Dui"]
            nombre = f"{row['Nombre']} {row['Apellido']}"
            default_val = float(row["Porcion_equivalente"])
            # Usamos number_input con key único
            val = st.number_input(f"{nombre} (DUI: {dui}) - Saldo inicio siguiente ciclo", min_value=0.0, step=0.01, format="%.2f", value=default_val, key=f"sald_{dui}")
            saldos_manual[dui] = float(val)

        st.markdown("---")

        # -------------------------
        # Crear nuevo ciclo siguiente o seleccionar uno existente para asignar saldos
        # -------------------------
        st.subheader("Guardar saldos y cerrar ciclo")
        st.write("Puedes crear un nuevo ciclo siguiente (recomendado) o asignar estos saldos a un ciclo ya existente.")

        # Opción: crear un nuevo ciclo siguiente automáticamente
        crear_siguiente = st.checkbox("Crear un nuevo ciclo siguiente automáticamente y asignar estos saldos", value=True)
        next_cycle_id = None
        if crear_siguiente:
            fecha_inicio_next = st.date_input("Fecha inicio del siguiente ciclo", value=date.today())
            fecha_fin_next = st.date_input("Fecha fin del siguiente ciclo (opcional)", value=None, key="fin_next")
            estado_next = st.selectbox("Estado del siguiente ciclo", ["Pendiente", "Activo"], index=0)
            utilidad_next = st.number_input("Utilidad total (opcional) del siguiente ciclo", min_value=0.0, step=0.01, format="%.2f", key="util_next")
        else:
            # seleccionar ciclo existente (para asignar saldos)
            df_ciclos2 = pd.read_sql_query("SELECT ID_Ciclo, Fecha_inicio, Fecha_fin, Estado FROM CICLO ORDER BY ID_Ciclo DESC", conn)
            opciones_exist = ["-- Seleccionar --"] + [f"{int(r.ID_Ciclo)} | {r.Fecha_inicio} - {r.Fecha_fin or '...'} ({r.Estado})" for r in df_ciclos2.itertuples()]
            sel_exist = st.selectbox("Selecciona ciclo existente donde asignar saldos", opciones_exist)
            if sel_exist != "-- Seleccionar --":
                next_cycle_id = int(sel_exist.split("|")[0].strip())

        # Botón final: cerrar ciclo actual (si aplica) y guardar saldos
        if st.button("🔒 Cerrar ciclo actual y guardar saldos"):
            try:
                # Si el usuario optó por crear siguiente ciclo, insertarlo primero
                if crear_siguiente:
                    utilidad_val = float(utilidad_next) if utilidad_next > 0 else None
                    cursor.execute(
                        "INSERT INTO CICLO (Fecha_inicio, Fecha_fin, Estado, Utilidad_Total) VALUES (%s, %s, %s, %s)",
                        (fecha_inicio_next, fecha_fin_next, estado_next, utilidad_val)
                    )
                    conn.commit()
                    next_cycle_id = cursor.lastrowid

                # Guardar saldos en SALDO_CICLO para el next_cycle_id
                if next_cycle_id is None:
                    st.error("No se especificó un ciclo siguiente para asignar saldos. Marca crear nuevo ciclo o selecciona uno existente.")
                else:
                    # Inserciones por miembro
                    inserted = 0
                    for dui, saldo_val in saldos_manual.items():
                        # comprobar existencia previa (evitar duplicados)
                        cursor.execute(
                            "SELECT COUNT(*) FROM SALDO_CICLO WHERE DUI = %s AND ID_Ciclo = %s",
                            (dui, next_cycle_id)
                        )
                        exists = cursor.fetchone()[0]
                        if exists:
                            # actualizar
                            cursor.execute(
                                "UPDATE SALDO_CICLO SET Saldo_Inicio = %s WHERE DUI = %s AND ID_Ciclo = %s",
                                (saldo_val, dui, next_cycle_id)
                            )
                        else:
                            cursor.execute(
                                "INSERT INTO SALDO_CICLO (DUI, ID_Ciclo, Saldo_Inicio) VALUES (%s, %s, %s)",
                                (dui, next_cycle_id, saldo_val)
                            )
                        inserted += 1

                    # Opcional: marcar el ciclo seleccionado (id_ciclo_sel) como Finalizado y guardar utilidad_total
                    if id_ciclo_sel:
                        # actualizar fecha_fin a hoy y estado a Finalizado y Utilidad_Total opcional con ingresos calculados
                        hoy = date.today()
                        try:
                            cursor.execute(
                                "UPDATE CICLO SET Fecha_fin = %s, Estado = %s, Utilidad_Total = %s WHERE ID_Ciclo = %s",
                                (hoy, "Finalizado", float(total_ingresos), id_ciclo_sel)
                            )
                            conn.commit()
                        except Exception:
                            conn.rollback()
                            # no fatal: continuar

                    conn.commit()
                    st.success(f"✅ Saldos guardados para {inserted} miembros en el ciclo {next_cycle_id}.")
                    st.info(f"Se asignó ${total_fondo:,.2f} como Fondo total; ${monto_por_miembro:,.2f} por miembro (por defecto).")
                    st.experimental_rerun()

            except Exception as e:
                conn.rollback()
                st.error(f"❌ Error al guardar saldos o cerrar ciclo: {e}")

    except Exception as e:
        st.error(f"❌ Error general: {e}")

    finally:
        if conn is not None:
            try:
                conn.close()
            except:
                pass
