import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(layout="wide", page_title="Dashboard Freno Regenerativo")

st.title("Freno Inteligente Adaptativo - Hackathon CASE 4.0")
st.sidebar.title("Configuración")
st.sidebar.image("v_app/logo_tacos_de_buche.png", width=150)
st.sidebar.subheader("Equipo: tacos de buche")
ruta_csv = "data/processed/telemetria_filtrada_lista_para_ml.csv"

try:
    df = pd.read_csv(ruta_csv)
    
    # 1. Limpiamos la vista quitando la columna del timestamp que tiene números muy grandes
    if 'timestamp_ns' in df.columns:
        df_visual = df.drop(columns=['timestamp_ns'])
    else:
        df_visual = df
    
    # 2. Métricas adaptadas a las fórmulas físicas del proyecto
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Aquí calculamos el promedio real de la velocidad actual con los datos del CSV
        velocidad_prom = df['velocidad_ms'].mean()
        st.metric(label="Velocidad Promedio", value=f"{velocidad_prom:.2f} m/s")

    with col2:
        st.metric(label="Índice de Oportunidad", value="-- %", delta="Pendiente") 

    with col3:
        st.metric(label="Potencia Teórica", value="-- kW", delta="Pendiente") 

    with col4:
        st.metric(label="Eventos de Frenado", value="--", delta="Pendiente")
        
    st.divider()

    # 3. Gráfica interactiva de la velocidad y aceleración
    st.subheader("Comportamiento del Vehículo en Tiempo Real")
    # Streamlit grafica automáticamente las columnas que le pasemos
    st.line_chart(df_visual[['velocidad_ms', 'aceleracion_long_m_s2']])

    st.divider()

    # 4. Tabla de datos limpia
    st.subheader("Telemetría con Filtro de Kalman")
    st.dataframe(df_visual.head(15))

except FileNotFoundError:
    st.error("Error: No se encontró el archivo CSV.")