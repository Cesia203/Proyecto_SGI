import pandas as pd
from modulos.reportes_db import (
    get_promotoras_list,
    get_grupo_info_by_promotora_id,
    get_ahorros_reporte,
    get_prestamos_reporte,
    get_multas_reporte
)

def generar_reporte_ahorros(ID_Grupo):
    """Muestra el reporte de ahorros en Streamlit."""
    ahorros, total = get_ahorros_reporte(ID_Grupo)
    
    if ahorros:
        st.subheader("📊 Reporte de Ahorros")
        
        # Crear DataFrame para mejor visualización
        df = pd.DataFrame(
            ahorros,
            columns=["Nombre", "Apellido", "Monto Actual"]
        )
        
        # Formato de moneda
        df["Monto Actual"] = df["Monto Actual"].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(df, use_container_width=True)
        st.success(f"💰 **TOTAL Ahorrado por el Grupo:** **${total:,.2f}**")
    else:
        st.info("No hay registros de ahorros para este grupo.")

def generar_reporte_prestamos(ID_Grupo):
    """Muestra el reporte de préstamos en Streamlit."""
    prestamos, total_saldo = get_prestamos_reporte(ID_Grupo)
    
    if prestamos:
        st.subheader("💸 Reporte de Préstamos")
        
        # Crear DataFrame
        df = pd.DataFrame(
            Prestamos,
            columns=["Nombre", "Apellido", "Monto Inicial", "Intereses (%)", "Saldo Restante"]
        )

        # Formato de moneda y porcentaje
        df["Monto Inicial"] = df["Monto Inicial"].apply(lambda x: f"${x:,.2f}")
        df["Saldo Restante"] = df["Saldo Restante"].apply(lambda x: f"${x:,.2f}")
        df["Intereses (%)"] = df["Intereses (%)"].apply(lambda x: f"{x:,.2f}%")
        
        st.dataframe(df, use_container_width=True)
        st.warning(f"🏦 **TOTAL Saldo Restante del Grupo:** **${total_saldo:,.2f}**")
    else:
        st.info("No hay préstamos activos registrados para este grupo.")

def generar_reporte_multas(ID_Grupo):
    """Muestra el reporte de multas en Streamlit."""
    multas, total_pendientes = get_multas_reporte(ID_Grupo)
    
    if Multas:
        st.subheader("🚨 Reporte de Multas Pendientes")
        
        # Crear DataFrame
        df = pd.DataFrame(
            multas,
            columns=["Nombre", "Apellido", "Tipo", "Monto", "Estado", "Fecha"]
        )

        # Formato de moneda
        df["Monto"] = df["Monto"].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(df, use_container_width=True)
        st.error(f"❌ **TOTAL Multas Pendientes del Grupo:** **${total_pendientes:,.2f}**")
    else:
        st.info("No hay multas pendientes registradas para este grupo.")

def gestionar_promotora():
    st.title("👩‍💼 Módulo de Promotoría y Reportes")
    st.markdown("---")

    promotoras = get_promotoras_list()
    
    if not promotoras:
        st.warning("No hay promotoras registradas en la base de datos.")
        return

    # Mapeo de promotoras para el selectbox
    promotora_options = {f"{p[1]} {p[2]} (ID: {p[0]})": p[0] for p in promotoras}
    
    # 1. Selector de Promotora
    promotora_seleccionada_key = st.selectbox(
        "Seleccione la Promotora a Consultar",
        ["Seleccione Promotora"] + list(promotora_options.keys())
    )
    
    if promotora_seleccionada_key != "Seleccione Promotora":
        promotora_id = promotora_options[promotora_seleccionada_key]
        
        # 2. Obtener información del grupo asignado
        grupo_info = get_grupo_info_by_promotora_id(promotora_id)
        
        if grupo_info:
            id_grupo, nombre_grupo = grupo_info
            
            st.info(f"Asignación: Esta promotora gestiona el grupo **{nombre_grupo}** (ID: {ID_Grupo}).")
            st.markdown("---")
            
            # 3. Pestañas para los Reportes
            tab_ahorros, tab_prestamos, tab_multas = st.tabs(["💰 Ahorros", "💸 Préstamos", "🚨 Multas"])
            
            with tab_ahorros:
                generar_reporte_ahorros(ID_Grupo)
            
            with tab_prestamos:
                generar_repo
