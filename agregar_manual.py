import json
import os

nombre = os.environ.get('PROD_NOMBRE')
imagen = os.environ.get('PROD_IMAGEN')
categoria = os.environ.get('PROD_CATEGORIA')

archivo = 'manuales.json'
productos = []

# Si la bóveda ya existe, la abrimos
if os.path.exists(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        productos = json.load(f)

# Guardamos tu nuevo producto
productos.append({
    "nombre": nombre,
    "imagen": imagen,
    "categoria": categoria
})

# Cerramos la bóveda
with open(archivo, 'w', encoding='utf-8') as f:
    json.dump(productos, f, ensure_ascii=False, indent=4)

print(f"¡Éxito! El producto '{nombre}' se guardó en tu bóveda manual.")
