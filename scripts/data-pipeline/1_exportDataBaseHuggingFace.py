
import json
import os
from huggingface_hub import hf_hub_download

def filtrar_dataset_openpilot():
    print("Iniciando descarga segura de 'database.json' desde Hugging Face...")

    try:
        # Download the original manifest
        archivo_local=hf_hub_download(
            repo_id="commaai/commaCarSegments",
            repo_type="dataset",
            filename="database.json"
        )

        with open(archivo_local,'r',encoding='utf-8') as f:
            database=json.load(f)
        print("¡Manifiesto cargado con éxito!\n")

    except Exception as e:
        print(f"Error crítico: {e}")
        return

    # Confirmed models in the catalog
    modelos_objetivo=[
        "CHEVROLET_BOLT_EUV",
        "CHEVROLET_BOLT",
        "TOYOTA_PRIUS",
        "HYUNDAI_IONIQ_5",
        "TESLA_MODEL_3"
    ]

    segmentos_encontrados=[]

    # Force the slash using its hexadecimal code \x2f so the formatter does not alter it
    slash="\x2f"
    url_base="https:"+slash+slash+"huggingface.co"+slash+"datasets"+slash+"commaai"+slash+"commaCarSegments"+slash+"resolve"+slash+"main"+slash+"segments"+slash

    # Process the string list directly
    for plataforma in modelos_objetivo:
        if plataforma in database:
            rutas_lista=database[plataforma]

            for elemento in rutas_lista:
                partes=elemento.split('/')

                if len(partes)>=3:
                    dongle_id=partes[0]
                    route_hash=partes[1]
                    seg_index=partes[2]

                    # Direct manual assembly by joining the pieces
                    url_download=url_base+dongle_id+slash+route_hash+slash+seg_index+slash+"rlog.zst"

                    segmentos_encontrados.append({
                        "coche": plataforma,
                        "url": url_download
                    })

    total=len(segmentos_encontrados)
    print("--- BÚSQUEDA FINALIZADA: "+str(total)+" segmentos encontrados ---\n")

    if total==0:
        print("No se encontraron segmentos. Verifica si cambiaste los nombres en 'modelos_objetivo'.")
        return

    print("Muestra de los primeros 3 enlaces corregidos y listos para descargar:")
    print("-" * 80)
    for seg in segmentos_encontrados[:3]:
        print(" Vehículo: "+seg['coche'])
        print(" Enlace:   "+seg['url'])
        print("-" * 80)

    # Guardar todos los enlaces generados en el archivo de texto
    archivo_salida="enlaces_descarga.txt"
    with open(archivo_salida,"w") as f_out:
        for seg in segmentos_encontrados:
            f_out.write(seg['url']+"\n")

    print("\nLista guardada con éxito en '"+archivo_salida+"'.")
    print("Para descargar el primer archivo de prueba ejecute:\nhead -n 1 enlaces_descarga.txt | xargs wget")

if __name__=="__main__":
    filtrar_dataset_openpilot()
