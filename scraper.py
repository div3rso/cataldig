import requests
from bs4 import BeautifulSoup
import json
import os

# La dirección del catálogo público
url = "https://digicorp.com.bo/" 
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
        
        # NOTA: Estas etiquetas (div, class) pueden variar dependiendo de cómo 
        # esté construida exactamente la web de Digicorp por dentro.
        # Este es un bloque genérico de búsqueda.
        tarjetas = sopa.find_all('div', class_='product-card') # Ajustar según el código real de la web
        
        for tarjeta in tarjetas:
            # Extraemos nombre e imagen. Ignoramos el precio.
            nombre_elem = tarjeta.find('h3')
            img_elem = tarjeta.find('img')
            
            if nombre_elem and img_elem:
                productos.append({
                    "nombre": nombre_elem.text.strip(),
                    "imagen": img_elem.get('src', 'https://via.placeholder.com/200?text=Sin+Imagen')
                })
                
        # Guardar en un archivo JSON que leerá el HTML
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(productos, f, ensure_ascii=False, indent=4)
            
        print(f"Éxito: Se guardaron {len(productos)} productos en productos.json")
        
    except Exception as e:
        print(f"Error durante la extracción: {e}")

if __name__ == "__main__":
    obtener_productos()
