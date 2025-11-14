# client.py

import requests
import argparse
import json
import time
import base64
import os
from urllib.parse import urljoin

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
def poll_task_status(status_url):
    """
    Consulta el endpoint /status/{task_id} hasta que la tarea 
    esté 'completed' o 'failed'.
    """
    poll_interval = 2 # Segundos entre cada verificación
    max_wait_time = 120 # Máximo 2 minutos de espera
    start_time = time.time()
    
    while True:
        # 1. Comprobar si se superó el tiempo máximo
        if time.time() - start_time > max_wait_time:
            raise Exception("La tarea superó el tiempo máximo de espera (120s)")
        
        # 2. Consultar el estado
        try:
            response = requests.get(status_url)
            response.raise_for_status()
            data = response.json()
            
            status = data.get("status")
            print(f"  Estado actual de la tarea: {status}...")
            
            # 3. Revisar el estado
            if status == "completed":
                print("✅ Tarea completada.")
                return True # Éxito
            
            if status == "failed":
                raise Exception("El servidor reportó que la tarea falló.")
            
            # 4. Esperar y volver a intentar
            # (status es 'pending', 'scraping', o 'processing')
            time.sleep(poll_interval)
            
        except requests.RequestException as e:
            # Error al consultar el estado, reintentar
            print(f"  Error al consultar estado ({e}), reintentando...")
            time.sleep(poll_interval)
def main():
    args = parse_args()
    
    # Construir la URL base del servidor
    base_url = f"http://{args.host}:{args.port}"
    
    try:
        # --- PASO 1: Enviar la Tarea ---
        scrape_endpoint = urljoin(base_url, "/scrape")
        params = {"url": args.url}
        
        print(f"Solicitando scraping de: {args.url}")
        print(f"Contactando al Servidor A en: {scrape_endpoint}")
        
        start_time = time.time()
        response = requests.get(scrape_endpoint, params=params, timeout=10)
        response.raise_for_status() # Error si es 4xx o 5xx
        
        # Guardar los datos de la tarea
        task_data = response.json()
        task_id = task_data.get("task_id")
        
        # Construir las URLs de estado y resultado
        status_url = urljoin(base_url, task_data.get("status_url"))
        result_url = urljoin(base_url, task_data.get("result_url"))
        
        print(f"Tarea aceptada por el servidor. ID de tarea: {task_id}")

        # --- PASO 2: Esperar a que la Tarea Termine (Polling) ---
        print("\nComenzando consulta de estado (polling)...")
        poll_task_status(status_url) # Esto bloquea hasta que esté listo

        # --- PASO 3: Obtener el Resultado Final ---
        print(f"\nDescargando resultado desde: {result_url}")
        response = requests.get(result_url)
        response.raise_for_status()
        
        end_time = time.time()
        print(f"Respuesta final recibida en {end_time - start_time:.2f} segundos.")
        
        data = response.json()
        
        # --- PASO 4: Mostrar Resumen (Igual que antes) ---
        print("\n--- Resumen del Scraping ---")
        print(f"Título: {data.get('scraping_data', {}).get('title', 'N/A')}")
        print(f"Status: {data.get('status', 'N/A')}")
        
        if data.get('status') == 'success':
            print(f"Imágenes encontradas: {data['scraping_data']['images_count']}")
            print(f"Tiempo de carga (ms): {data['processing_data']['performance']['load_time_ms']}")
            print(f"Screenshot: {len(data['processing_data']['screenshot'])} bytes (base64)")
            
            if args.save:
                save_images(data)
        else:
            print(f"Error del servidor: {data.get('message', 'Desconocido')}")

    except requests.exceptions.Timeout:
        print("Error: La solicitud inicial al Servor A ha superado el timeout.")
    except requests.exceptions.ConnectionError:
        print("Error: No se pudo conectar al Servidor A. ¿Está corriendo?")
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")
if __name__ == "__main__":
    main()