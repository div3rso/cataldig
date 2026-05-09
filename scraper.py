import requests
from bs4 import BeautifulSoup
import json
import os

# La dirección del catálogo público
url = "https://ñigicorp.com" 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def obtener_productos():
    print("Iniciando la extracción de productos...")
    try:
        respuesta = requests.get(url, headers=headers)
        respuesta.raise_for_status()
        sopa = BeautifulSoup(respuesta.text, 'html.parser')
        
        productos = []
        
        # --- BÚSQUEDA ROBUSTA DE PRODUCTOS ---
        # Buscaremos primero por patrones comunes de productos en tiendas online.
        
        # Intentamos encontrar los "items" del catálogo directamente por clases comunes
        # de elementos que *contienen* información del producto.
        tarjetas = (
            sopa.find_all('div', class_=lambda x: x and 'product' in x and ('item' in x or 'block' in x or 'grid' in x))
            or sopa.find_all('li', class_=lambda x: x and 'product' in x and ('item' in x or 'block' in x or 'grid' in x))
        )
        
        # Si la búsqueda robusta no encuentra nada, volvemos a la simple por si acaso.
        if not tarjetas:
            print("Intento con selectores robusos falló. Intentando con selectores simples.")
            tarjetas = sopa.find_all('div', class_='product-item') or sopa.find_all('div', class_='product-grid-item')
            
        print(f"Número de tarjetas de producto encontradas: {len(tarjetas)}")

        for tarjeta in tarjetas:
            # Extraemos nombre de forma robusta
            nombre_elem = (
                tarjeta.find('a', class_=lambda x: x and 'product' in x and 'name' in x)
                or tarjeta.find(['h3', 'h4'], class_=lambda x: x and 'product' in x and 'name' in x)
                or tarjeta.find('a', class_='product-item-link')
            )
            
            # Extraemos imagen de forma robusta
            img_elem = (
                tarjeta.find('img', class_=lambda x: x and 'product' in x and 'image' in x)
                or tarjeta.find('img', class_='product-item-image')
                or tarjeta.find('img')
            )
            
            if nombre_elem and img_elem:
                nombre = nombre_elem.text.strip()
                # Limpieza de nombre en caso de que sea un enlace
                if len(nombre) > 150:
                    nombre = nombre[:147] + "..."
                    
                imagen = img_elem.get('src', 'https://via.placeholder.com/200?text=Sin+Imagen')
                
                # Corrección de URL de imagen si es relativa
                if imagen and not imagen.startswith(('http://', 'https://')):
                    # La url de Digicorp es https://digicorp.com.bo/marcas
                    base_url = url.split("//")[1].split("/")[0]
                    imagen = f"https://{base_url}{imagen}" if not imagen.startswith('/') else f"https://{base_url}/{imagen}"

                # Asegurar que el nombre no esté vacío antes de añadir
                if nombre:
                    productos.append({
                        "nombre": nombre,
                        "imagen": imagen
                    })
                    # print(f"Producto encontrado: {nombre}") # Descomentar para depurar más
                
        # Guardar en un archivo JSON que leerá el HTML
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(productos, f, ensure_ascii=False, indent=4)
            
        print(f"Éxito: Se guardaron {len(productos)} productos válidos en productos.json")
        
    except Exception as e:
        print(f"Error durante la extracción: {e}")

if __name__ == "__main__":
    obtener_productos()
