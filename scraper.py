from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

# Lista completa de las 15 categorías proporcionadas por el usuario
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
    print("Iniciando extracción con filtros avanzados para el proveedor...")
    productos_totales = []
    
    # Lista ampliada de palabras basura (textos que no son productos)
    # Basado en la imagen enviada: 'contáctanos', 'descarga nuestra app', 'google play', etc.
    palabras_basura = [
        'contáctanos', 'horarios', 'google play', 'app store', 'descarga', 
        'boletín', 'suscríbete', 'inicio', 'nosotros', 'políticas', 
        'términos', 'bs.', 'oferta', 'nuevo', 'registrarse', 'carrito',
        'soluciones tecnológicas' # Texto que acompaña al logo
    ]
    
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(viewport={'width': 1280, 'height': 800})
            pagina = contexto.new_page()
            
            for nombre_cat, url in categorias_a_extraer.items():
                print(f"Explorando pasillo: {nombre_cat}...")
                try:
                    pagina.goto(url, wait_until="networkidle", timeout=60000)
                    pagina.wait_for_timeout(6000)
                    
                    for i in range(6): 
                        pagina.evaluate("window.scrollBy(0, 900)")
                        pagina.wait_for_timeout(2500)
                        
                    html = pagina.content()
                    sopa = BeautifulSoup(html, 'html.parser')
                    
                    count = 0
                    nombres_vistos = set()
                    
                    for img in sopa.find_all('img'):
                        imagen = img.get('src') or img.get('data-src') or img.get('data-original')
                        if not imagen: continue
                        
                        # FILTRO PROTECTOR: Ignorar Base64 pesado
                        if imagen.startswith('data:image'): continue
                            
                        imagen_url_low = imagen.lower()
                        alt_text_low = img.get('alt', '').lower()

                        # --- NUEVOS FILTROS ESPECÍFICOS PARA EL PROVEEDOR ---
                        # Basado en la imagen proporcionada (Logo DIGICORP y Banner de App)
                        # Ignoramos si la URL de la imagen o el texto alternativo contienen palabras clave de branding
                        marcas_proveedor = ['logo', 'icon', 'banner', 'footer', 'promo', 'digicorp', 'google-play', 'app-store']
                        if any(x in imagen_url_low for x in marcas_proveedor):
                            continue
                        
                        # Filtro extra por el texto 'alt' de la imagen si lo tiene
                        if any(x in alt_text_low for x in ['digicorp', 'app', 'descarga', 'google play', 'soluciones']):
                            continue
                        
                        padre = img.parent
                        nombre = ""
                        
                        for _ in range(4):
                            if padre:
                                textos = list(padre.stripped_strings)
                                # Usamos la lista ampliada de palabras_basura
                                textos_validos = [t for t in textos if len(t) > 12 and not any(b in t.lower() for b in palabras_basura)]
                                
                                if textos_validos:
                                    nombre = max(textos_validos, key=len)
                                    break
                                padre = padre.parent
                                
                        if nombre and imagen:
                            nombre = nombre.strip().replace('\n', ' ').replace('  ', ' ')
                            # Validación adicional del nombre extraído
                            if len(nombre) > 15 and nombre.lower() not in ['contáctanos', 'soluciones tecnológicas']:
                                if nombre not in nombres_vistos:
                                    if not imagen.startswith('http'):
                                        imagen = f"https://www.digicorp.com.bo{imagen}" if imagen.startswith('/') else f"https://www.digicorp.com.bo/{imagen}"
                                        
                                    productos_totales.append({
                                        "nombre": nombre,
                                        "imagen": imagen,
                                        "categoria": nombre_cat
                                    })
                                    nombres_vistos.add(nombre)
                                    count += 1
                                
                    print(f"  -> Capturados {count} productos reales limpios de {nombre_cat}")
                except Exception as e:
                    print(f"  -> Error en {nombre_cat}: {e}")
                    
            navegador.close()
            
        # Filtro final de duplicados globales
        vistos = set()
        productos_finales = []
        for p in productos_totales:
            if p['nombre'] not in vistos:
                vistos.add(p['nombre'])
                productos_finales.append(p)
                
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(productos_finales, f, ensure_ascii=False, indent=4)
            
        print(f"\nProceso finalizado. Total guardado: {len(productos_finales)} productos legítimos y limpios.")
        
    except Exception as e:
        print(f"Fallo general: {e}")

if __name__ == "__main__":
    obtener_productos()
