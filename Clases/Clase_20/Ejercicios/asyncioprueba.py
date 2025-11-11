import time
import requests  # Para versión síncrona
import asyncio
import aiofiles
import aiohttp   # Para versión asíncrona

# Versión SÍNCRONA
def descargar_sincrono():
    urls = [
        "http://example.com",
        "http://example.org", 
        "http://example.net"
    ]
    
    inicio = time.time()
    
    for url in urls:
        response = requests.get(url)
        print(f"Descargado {url}: {len(response.text)} bytes")
    
    print(f"Tiempo total: {time.time() - inicio:.2f}s")

# Versión ASÍNCRONA
async def descargar_una(session, url):
    async with session.get(url) as response:
        contenido = await response.text()
        print(f"Descargado {url}: {len(contenido)} bytes")

async def descargar_asincrono():
    urls = [
        "http://example.com",
        "http://example.org",
        "http://example.net"
    ]
    
    inicio = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Crear todas las tareas
        tareas = [descargar_una(session, url) for url in urls]
        # Ejecutarlas concurrentemente
        await asyncio.gather(*tareas)
    
    print(f"Tiempo total: {time.time() - inicio:.2f}s")

# Ejecutar
print("=== SÍNCRONO ===")
descargar_sincrono()

print("\n=== ASÍNCRONO ===")
asyncio.run(descargar_asincrono())