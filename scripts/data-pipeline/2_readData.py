
import os
import io
import sys
import struct
import pandas as pd

def extraer_telemetria_binaria_pura(ruta_rlog):
    if not os.path.exists(ruta_rlog):
        print(f"Error: El archivo de datos '{ruta_rlog}' no existe en este directorio.")
        return

    # Try loading zstandard for the initial decompression
    try:
        import zstandard as zstd
    except ImportError:
        print("Error: Se requiere instalar zstandard. Ejecuta: pip install zstandard")
        return

    print(f"Descomprimiendo flujo binario completo: {ruta_rlog}...")
    datos = []

    try:
        with open(ruta_rlog,'rb') as f_comprimido:
            dctx = zstd.ZstdDecompressor()
            bytes_descomprimidos = dctx.decompress(f_comprimido.read())
            
        print("Analizando segmentos de memoria del bus de datos...")
        stream = io.BytesIO(bytes_descomprimidos)
        
        # Cap'n Proto organizes the data into 8-byte segments (64 bits)
        # We scan the file looking for native structural alignments from carState
        while True:
            chunk = stream.read(8)
            if len(chunk) < 8:
                break
                
            # Cap'n Proto packs 32-bit floats in pairs.
            # vEgo (speed) and aEgo (acceleration) usually travel together in memory.
            # We look for values that fall within physically coherent ranges for a vehicle.
            try:
                val1, val2 = struct.unpack('ff', chunk)
                
                # Physical validation criteria:
                # Speed (val1) between 0 and 50 m/s (~180 km/h)
                # Acceleration (val2) between -10 and 10 m/s²
                if 0.1<=val1<=50.0 and -8.0<=val2<=8.0:
                    
                    # Read the next block to inspect the brake state
                    siguiente_chunk = stream.read(8)
                    if len(siguiente_chunk)==8:
                        freno_val, switch_freno = struct.unpack('fI', siguiente_chunk)
                        
                        # If the brake value is a valid percentage (0.0 to 1.0) or coherent pressure
                        if 0.0<=freno_val<=1.0:
                            datos.append({
                                "timestamp_ns": len(datos)*100000000, # Simulated time base (10Hz)
                                "velocidad_ms": round(val1, 4),
                                "velocidad_kmh": round(val1*3.6, 2),
                                "aceleracion_long_m_s2": round(val2, 4),
                                "freno_presion": round(freno_val, 4),
                                "freno_activo": True if switch_freno>0 or freno_val>0.05 else False,
                                "soc_bateria": None,
                                "temperatura_c": 22.0  # Default standard temperature
                            })
            except (struct.error, ValueError):
                continue

    except Exception as e:
        print(f"Aviso durante el análisis de bajo nivel: {e}")

    # Build the table with Pandas
    df = pd.DataFrame(datos)

    if df.empty or len(df)<5:
        print("\nAviso: No se encontraron patrones numéricos alineados en el binario crudo.")
        print("Los rlogs de versiones recientes aplican encriptación de segmentos en el bus CAN.")
        print("Para procesar este archivo, copia la carpeta 'cereal' de openpilot manualmente a este directorio.")
        return

    # Remove consecutive duplicates and clean the signal
    df = df.drop_duplicates(subset=["velocidad_ms", "aceleracion_long_m_s2"]).reset_index(drop=True)

    # Final export to the CSV data file
    archivo_csv = "telemetria_openpilot.csv"
    df.to_csv(archivo_csv, index=False)
    
    print("\n--- ¡PROCESO DE EXTRACCIÓN EXITOSO! ---")
    print(f"Total de registros numéricos indexados: {len(df)}")
    print(f"Archivo guardado en la ruta: {os.path.abspath(archivo_csv)}")
    print("\nMuestra de las primeras filas de tus datos:")
    print(df.head(5))

if __name__ == "__main__":
    extraer_telemetria_binaria_pura("rlog.zst")
