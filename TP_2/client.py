# client.py

import requests
import argparse
import json
import time
import base64
import os

def parse_args():
    """Parsea los argumentos para el cliente."""
    parser = argparse.ArgumentParser(description="Cliente de Prueba para el Sistema de Scraping")
    parser.add_argument("url", type=str, help="URL completa a scrapear (ej: https://google.com)")
    parser.add_argument("--host", default="127.0.0.1", help="Host del Servidor A (scraping)")
    parser.add_argument("--port", default=8000, type=int, help="Puerto del Servidor A")
    parser.add_argument("--save", action="store_true", help="Guardar screenshot y thumbnails en disco")
    return parser.parse_args()

def save_images(response_data):
    """Guarda las imágenes base64 en archivos locales para verificación."""
    print("\nGuardando imágenes...")
    
    # 1. Guardar Screenshot
    try:
        if "processing_data" in response_data and "screenshot" in response_data["processing_data"]:
            img_b64 = response_data["processing_data"]["screenshot"]
            img_data = base64.b64decode(img_b64)
            
            # Asegurarse que el directorio exista
            os.makedirs("output", exist_ok=True)
            filepath = "output/screenshot.png"
            
            with open(filepath, "wb") as f:
                f.write(img_data)
            print(f"✅ Screenshot guardado en: {filepath}")
            
    except Exception as e:
        print(f"⚠️ Error al guardar screenshot: {e}")

    # 2. Guardar Thumbnails (Opcional, pero útil)
    # ... (lógica similar para iterar 'thumbnails' y guardarlos) ...

def main():
    args = parse_args()
    
    # Construir la URL del endpoint del Servidor A
    scrape_endpoint = f"http://{args.host}:{args.port}/scrape"
    params = {"url": args.url}
    
    print(f"Solicitando scraping de: {args.url}")
    print(f"Contactando al Servidor A en: {scrape_endpoint}")
    
    start_time = time.time()
    
    try:
        # 1. Realizar la solicitud HTTP
        response = requests.get(scrape_endpoint, params=params, timeout=120) # Timeout largo para el cliente
        
        end_time = time.time()
        print(f"\nRespuesta recibida en {end_time - start_time:.2f} segundos.")
        
        # 2. Verificar estado
        response.raise_for_status() # Lanza excepción si es 4xx o 5xx
        
        # 3. Cargar el JSON
        data = response.json()
        
        # 4. Mostrar un resumen de los datos
        print("\n--- Resumen del Scraping ---")
        print(f"Título: {data.get('scraping_data', {}).get('title', 'N/A')}")
        print(f"Status: {data.get('status', 'N/A')}")
        
        if data.get('status') == 'success':
            print(f"Imágenes encontradas: {data['scraping_data']['images_count']}")
            print(f"Tiempo de carga (ms): {data['processing_data']['performance']['load_time_ms']}")
            print(f"Screenshot: {len(data['processing_data']['screenshot'])} bytes (base64)")
            print(f"Thumbnails generados: {len(data['processing_data']['thumbnails'])}")
        
            # 5. Guardar imágenes si se solicitó
            if args.save:
                save_images(data)
        
        else:
            print(f"Error del servidor: {data.get('message', 'Desconocido')}")

    except requests.exceptions.Timeout:
        print("Error: La solicitud al Servidor A ha superado el timeout.")
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al Servidor A. ¿Está corriendo?")
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

if __name__ == "__main__":
    main()