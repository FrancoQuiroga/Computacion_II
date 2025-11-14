"""Servidor Multiprocessing:  
Este modulo debe implementar multiprocessing y socketserver  
Este servidor debe:  
    - Escuchar conexiones en un puerto diferente al servidor principal
    - Recibir solicitudes del Server A a través de sockets
    - Ejecutar las siguientes operaciones(En distintos procesos)
        . Captura de screenshot: Generar un PNG de cómo se ve la página web renderizada
        . Anáñisis de Rendimiento: Calcular el tiempo de carga, tamaño total de recursos, cantidad de request necesarios
        . Análisis de Imagen: Descargar las imágenes principales de la página y generar thumbnails ¿optimizados?
    
    - Manejar múltiples solicitudes concurrentemente usando un process pool
    - Devolver los resultados al Server A, a través de sockets

La comunicación entre servidores debe hacerse mediante sockets y usar serialización (JSON)
"""
# server_scraping.py

import asyncio
import argparse
import aiohttp
from aiohttp import web
import json
from datetime import datetime
import time
import uuid # Para generar task_ids
# Importar los módulos de scraping y comunicación
# (Asumimos que están en scraper/ y common/)
import scraper.async_http as async_scraper
import scraper.html_parser as parser
import common.protocol as protocol
import common.serialization as serializer
from common.protocol import send_msg_async, read_msg_async
from common.serialization import serializer
async def run_scrape_task(app, task_id, url):
    """
    Esta es la tarea que se ejecuta en segundo plano.
    Contiene la lógica original de scraping y procesamiento.
    """
    task_storage = app['task_storage']
    
    try:
        # 1. Actualizar estado a "scraping"
        task_storage[task_id]["status"] = "scraping"
        
        http_session = app['http_session']
        server_b_config = app['server_b_config']

        # --- Tarea A: Scraping y Parsing ---
        html_content = await asyncio.wait_for(
            async_scraper.fetch_html(http_session, url),
            timeout=30.0
        )
        
        loop = asyncio.get_event_loop()
        scraping_data = await loop.run_in_executor(
            None, 
            parser.parse_html_data, 
            html_content,
            url
        )
        image_urls = scraping_data.get("image_urls", [])

        # 2. Actualizar estado a "processing"
        task_storage[task_id]["status"] = "processing"

        # --- Tarea B: Comunicación con Servidor B ---
        processing_data = await request_processing_from_server_b(
            server_b_config,
            url,
            image_urls
        )
        
        # 3. Consolidar y guardar el resultado final
        final_result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "scraping_data": scraping_data,
            "processing_data": processing_data,
            "status": "success" # Status del *resultado*, no de la tarea
        }
        
        # 4. Actualizar estado a "completed"
        task_storage[task_id]["status"] = "completed"
        task_storage[task_id]["result"] = final_result

    except Exception as e:
        # 5. Manejar fallos
        task_storage[task_id]["status"] = "failed"
        task_storage[task_id]["result"] = {"status": "error", "message": str(e)}

async def handle_scrape(request):
    """
    Manejador principal de la ruta /scrape.
    Recibe la URL, coordina el scraping local y el procesamiento remoto (Servidor B).
    """
    
    url = request.query.get('url')
    if not url:
        return web.json_response(
            {"status": "error", "message": "URL query parameter is required"}, 
            status=400
        )

    # Obtenemos la sesión HTTP compartida (creada en main)
    http_session = request.app['http_session']
    
    # Obtenemos la configuración del Servidor B (Host/Port)
    server_b_config = request.app['server_b_config']

    try:
        # --- Tarea A: Scraping (I/O Asíncrono) ---
        # 1. Descargar el HTML de forma asíncrona
        #    con timeout de 30s.
        start_time = time.time()
        
        html_content = await asyncio.wait_for(
            async_scraper.fetch_html(http_session, url),
            timeout=30.0
        )
        
        # --- Tarea A: Parsing (CPU-Bound) ---
        # 2. Parsear el HTML. Esto es CPU-bound, así que lo ejecutamos 
        #    en un executor (ThreadPool) para no bloquear el event loop.
        loop = asyncio.get_event_loop()
        
        # (parse_html_data es una función SÍNCRONA de html_parser.py)
        scraping_data = await loop.run_in_executor(
            None, # Usa el ThreadPoolExecutor por defecto
            parser.parse_html_data, 
            html_content,
            url
        )

        # 3. Extraer las URLs de imágenes (necesarias para el Servidor B)
        #    (Asumimos que parse_html_data también extrae 'image_urls')
        image_urls = scraping_data.get("image_urls", [])

        # --- Tarea B: Comunicación (I/O Asíncrono) ---
        # 4. Comunicarse con el Servidor B usando Sockets Asíncronos
        #    Esta función manejará asyncio.open_connection
        
        processing_data = await request_processing_from_server_b(
            server_b_config,
            url,
            image_urls
        )
        
        # 5. Consolidar y devolver el JSON final
        final_response = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "scraping_data": scraping_data,
            "processing_data": processing_data,
            "status": "success"
        }
        return web.json_response(final_response)

    # --- Manejo de Errores ---
    except asyncio.TimeoutError:
        return web.json_response(
            {"status": "error", "message": "Scraping timeout (30s)"}, 
            status=504 # Gateway Timeout
        )
    except aiohttp.ClientError as e:
        return web.json_response(
            {"status": "error", "message": f"HTTP request failed: {e}"}, 
            status=400
        )
    except ConnectionRefusedError:
        return web.json_response(
            {"status": "error", "message": "Server B (Processing) is unavailable"}, 
            status=503 # Service Unavailable
        )
    except Exception as e:
        # Error genérico (ej: parsing fallido, error de socket)
        return web.json_response(
            {"status": "error", "message": str(e)}, 
            status=500
        )

