import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
try:
    global df
    df=pd.read_csv('data/raw/telemetria_openpilot.csv')
except FileNotFoundError:
    print("File not found. Please check the file path")
    sys.exit()

def kalman_filter_1d(x,P,Q,R,z):
    # Prediction step
    x_pred=x
    P_pred=P+Q
    # Update step
    K=P_pred/(P_pred+R)
    x=x_pred+K*(z-x_pred)
    P=P_pred*(1-K)
    return x,P

x=df['velocidad_ms'].iloc[0]  # Initial state estimate
P=1.0  # Initial estimate uncertainty
Q=1e-5  # Process noise covariance
R=0.01  # Measurement noise covariance

velocidades_limpias=[]
for z in df['velocidad_ms']:
    x,P=kalman_filter_1d(x,P,Q,R,z)
    velocidades_limpias.append(x)

df['velocidad_filtrada_ms']=velocidades_limpias

columnas_finales=['timestamp_ns','velocidad_filtrada_ms','aceleracion_long_m_s2','freno_activo']
df_limpio=df[columnas_finales].copy()
df_limpio=df_limpio.rename(columns={'velocidad_filtrada_ms':'velocidad_ms'})
df_limpio.to_csv('data/processed/telemetria_filtrada_lista_para_ml.csv',index=False)
print("Archivo de telemetría filtrada guardado en 'data/processed/telemetria_filtrada_lista_para_ml.csv'")

plt.figure(figsize=(12,6))
plt.plot(df['velocidad_ms'],label='Señal Cruda (Sensor / Carving)',color='red',alpha=0.5,linestyle='--')
plt.plot(df['velocidad_filtrada_ms'],label='Señal Filtrada (Kalman)',color='blue',linewidth=2)
plt.title('Validación de Extracción de Telemetría: Velocidad')
plt.xlabel('Muestras (Frecuencia de 10Hz)')
plt.ylabel('Velocidad (m/s)')
plt.legend()
plt.grid(True)
plt.show()
