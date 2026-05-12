import json
import os

# Recibe el bloque de texto que copiaste del gestor
datos_raw = os.environ.get('BLOQUE_JSON')
nuevos_productos = json.loads(datos_raw)

archivo = 'manuales.json'
productos_actuales = []

if os.path.exists(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        productos_actuales = json.load(f)

# Unimos lo que ya tenías con lo nuevo
productos_actuales.extend(nuevos_productos)

# Guardamos
with open(archivo, 'w', encoding='utf-8') as f:
    json.dump(productos_actuales, f, ensure_ascii=False, indent=4)

print(f"Se han guardado {len(nuevos_productos)} productos con éxito.")
