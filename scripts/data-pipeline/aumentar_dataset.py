import pandas as pd
import numpy as np
import sys
try:
    df_base=pd.read_csv('data/processed/telemetria_filtrada_lista_para_ml.csv')
    print("Dataset original cargado correctamente")
except FileNotFoundError:
    print("Error: No se encontró el archivo 'telemetria_filtrada_lista_para_ml.csv'. Asegúrate de que el archivo exista en la ruta 'data/processed/'.")
    sys.exit()

#correction the base physical, the mismatch fusion sensor
dt_dinamico=df_base['timestamp_ns'].diff()/1e9
df_base['aceleracion_long_m_s2']=df_base['velocidad_ms'].diff()/dt_dinamico
df_base['aceleracion_long_m_s2']=df_base['aceleracion_long_m_s2'].replace([np.inf, -np.inf],0.0).fillna(0.0)
df_base['velocidad_promedio_5s']=df_base['velocidad_ms'].rolling(window=50, min_periods=1).mean()
df_base['aceleracion_promedio_5s']=df_base['aceleracion_long_m_s2'].rolling(window=50, min_periods=1).mean()

df_highway=df_base.copy()
#adding random noise to the highway dataset to simulate real-world conditions, natural dispersion aprox +- 1.5
df_highway['velocidad_ms']=df_highway['velocidad_ms']+22.0
df_highway['aceleracion_long_m_s2']=df_highway['velocidad_ms'].diff()/dt_dinamico
ruido_highway=np.random.normal(loc=0.0, scale=0.5, size=len(df_highway))
df_highway['velocidad_ms']=df_highway['velocidad_ms']+ruido_highway
df_highway['aceleracion_long_m_s2']=df_highway['aceleracion_long_m_s2'].replace([np.inf, -np.inf],0.0).fillna(0.0)
df_highway['velocidad_promedio_5s']=df_highway['velocidad_ms'].rolling(window=50, min_periods=1).mean()
df_highway['aceleracion_promedio_5s']=df_highway['aceleracion_long_m_s2'].rolling(window=50, min_periods=1).mean()

df_panic=df_base.copy()
delta_v=df_panic['velocidad_ms'].diff()
#simulate braking forcing velocity to decrease, just where there was a decrease in real data
delta_v_modificado=np.where((delta_v < 0)&(df_panic['freno_activo']==True), delta_v*15.0, delta_v)
#reconstruct the velocity with the modified delta_v
velocidad_reconstruida=pd.Series(df_panic['velocidad_ms'].iloc[0]+np.cumsum(np.nan_to_num(delta_v_modificado)))
df_panic['aceleracion_long_m_s2']=(velocidad_reconstruida.diff()/dt_dinamico)
ruido_sensor=np.random.normal(0.0, 0.5, len(df_panic))
df_panic['velocidad_ms']=velocidad_reconstruida+10.0+ruido_sensor
df_panic['velocidad_ms']=df_panic['velocidad_ms'].clip(lower=0.0)
#limit to the physical limit of the vehicle clipping the acceleration
df_panic['aceleracion_long_m_s2']=df_panic['aceleracion_long_m_s2'].clip(lower=-10.0,upper=4.0)
df_panic['aceleracion_long_m_s2']=df_panic['aceleracion_long_m_s2'].replace([np.inf, -np.inf],0.0).fillna(0.0)
df_panic['freno_activo']=np.where(df_panic['aceleracion_long_m_s2'] < -3.0, True, df_panic['freno_activo'])
df_panic['velocidad_promedio_5s']=df_panic['velocidad_ms'].rolling(window=50, min_periods=1).mean()
df_panic['aceleracion_promedio_5s']=df_panic['aceleracion_long_m_s2'].rolling(window=50, min_periods=1).mean()
df_aumentado=pd.concat([df_base, df_highway, df_panic], ignore_index=True)
df_aumentado.to_csv('data/processed/telemetria_filtrada_lista_para_ml_aumentado.csv', index=False)
print("Dataset aumentado guardado correctamente en 'telemetria_filtrada_lista_para_ml_aumentado.csv'")
print(f"filas originales: {len(df_base)}")
print(f"nuevas filas totales: {len(df_aumentado)}")
print(df_aumentado.head())