async def handle_submit_scrape(request):
    """
    (NUEVO) Acepta la tarea y devuelve un task_id.
    Reemplaza a 'handle_scrape'. Debería ser un POST, pero
    lo dejamos en GET por simplicidad del client.py.
    """
    url = request.query.get('url')
    if not url:
        return web.json_response({"error": "URL parameter is required"}, status=400)

    # 1. Generar ID y crear tarea
    task_id = str(uuid.uuid4())
    app = request.app
    app['task_storage'][task_id] = {"status": "pending", "result": None}

    # 2. Lanzar la tarea en segundo plano
    asyncio.create_task(run_scrape_task(app, task_id, url))

    # 3. Devolver el task_id inmediatamente
    response_data = {
        "message": "Task accepted",
        "task_id": task_id,
        "status_url": f"/status/{task_id}",
        "result_url": f"/result/{task_id}"
    }
    return web.json_response(response_data, status=202) # 202 Accepted

async def handle_get_status(request):
    """(NUEVO) Devuelve el estado de una tarea."""
    task_id = request.match_info.get('task_id')
    task_storage = request.app['task_storage']
    
    task = task_storage.get(task_id)
    if not task:
        return web.json_response({"error": "Task not found"}, status=404)
        
    return web.json_response({"task_id": task_id, "status": task["status"]})
# --- 2. Cliente Asíncrono para el Servidor B ---

async def request_processing_from_server_b(server_b_config, url, image_urls):
    """
    Se conecta al Servidor B (multiprocessing) usando sockets asíncronos.
    """
    host = server_b_config['host']
    port = server_b_config['port']
    
    # 1. Abrir conexión de socket asíncrona
    reader, writer = await asyncio.open_connection(host, port)

    # 2. Preparar los datos de la solicitud
    request_data = {
        "url": url,
        "image_urls": image_urls
    }
    
    # 3. Serializar y enviar (usando el módulo de protocolo)
    #    protocol.send_data(writer, request_data)
    msg_bytes = serializer.serialize(request_data)
    await send_msg_async(writer, msg_bytes)
    await writer.drain() # Esperar a que el buffer se vacíe

    # 4. Leer la respuesta
    #    response_data = await protocol.read_data(reader)
    response_bytes = await read_msg_async(reader)
    response_data = serializer.deserialize(response_bytes)
    
    # 5. Cerrar la conexión
    writer.close()
    await writer.wait_closed()
    
    return response_data

async def handle_get_result(request):
    """(NUEVO) Devuelve el resultado de una tarea completada."""
    task_id = request.match_info.get('task_id')
    task_storage = request.app['task_storage']
    
    task = task_storage.get(task_id)
    if not task:
        return web.json_response({"error": "Task not found"}, status=404)
        
    if task["status"] == "completed":
        return web.json_response(task["result"])
    elif task["status"] == "failed":
        return web.json_response(task["result"], status=500)
    else:
        # Aún no está lista
        return web.json_response(
            {"status": task["status"], "message": "Task is not yet complete"}, 
            status=202 # 202 Accepted (pero no listo)
        )
# --- 3. Módulos de Scraping (Archivos Separados) ---

# scraper/async_http.py
async def fetch_html(session, url):
    """(En archivo separado) Usa aiohttp para descargar el HTML."""
    async with session.get(url) as response:
        response.raise_for_status() # Lanza excepción si es 4xx/5xx
        return await response.text()

# scraper/html_parser.py
def parse_html_data(html_content):
    """
    (En archivo separado) Función SÍNCRONA que usa BeautifulSoup 
    para extraer todo lo requerido en 'scraping_data'.
    """
    # soup = BeautifulSoup(html_content, 'lxml')
    # ... lógica de parsing ...
    # return { "title": ..., "links": ..., "meta_tags": ..., ... }
    pass # (Implementación de parsing aquí)


# --- 4. Inicialización y CLI ---

def parse_args():
    """Configura y parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description="Servidor de Scraping Web Asíncrono")
    parser.add_argument("-i", "--ip", required=True, help="Dirección de escucha (soporta IPv4/IPv6)")
    parser.add_argument("-p", "--port", required=True, type=int, help="Puerto de escucha")
    # (El argumento 'workers' es manejado por el runner de aiohttp si se usa Gunicorn, 
    # pero aiohttp.web.run_app es single-process por defecto)
    
    # Argumentos para conectar al Servidor B
    parser.add_argument("--b-host", default="127.0.0.1", help="Host del Servidor B")
    parser.add_argument("--b-port", default=8001, type=int, help="Puerto del Servidor B")

    return parser.parse_args()

async def init_app(server_b_config):
    """Inicializa la aplicación aiohttp."""
    app = web.Application()
    
    # 1. Almacén de Tareas
    app['task_storage'] = {}
    
    # 2. Sesión HTTP
    app['http_session'] = aiohttp.ClientSession()
    
    # 3. Configuración del Servidor B
    app['server_b_config'] = server_b_config

    # 4. Definir NUEVAS rutas
    app.router.add_get('/scrape', handle_submit_scrape) # Antes 'handle_scrape'
    app.router.add_get('/status/{task_id}', handle_get_status)
    app.router.add_get('/result/{task_id}', handle_get_result)
    
    # ... (Manejo de cierre limpio) ...
    
    return app
def main():
    args = parse_args()
    
    server_b_config = {"host": args.b_host, "port": args.b_port}

    # Iniciar la aplicación aiohttp
    # aiohttp maneja automáticamente IPv4/IPv6 según el 'host'
    # (ej: '0.0.0.0' para IPv4, '::' para IPv6/Dual-stack)
    web.run_app(init_app(server_b_config), host=args.ip, port=args.port)

if __name__ == "__main__":
    main()