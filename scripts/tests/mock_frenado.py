import pandas as pd
import numpy as np
import sys
try:
    df=pd.read_csv('data/processed/telemetria_filtrada_lista_para_ml_aumentado.csv')
    print("Archivo de telemetría filtrada cargado correctamente desde 'data/processed/telemetria_filtrada_lista_para_ml.csv'")
except FileNotFoundError:
    print("Archivo de telemetría filtrada no encontrado. Por favor, asegúrese de que el archivo exista en 'data/processed/telemetria_filtrada_lista_para_ml.csv'")
    sys.exit()
conditions_context = [
    (df['aceleracion_promedio_5s'] < -2.0),
    (df['velocidad_promedio_5s'] > 20.0)]
options_context = ['Deceleration','Highway']
df['contexto_conduccion'] = np.select(conditions_context, options_context, default='Urban')
conditions_freno=[
        (df['freno_activo']==False),
        (df['freno_activo']==True) & (df['contexto_conduccion']=='Urban'),
        (df['freno_activo']==True) & (df['contexto_conduccion']=='Highway'),
        (df['freno_activo']==True) & (df['contexto_conduccion']=='Deceleration')]
options_regen=[0.0,0.8,0.4,0.0]
options_mecanico=[0.0,0.2,0.6,1.0]
df['frena_regenerativo_pct']=np.select(conditions_freno, options_regen, default=0.0)
df['frena_mecanico_pct']=np.select(conditions_freno, options_mecanico, default=0.0)
ruta_mock='data/telemetria_mock_para_interfaz.csv'
df.to_csv(ruta_mock,index=False)
print(f"Archivo de telemetrías mock generado y guardado en '{ruta_mock}'")
print("mostrar las primeras filas del archivo mock generado:")
print(df.head(5))


