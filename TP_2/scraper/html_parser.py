# scraper/html_parser.py

from bs4 import BeautifulSoup
from urllib.parse import urljoin
# Importar el nuevo módulo
from scraper.metadata_extractor import extract_metadata

def parse_html_data(html_content, base_url):
    """
    (Actualizado) Función SÍNCRONA que parsea el contenido HTML.
    Delega la extracción de metadatos a metadata_extractor.
    """
    
    # Usar 'lxml' es recomendado por ser más rápido
    soup = BeautifulSoup(html_content, 'lxml')

    # 1. Extraer Metadatos (usando el módulo separado)
    #    Aquí delegamos el trabajo.
    metadata = extract_metadata(soup) # Obtiene { "title": "...", "meta_tags": {...} }

    # 2. Todos los enlaces (links)
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Convertir enlaces relativos (ej: "/about") en absolutos
        abs_link = urljoin(base_url, href)
        links.append(abs_link)

    # 3. Cantidad de imágenes en la página
    img_tags = soup.find_all('img')
    images_count = len(img_tags)

    # 4. Estructura básica (cantidad de headers H1-H6)
    structure = {}
    for i in range(1, 7):
        header_tag = f'h{i}'
        count = len(soup.find_all(header_tag))
        structure[header_tag] = count

    # 5. (NECESARIO PARA SERVIDOR B) Extraer URLs de imágenes
    image_urls = []
    for img in img_tags:
        src = img.get('src')
        if src:
            # 'image_processor.py' ya maneja la lógica de urljoin
            image_urls.append(src)

    # Compilar el diccionario final de 'scraping_data'
    return {
        "title": metadata["title"],         # <--- Viene de metadata_extractor
        "links": list(set(links)),          # <--- Viene de html_parser
        "meta_tags": metadata["meta_tags"], # <--- Viene de metadata_extractor
        "structure": structure,             # <--- Viene de html_parser
        "images_count": images_count,       # <--- Viene de html_parser
        "image_urls": image_urls            # <--- Viene de html_parser
    }