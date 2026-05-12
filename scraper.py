from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os

# Lista de categorías actualizada incluyendo NOVEDADES y DIMAX
categorias_a_extraer = {
    "NOVEDADES": "https://www.digicorp.com.bo/novedades",
    "Cámaras - Control Remoto - Energía - Cables - Soportes - Conectores": "https://digicorp.com.bo/marcas/DIMAX",
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
    print("Iniciando extracción incluyendo NOVEDADES, DIMAX y Gestor Inteligente...")
    productos_totales = []
    
    palabras_basura = [
        'digicorp ©', 'Iniciar sesión', 'en dios confiamos', 'lunes a viernes:', 'preguntas frecuentes',
        'contáctanos', 'horarios', 'google play', 'app store', 'descarga', 
        'boletín', 'suscríbete', 'inicio', 'nosotros', 'políticas', 
        'términos', 'bs.', 'oferta', 'nuevo', 'registrarse', 'carrito',
        'soluciones tecnológicas', 'derechos reservados', 'página oficial'
    ]
    
    img_basura = ['iso.png', 'x.svg', 'contactanos.png', 'logo.', '/logo', 'icon', 'banner', 'footer', 'playstore', 'appstore', 'whatsapp']
    
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(viewport={'width': 1280, 'height': 800})
            pagina = contexto.new_page()
            
            for nombre_cat, url in categorias_a_extraer.items():
                print(f"Explorando pasillo: {nombre_cat}...")
                try:
                    pagina.goto(url, wait_until="networkidle", timeout=60000)
                    pagina.wait_for_timeout(7000)
                    
                    # Scroll para cargar todos los productos de la categoría
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
                        if imagen.startswith('data:image'): continue
                            
                        imagen_url_low = imagen.lower()
                        if any(x in imagen_url_low for x in img_basura):
                            continue
                        
                        padre = img.parent
                        nombre = ""
                        
                        # Buscamos textos alrededor de la imagen para capturar Marca, Modelo y Descripción
                        for _ in range(4):
                            if padre:
                                textos = list(padre.stripped_strings)
                                # Filtramos textos muy cortos o que sean basura publicitaria
                                textos_validos = [t for t in textos if len(t) > 2 and not any(b in t.lower() for b in palabras_basura)]
                                
                                if textos_validos:
                                    # Combinamos los textos encontrados para un título profesional
                                    nombre = " - ".join(textos_validos)
                                    break
                                padre = padre.parent
                                
                        if nombre and imagen:
                            nombre = nombre.strip().replace('\n', ' ').replace('  ', ' ')
                            
                            if len(nombre) > 10 and not any(b in nombre.lower() for b in palabras_basura):
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
                                
                    print(f"  -> Capturados {count} productos detallados de {nombre_cat}")
                except Exception as e:
                    print(f"  -> Error en {nombre_cat}: {e}")
                    
            navegador.close()
            
        # --- SISTEMA DE FUSIÓN Y LISTA NEGRA (El nuevo cerebro) ---
        print("Revisando tu Gestor de Productos (Manuales, Detalles y Lista Negra)...")
        manuales_dict = {}
        if os.path.exists('manuales.json'):
            try:
                with open('manuales.json', 'r', encoding='utf-8') as fm:
                    datos_m = json.load(fm)
                    # Convertimos la lista a un diccionario para encontrar los productos súper rápido
                    manuales_dict = {m['nombre']: m for m in datos_m if 'nombre' in m}
            except Exception as e:
                print(f"  -> Advertencia: No se pudo leer manuales.json: {e}")

        productos_finales = []
        nombres_finales = set()

        # 1. Filtramos y enriquecemos lo que el robot acaba de extraer de la web
        for p in productos_totales:
            nombre = p['nombre']
            
            # REGLA 1 (Lista Negra): Si tú le diste a "Ocultar" en el gestor, el robot lo ignora.
            if nombre in manuales_dict and manuales_dict[nombre].get('visible') == False:
                continue
            
            # REGLA 2 (Enriquecimiento): Si le pusiste video o detalles técnicos, se los sumamos.
            if nombre in manuales_dict:
                p.update(manuales_dict[nombre])
            
            if nombre not in nombres_finales:
                productos_finales.append(p)
                nombres_finales.add(nombre)

        # 2. Agregamos los productos que son 100% manuales (los que tú subiste desde cero)
        for nombre, datos in manuales_dict.items():
            # Si no está en la web y NO está oculto, lo agregamos al catálogo final
            if nombre not in nombres_finales and datos.get('visible') != False:
                productos_finales.append(datos)
                nombres_finales.add(nombre)
        # -------------------------------------------------------------
                
        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(productos_finales, f, ensure_ascii=False, indent=4)
            
        print(f"\nProceso finalizado. Catálogo actualizado, filtrado y fusionado con éxito.")
        
    except Exception as e:
        print(f"Fallo general del sistema: {e}")

if __name__ == "__main__":
    obtener_productos()
