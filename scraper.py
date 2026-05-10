from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import time

# Mapa completo de categorías proporcionado
categorias_a_extraer = {
    "VIDEOVIGILANCIA": "https://www.digicorp.com.bo/producto/categoria/01010000",
    "CONTROL DE ACCESO": "https://www.digicorp.com.bo/producto/categoria/02010000",
    "ALARMAS Y DOMOTICA": "https://www.digicorp.com.bo/producto/categoria/03010000",
    "SISTEMAS ANTIHURTO": "https://www.digicorp.com.bo/producto/categoria/03020000",
    "PROTECCION PERIMETRAL": "https://www.digicorp.com.bo/producto/categoria/03030000",
    "DETECCION DE INCENDIO": "https://www.digicorp.com.bo/producto/categoria/03040000",
    "GPS": "https://www.digicorp.com.bo/producto/categoria/03050000",
    "REDES": "https://www.digicorp.com.bo/producto/categoria/04010000",
    "TELEFONIA": "https://www.digicorp.com.bo/producto/categoria/04020000",
    "RADIOCOMUNICACION": "https://www.digicorp.com.bo/producto/categoria/04030000",
    "CABLEADO ESTRUCTURADO Y FO.": "https://www.digicorp.com.bo/producto/categoria/05010000",
    "ENERGIA Y CABLES": "https://www.digicorp.com.bo/producto/categoria/05020000",
    "ILUMINACION Y SONIDO": "https://www.digicorp.com.bo/producto/categoria/06010000",
    "HERRAMIENTAS Y FERRETERIA": "https://www.digicorp.com.bo/producto/categoria/06020000",
    "COMPUTO": "https://www.digicorp.com.bo/producto/categoria/07010000"
}

def obtener_productos():
    print("Iniciando extracción masiva por categorías...")
    productos_totales = []
    
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(viewport={'width': 1280, 'height': 800})
            pagina = contexto.new_page()
            
            for nombre_cat, url in categorias_a_extraer.items():
                print(f"Explorando: {nombre_cat}...")
                try:
                    pagina.goto(url, wait_until="networkidle", timeout=60000)
                    pagina.wait_for_timeout(4000)
                    
                    # Scroll moderado para cargar productos iniciales
                    for i in range(5): 
                        pagina.keyboard.press("End")
                        pagina.wait_for_timeout(2000)
                        
                    html = pagina.content()
                    sopa = BeautifulSoup(html, 'html.parser')
                    
                    # Selectores basados en la estructura común de la tienda
                    tarjetas = sopa.find_all(['div', 'li'], class_=lambda c: c and any(p in c.lower() for p in ['product', 'item', 'grid', 'card']))
                    
                    count = 0
                    for tarjeta in tarjetas:
                        nombre_elem = tarjeta.find(['h2', 'h3', 'h4', 'a'], class_=lambda c: not c or 'btn' not in c.lower())
                        img_elem = tarjeta.find('img')
                        
                        if nombre_elem and img_elem:
                            nombre = nombre_elem.text.strip()
                            imagen = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original')
                            
                            if nombre and imagen and len(nombre) > 3:
                                if not imagen.startswith('http'):
                                    imagen = f"https://www.digicorp.com.bo{imagen}" if imagen.startswith('/') else f"https://www.digicorp.com.bo/{imagen}"
                                    
                                productos_totales.append({
                                    "nombre": nombre,
                                    "imagen": imagen,
                                    "categoria": nombre_cat
                                })
                                count += 1
                    print(f"Capturados {count} productos de {nombre_cat}")
                except Exception as e:
                    print(f"Error en {nombre_cat}: {e}")
                    
            navegador.close()
        
        # Eliminar duplicados exactos
        vistos = set()
        productos_finales = []
        for p in productos_totales:
            id_prod = f"{p['nombre']}-{p['categoria']}"
            if id_prod not in vistos:
                vistos.add(id_prod)
                productos_finales.append(p)
        
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(productos_finales, f, ensure_ascii=False, indent=4)
            
        print(f"Proceso finalizado. Total: {len(productos_finales)} productos.")
        
    except Exception as e:
        print(f"Fallo general del sistema: {e}")

if __name__ == "__main__":
    obtener_productos()
