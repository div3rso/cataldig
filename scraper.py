from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta

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
    print("Iniciando Robot Maestro...")
    productos_totales = []
    palabras_basura = ['digicorp ©', 'Iniciar sesión', 'en dios confiamos', 'lunes a viernes:', 'preguntas frecuentes', 'contáctanos', 'horarios', 'google play', 'app store', 'descarga', 'boletín', 'suscríbete', 'inicio', 'nosotros', 'políticas', 'términos', 'bs.', 'oferta', 'nuevo', 'registrarse', 'carrito', 'derechos reservados']
    img_basura = ['iso.png', 'x.svg', 'contactanos.png', 'logo.', '/logo', 'icon', 'banner', 'footer', 'whatsapp']
    
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            contexto = navegador.new_context(viewport={'width': 1280, 'height': 800})
            pagina = contexto.new_page()
            for nombre_cat, url in categorias_a_extraer.items():
                print(f"-> Escaneando: {nombre_cat}...")
                try:
                    pagina.goto(url, wait_until="networkidle", timeout=60000)
                    pagina.wait_for_timeout(7000)
                    for i in range(6): 
                        pagina.evaluate("window.scrollBy(0, 1000)")
                        pagina.wait_for_timeout(2000)
                    html = pagina.content()
                    sopa = BeautifulSoup(html, 'html.parser')
                    nombres_vistos = set()
                    for img in sopa.find_all('img'):
                        imagen = img.get('src') or img.get('data-src') or img.get('data-original')
                        if not imagen or imagen.startswith('data:image') or any(x in imagen.lower() for x in img_basura): continue
                        padre = img.parent
                        nombre = ""
                        for _ in range(4):
                            if padre:
                                textos = list(padre.stripped_strings)
                                validos = [t for t in textos if len(t) > 2 and not any(b in t.lower() for b in palabras_basura)]
                                if validos:
                                    nombre = " - ".join(validos)
                                    break
                                padre = padre.parent
                        if nombre and len(nombre) > 10 and nombre not in nombres_vistos:
                            if not imagen.startswith('http'):
                                imagen = f"https://www.digicorp.com.bo{imagen}" if imagen.startswith('/') else f"https://www.digicorp.com.bo/{imagen}"
                            productos_totales.append({"nombre": nombre, "imagen": imagen, "categoria": nombre_cat})
                            nombres_vistos.add(nombre)
                except: pass
            navegador.close()

        # FUSIÓN CON MANUALES
        manuales_dict = {}
        if os.path.exists('manuales.json'):
            with open('manuales.json', 'r', encoding='utf-8') as fm:
                try:
                    m_data = json.load(fm)
                    manuales_dict = {m['nombre']: m for m in m_data if 'nombre' in m}
                except: pass

        productos_finales = []
        final_vistos = set()
        for p in productos_totales:
            nombre = p['nombre']
            if nombre in manuales_dict and manuales_dict[nombre].get('visible') == False: continue
            if nombre in manuales_dict: p.update(manuales_dict[nombre])
            if nombre not in final_vistos:
                productos_finales.append(p)
                final_vistos.add(nombre)

        for n, m in manuales_dict.items():
            if n not in final_vistos and m.get('visible') != False:
                productos_finales.append(m)
                final_vistos.add(n)

        # GENERACIÓN DE FECHA VERSIÓN (Bolivia UTC-4)
        fecha_bolivia = datetime.utcnow() - timedelta(hours=4)
        version_str = fecha_bolivia.strftime("%m%d%Y.%H.%M")

        # GUARDADO CON NUEVA ESTRUCTURA
        data_final = {
            "version": version_str,
            "productos": productos_finales
        }

        with open('productos.json', 'w', encoding='utf-8') as f:
            json.dump(data_final, f, ensure_ascii=False, indent=4)
        print(f"¡Catálogo Actualizado! Versión: {version_str}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    obtener_productos()
