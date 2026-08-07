import streamlit as st
import pandas as pd
import time

st.set_page_config(layout="wide", page_title="Simulador Freno Inteligente")

st.markdown("""
<style>
[data-testid="stMetric"] {
    background-color: #1E1E1E;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    text-align: center;
    margin-bottom: 20px;
}
[data-testid="stMetricLabel"] * {
    color: #888888 !important;
    font-size: 16px !important;
}
[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 32px !important;
}
</style>
""", unsafe_allow_html=True)

if 'simulando' not in st.session_state:
    st.session_state.simulando = False
if 'indice_actual' not in st.session_state:
    st.session_state.indice_actual = 0

st.sidebar.image("v_app/logo_tacos_de_buche.png", use_container_width=True)
st.sidebar.divider()
st.sidebar.markdown("### Controles de Simulación")

col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    if st.button("▶️ Play", use_container_width=True):
        st.session_state.simulando = True
with col_btn2:
    if st.button("⏸️ Pause", use_container_width=True):
        st.session_state.simulando = False

if st.sidebar.button("⏹️ Stop / Reiniciar", use_container_width=True):
    st.session_state.simulando = False
    st.session_state.indice_actual = 0

st.title("Panel de Control BYD")

try:
    df = pd.read_csv("data/telemetria_mock_para_interfaz.csv")
    df['energia_cinetica_rel'] = df['velocidad_ms'] ** 2
    df['potencia_teorica'] = df['velocidad_ms'] * df['aceleracion_long_m_s2']

    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    
    with col_izq:
        metrica_vel = st.empty()
        metrica_energia = st.empty()
        
    with col_centro:
        st.image("v_app/byd.png", use_container_width=True) 
        st.markdown("<br>", unsafe_allow_html=True)
        grafica_dinamica = st.empty()
        
    with col_der:
        metrica_potencia = st.empty()
        metrica_freno = st.empty()

    if not st.session_state.simulando:
        fila_actual = df.iloc[st.session_state.indice_actual]
        
        metrica_vel.metric("Velocidad", f"{fila_actual['velocidad_ms']:.2f} m/s")
        metrica_energia.metric("Energía Cinética Rel.", f"{fila_actual['energia_cinetica_rel']:.2f}")
        metrica_potencia.metric("Potencia Teórica", f"{fila_actual['potencia_teorica']:.2f} kW")
        
        estado = "🔴 ACTIVO" if fila_actual['freno_activo'] == 1 else "🟢 INACTIVO"
        metrica_freno.metric("Freno", estado)
        
        datos_recientes = df.iloc[max(0, st.session_state.indice_actual-50):st.session_state.indice_actual+1]
        grafica_dinamica.line_chart(datos_recientes[['velocidad_ms', 'aceleracion_long_m_s2']])
        
    else:
        for i in range(st.session_state.indice_actual, len(df)):
            st.session_state.indice_actual = i
            fila_actual = df.iloc[i]
            
            metrica_vel.metric("Velocidad", f"{fila_actual['velocidad_ms']:.2f} m/s")
            metrica_energia.metric("Energía Cinética Rel.", f"{fila_actual['energia_cinetica_rel']:.2f}")
            metrica_potencia.metric("Potencia Teórica", f"{fila_actual['potencia_teorica']:.2f} kW")
            
            estado = "🔴 ACTIVO" if fila_actual['freno_activo'] == 1 else "🟢 INACTIVO"
            metrica_freno.metric("Freno", estado)
            
            datos_recientes = df.iloc[max(0, i-50):i+1]
            grafica_dinamica.line_chart(datos_recientes[['velocidad_ms', 'aceleracion_long_m_s2']])
            
            time.sleep(1.0)
            
        st.session_state.simulando = False
        st.success("¡Simulación finalizada! Llegamos al final de los datos.")

except FileNotFoundError:
    st.error("Error: No se encontró el archivo CSV en 'data/telemetria_mock_para_interfaz.csv'.")