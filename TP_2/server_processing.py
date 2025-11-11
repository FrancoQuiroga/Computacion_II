""" Este módulo debería:  
    - Recibir URLs de sitios web a analizar (mediante HTTP)
    - Realizar scraping de la página web de forma asíncrona
    - Extraer la sig información de cada URL:
        . Título de la página <Title>
        . Todos los enlaces encontrados <link href="link">
        . MetaTags relevantes (description keywords, open graph tags)
        . Cantidad de imagenes en la página
        . Estructura básica (H1 - H6)
    - Comunicarse con el server de procesamiento (parte B) para extra análisis
    - Devolver al cliente una respuesta JSON, con toda la info extraída y procesada

El server  debe implementar mecanismos de comunicación asíncrona  
entre tareas para coordinar el scraping y el procesamiento sin bloquear operaciones

""" 
# server_processing.py
import socketserver
import json
import multiprocessing
import sys
import argparse
import os
from processor.image_processor import process_images
from processor.performance import analyze_performance
from processor.screenshot import generate_screenshot
from common.protocol import read_msg_sync, send_msg_sync
from common.serialization import serializer
import signal
# Importar funciones de worker (screenshot, performance, images)
# Importar módulos de serialización/protocolo
def init_worker():
    """Ignora la señal de KeyboardInterrupt (Ctrl+C) en el worker."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


class ProcessingWorkerPool:
    """Clase para gestionar el pool de procesos y someter tareas."""
    def __init__(self, num_processes):
        # Crear un Pool de procesos
        self.pool = multiprocessing.Pool(processes=num_processes,initializer=init_worker)

    def submit_processing_tasks(self, task_data):
        """
        Somete las tareas de procesamiento al pool.
        
        task_data será un diccionario con la URL y quizás una lista de URLs de imágenes
        extraídas por el Servidor A.
        """
        url = task_data.get("url")
        image_urls = task_data.get("image_urls", [])

        # Sometemos las tareas al pool. Usamos apply_async o map_async para 
        # obtener Futures/AsyncResult.
        # Aquí usamos apply_async para simular:
        
        # 1. Captura de Screenshot
        screenshot_result = self.pool.apply_async(generate_screenshot, args=(url, {}))
        
        # 2. Análisis de Rendimiento
        performance_result = self.pool.apply_async(analyze_performance, args=(url,))
        
        # 3. Análisis de Imágenes
        thumbnails_result = self.pool.apply_async(process_images, args=(url, image_urls))
        
        try:
            # Esperamos los resultados (esto es blocking para este proceso/hilo del socketserver,
            # pero el trabajo pesado se hizo en un proceso worker)
            screenshot = screenshot_result.get(timeout=60) # Con timeout
            performance = performance_result.get(timeout=60)
            thumbnails = thumbnails_result.get(timeout=60)
            
            return {
                "screenshot": screenshot,
                "performance": performance,
                "thumbnails": thumbnails
            }
        except Exception as e:
            # Manejo de errores (timeouts, excepciones en el worker, etc.)
            return {"error": str(e), "status": "processing_failed"}


class ProcessingRequestHandler(socketserver.BaseRequestHandler):
    """Maneja una solicitud entrante del Servidor A."""
    
    # Se inicializa con el pool de procesos
    worker_pool = None 
    
    def handle(self):
        """Método que se ejecuta al recibir una conexión."""
        
        # 1. Recepción de datos del socket
        data_bytes = read_msg_sync(self.request) # self.request es el socket
        if not data_bytes:
            return # Cliente desconectado
        try:
            # 2. Deserialización
            task_data = serializer.deserialize(data_bytes)
            # 3. Delegar al pool de workers
            if self.worker_pool:
                results = self.worker_pool.submit_processing_tasks(task_data)
            else:
                results = {"error": "Worker pool no inicializado", "status": "internal_error"}
                
        except Exception as e:
            # Manejo de errores de protocolo/serialización
            results = {"error": f"Error al procesar la solicitud: {e}", "status": "protocol_error"}
            
        response_bytes = serializer.serialize(results)
        send_msg_sync(self.request, response_bytes)



# server_processing.py


def parse_args():
    """Configura y parsea los argumentos de línea de comandos con argparse."""
    parser = argparse.ArgumentParser(description="Servidor de Procesamiento Distribuido")
    parser.add_argument("-i", "--ip", required=True, help="Dirección de escucha")
    parser.add_argument("-p", "--port", required=True, type=int, help="Puerto de escucha")
    parser.add_argument("-n", "--processes", type=int, 
                        default=os.cpu_count(), 
                        help="Número de procesos en el pool (default: CPU count)")
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Inicializar el Pool de Procesos
    print(f"Iniciando pool con {args.processes} procesos...")
    pool_manager = ProcessingWorkerPool(args.processes)
    
    # Asignar el pool a la clase de Request Handler
    ProcessingRequestHandler.worker_pool = pool_manager
    
    # Configurar el servidor de sockets. Usamos ThreadingTCPServer o ForkingTCPServer 
    # para manejar múltiples conexiones del Servidor A, pero delegamos el 
    # trabajo pesado (CPU-bound) al pool de procesos. 
    # ThreadingTCPServer es común en Windows, ForkingTCPServer en Unix/Linux.
    # Dado que el requisito es usar multiprocessing y socketserver, 
    # ForkingTCPServer es una opción más "natural" para el paralelismo en la recepción.

    # Usaremos ThreadingTCPServer ya que delegamos el paralelismo real a Pool
    # para el trabajo CPU-bound, y los hilos son suficientes para recibir datos del socket.
    server = socketserver.ThreadingTCPServer((args.ip, args.port), ProcessingRequestHandler)
    
    print(f"Servidor de Procesamiento escuchando en {args.ip}:{args.port}")
    
    try:
        # Activar el servidor
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido por el usuario.")
    finally:
        server.shutdown()
        pool_manager.pool.close()
        pool_manager.pool.join()
        print("Servidor y Pool de Procesos cerrados.")

if __name__ == "__main__":
    main()