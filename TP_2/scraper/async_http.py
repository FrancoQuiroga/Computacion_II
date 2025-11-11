# scraper/async_http.py

import aiohttp

async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    """
    (En archivo separado) Usa aiohttp para descargar el HTML.
    
    Esta función es asíncrona y no bloquea el event loop.
    """
    try:
        async with session.get(url, allow_redirects=True) as response:
            # Lanza una excepción para códigos de error 4xx/5xx
            response.raise_for_status() 
            
            # Asegurarse de que sea HTML (opcional pero bueno)
            if "text/html" not in response.headers.get("Content-Type", ""):
                raise Exception(f"La URL no es HTML (Content-Type: {response.headers.get('Content-Type')})")
                
            return await response.text()
            
    except aiohttp.ClientError as e:
        # Re-lanzar el error para que el handler principal lo capture
        raise Exception(f"Error de red al fetchear {url}: {e}")