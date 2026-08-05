import pandas as pd
import numpy as np
import os
def aplicar_modelo_fisico(ruta_entrada, ruta_salida):
    print(f"Aplicando modelo físico inverso a {ruta_entrada}...")
    df=pd.read_csv(ruta_entrada)
    #parametros fisicos del vehiculo
    mass_kg=1700.0 #masa del vehiculo en kg
    rho=1.225 #densidad del aire en kg/m^3
    Cd=0.28 #coeficiente de arrastre
    A=2.2 #area frontal del vehiculo en m^2
    battery_capacity_J=60*3.6e6 #bateria de 60 kWh en Joules
    eff_motor=0.9 #90% de eficiencia en traccion
    eff_regen=0.65 #65% de eficiencia en frenado regenerativo
    #calcular el delta del tiempo real en segundos a partir de los nanosegundos
    df['dt_s']=df['timestamp_ns'].diff().div(1e9).fillna(0.1)
    df['dt_s']=df['dt_s'].replace(0,0.1)
    #dinamica longitudinal del vehiculo
    #fuerza aerodinamica y fuerza total de traccion
    df['F_aero_N']=0.5*rho*Cd*A*(df['velocidad_ms']**2)
    df['F_tract_N']=(mass_kg*df['aceleracion_long_m_s2'])+df['F_aero_N']
    #potencia en watts P=F*v
    df['Power_W']=df['F_tract_N']*df['velocidad_ms']
    #consumo de energia y SoC
    #si Power es positivo, consume (divide entre eficiencia) si el Power es negativo, regenera (multiplica por eficiencia)
    df['Energy_J']=np.where(df['Power_W']>0,df['Power_W']*df['dt_s']/eff_motor,df['Power_W']*df['dt_s']*eff_regen)
    df['Cumulaitive_Energy_J']=df['Energy_J'].cumsum()
    #inicia en 85% y resta el porcentaje consumido
    soc_start=85.0
    df['soc_bateria']=soc_start-(df['Cumulaitive_Energy_J']/battery_capacity_J)*100
    #modelo termico
    #el calor es la energia que se pierde por la ineficiencia
    df['Heat_J']=np.where(df['Power_W']>0,df['Power_W']*(1-eff_motor)*df['dt_s'],abs(df['Power_W'])*(1-eff_regen)*df['dt_s'])
    C_thermal=250000 #capacidad termica estimada del paquete de baterias
    k_cooling=0.01 #tasa de enfriamento
    T_ambient=22.0 #temperatura ambiente en grados Celsius
    temps=[T_ambient]
    for i in range(1,len(df)):
        dT_heat=df.loc[i,'Heat_J']/C_thermal
        dT_cool=k_cooling*(temps[-1]-T_ambient)*df.loc[i,'dt_s']
        temps.append(temps[-1]+dT_heat-dT_cool)
    df['temperatura_c']=temps
    #redondear
    df['soc_bateria']=df['soc_bateria'].round(4)
    df['temperatura_c']=df['temperatura_c'].round(4)
    #descartar columnas de calculo intermedias
    df_clean=df.drop(columns=['dt_s','F_aero_N','F_tract_N','Power_W','Energy_J','Cumulaitive_Energy_J','Heat_J'])
    #guardar resultados
    df_clean.to_csv(ruta_salida,index=False)
    print(f"Modelo físico aplicado y resultados guardados en {ruta_salida}")
    print("\nMuestra de los primeros 5 registros del DataFrame resultante:")
    print(df_clean[['velocidad_ms', 'aceleracion_long_m_s2', 'soc_bateria', 'temperatura_c']].head(5))

if __name__ == "__main__":
    directorio_script = os.path.dirname(os.path.abspath(__file__))
    raiz_proyecto = os.path.dirname(os.path.dirname(directorio_script))
    ruta_entrada = os.path.join(raiz_proyecto, "data/raw/telemetria_openpilot.csv")
    ruta_salida = os.path.join(raiz_proyecto, "data/raw/telemetria_openpilot_fisica.csv")
    aplicar_modelo_fisico(ruta_entrada, ruta_salida)
