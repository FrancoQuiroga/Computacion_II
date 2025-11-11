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

# Importar los módulos de scraping y comunicación
# (Asumimos que están en scraper/ y common/)
import scraper.async_http as async_scraper
import scraper.html_parser as parser
import common.protocol as protocol

# --- 1. El Coordinador (Manejador de Rutas HTTP) ---

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
            html_content 
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
    message = json.dumps(request_data).encode('utf-8') # Serialización simple
    writer.write(message)
    await writer.drain() # Esperar a que el buffer se vacíe
    
    writer.write_eof() # Indicar fin de envío (opcional, depende del protocolo)

    # 4. Leer la respuesta
    #    response_data = await protocol.read_data(reader)
    response_bytes = await reader.read(8192) # Leer hasta 8KB
    response_data = json.loads(response_bytes.decode('utf-8'))
    
    # 5. Cerrar la conexión
    writer.close()
    await writer.wait_closed()
    
    return response_data


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
    
    # 1. Crear una única sesión de cliente HTTP para reutilizar conexiones
    app['http_session'] = aiohttp.ClientSession()
    
    # 2. Almacenar configuración del Servidor B
    app['server_b_config'] = server_b_config

    # 3. Definir rutas
    app.router.add_get('/scrape', handle_scrape)
    
    # Manejo de cierre limpio
    async def on_cleanup(app):
        await app['http_session'].close()
    app.on_cleanup.append(on_cleanup)
    
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