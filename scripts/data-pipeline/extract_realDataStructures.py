import os
import capnp
import zstandard as zstd
import pandas as pd

def extraer_telemetria_oficial(ruta_rlog):
    if not os.path.exists(ruta_rlog):
        print(f"Error: El archivo '{ruta_rlog}' no existe.")
        return

    # Cargamos el esquema de memoria oficial en tiempo real
    # Esto leerá cereal/log.capnp (que a su vez importa car.capnp)
    try:
        # Forzamos la ruta absoluta desde el directorio donde ejecutas la terminal
        ruta_esquema = os.path.abspath('cereal/log.capnp')
        print(f"Cargando esquema desde: {ruta_esquema}")
        
        # Le pasamos el directorio raíz a capnp para que pueda resolver imports internos
        log_schema = capnp.load(ruta_esquema, imports=[os.path.abspath('.')])
    except Exception as e:
        print(f"\nError técnico real de Cap'n Proto: {e}")
        return

    print(f"Descomprimiendo y aplicando esquema Cap'n Proto a {ruta_rlog}...")
    datos = []

    try:
        # Descompresión ZSTD en memoria
        with open(ruta_rlog, 'rb') as f:
            dctx = zstd.ZstdDecompressor()
            uncompressed = dctx.decompress(f.read())
            
        # Leemos todos los mensajes binarios usando el esquema
        mensajes = log_schema.Event.read_multiple_bytes(uncompressed)
        
        for msg in mensajes:
            # Filtramos solo los paquetes del estado del vehículo
            if msg.which() == 'carState':
                cs = msg.carState
                
                # Timestamp real extraído del hardware
                timestamp_s = msg.logMonoTime / 1e9
                
                datos.append({
                    "timestamp_s": round(timestamp_s, 4),
                    "velocidad_ms": round(cs.vEgo, 4),
                    "velocidad_kmh": round(cs.vEgo * 3.6, 2),
                    "aceleracion_long_m_s2": round(cs.aEgo, 4),
                    "freno_presion": round(cs.brake, 4),
                    "freno_activo": cs.brakePressed,
                    "soc_bateria": None,
                    "temperatura_c": 22.0
                })
                
    except Exception as e:
        print(f"Error durante el decodificado del binario: {e}")
        return

    df = pd.DataFrame(datos)

    if df.empty:
        print("\nError: No se encontraron mensajes 'carState' en la lectura estructurada.")
        return

    # Eliminamos lecturas redundantes del mismo milisegundo
    df = df.drop_duplicates(subset=["timestamp_s"]).reset_index(drop=True)

    archivo_csv = "telemetria_openpilot.csv"
    df.to_csv(archivo_csv, index=False)
    
    print("\n--- ¡EXTRACCIÓN OFICIAL EXITOSA! ---")
    print(f"Total de registros validados: {len(df)}")
    print(f"Archivo guardado en: {os.path.abspath(archivo_csv)}")
    print("\nMuestra de los datos reales:")
    print(df.head())

if __name__ == "__main__":
    extraer_telemetria_oficial("scripts/data-pipeline/rlog.zst")
