# processor/image_processor.py

import requests
from PIL import Image
import io
import base64
from urllib.parse import urljoin # Para resolver URLs relativas

# Constante para el tamaño del thumbnail
THUMBNAIL_SIZE = (100, 100) # (Ancho, Alto) en píxeles

# Límite de imágenes a procesar para no sobrecargar
MAX_IMAGES_TO_PROCESS = 5 

def process_images(base_url, image_urls):
    """
    Descarga imágenes principales, genera thumbnails optimizados y 
    los devuelve codificados en base64.
    
    Esta función es síncrona (para el pool de multiprocessing).
    
    Args:
        base_url (str): La URL de la página (para resolver rutas relativas).
        image_urls (list): Lista de URLs (str) de las imágenes 
                           extraídas por el Servidor A.
    """
    
    thumbnails_base64 = []
    processed_count = 0
    # 1. Iterar sobre las URLs de imágenes recibidas
    for img_url in image_urls:
        if processed_count >= MAX_IMAGES_TO_PROCESS:
            break # Limitar la cantidad de procesamiento

        try:
            # 2. Resolver URL (manejar rutas relativas como "/img/logo.png")
            full_img_url = urljoin(base_url, img_url)

            # 3. Descargar la imagen (síncrono)
            # Usamos un timeout corto para imágenes
            response = requests.get(full_img_url, timeout=10) 
            response.raise_for_status() # Error si es 4xx o 5xx

            # 4. Procesamiento con Pillow
            img_data = io.BytesIO(response.content)
            
            with Image.open(img_data) as img:
                
                # Opcional: Filtrar "imágenes principales" (ej: por tamaño)
                # Si la imagen es muy pequeña (ej: un ícono), la saltamos.
                if img.width < 50 or img.height < 50:
                    continue 

                # 5. Generar Thumbnail
                img.thumbnail(THUMBNAIL_SIZE)
                
                # 6. Guardar en buffer y codificar Base64
                output_buffer = io.BytesIO()
                # Guardar como PNG (o JPEG para mejor compresión)
                img.save(output_buffer, format="PNG") 
                
                img_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
                thumbnails_base64.append(img_base64)
                
                processed_count += 1

        except requests.RequestException:
            # Ignorar si falla la descarga de una imagen (timeout, 404)
            pass
        except Exception as e:
            # Ignorar si falla el procesamiento de una imagen (ej: formato corrupto)
            print(f"Error procesando imagen {img_url}: {e}")
            pass
            
    # 7. Devolver la lista de thumbnails codificados
    # Cumple con el formato JSON: "thumbnails": ["base64_thumb1", ...]
    return thumbnails_base64

if __name__ == "__main__":
    
    # URL base de la página analizada
    base_url = "https://httpbin.org/"

    # Lista de URLs de imágenes (como las habría extraído el Servidor A)
    image_urls = [
        # 1. Imagen absoluta (PNG) - Debería funcionar
        "https://httpbin.org/image/png",

        # 2. Imagen relativa (JPEG) - Debería funcionar (urljoin lo resolverá)
        "/image/jpeg",

        # 3. Imagen pequeña (Favicon) - Debería descargarse pero ser filtrada por tamaño (<50px)
        "https://www.google.com/favicon.ico",

        # 4. Imagen rota (404) - Debería fallar (RequestException) y ser ignorada
        "https://httpbin.org/status/404",

        # 5. Imagen inexistente - Debería fallar (RequestException) y ser ignorada
        "https://httpbin.org/image/nonexistent.jpg",

        # 6. Imagen absoluta grande (Google Logo) - Debería funcionar
        "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",

        # 7. Otra imagen (para probar el límite MAX_IMAGES_TO_PROCESS)
        "https://httpbin.org/image/webp"
    ]
    resultados = process_images(base_url, image_urls)
    print(resultados)