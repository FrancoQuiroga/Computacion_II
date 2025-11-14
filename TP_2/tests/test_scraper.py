# tests/test_scraper.py

import unittest
import sys
import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup

# --- Configuración del PYTHONPATH ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# ------------------------------------

# Importar las funciones que queremos probar
from scraper.async_http import fetch_html
from scraper.metadata_extractor import extract_metadata
from scraper.html_parser import parse_html_data

# --- Constantes de Prueba ---
TEST_URL_STATIC = "https://example.com"
TEST_URL_NON_HTML = "https://httpbin.org/image/png"
TEST_URL_INVALID = "http://invalid-url-that-does-not-exist.xyz"

class TestScraperModules(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada prueba."""
        print(f"\nEjecutando: {self._testMethodName}...")

    def tearDown(self):
        """Se ejecuta después de cada prueba."""
        print("Prueba finalizada.")

    # --- 1. Prueba del Descargador Asíncrono ---
    def test_async_http_fetch(self):
        """Prueba la función asíncrona fetch_html."""
        
        async def run_test():
            # Creamos una sesión de aiohttp solo para esta prueba
            async with aiohttp.ClientSession() as session:
                
                # Prueba 1: URL válida
                html = await fetch_html(session, TEST_URL_STATIC)
                self.assertIsInstance(html, str)
                self.assertIn("Example Domain", html) # Verificar contenido
                
                # Prueba 2: URL no HTML (debe fallar por Content-Type)
                with self.assertRaises(Exception, msg="No falló con URL no-HTML"):
                    await fetch_html(session, TEST_URL_NON_HTML)
                
                # Prueba 3: URL inválida (debe fallar por DNS)
                with self.assertRaises(Exception, msg="No falló con URL inválida"):
                    await fetch_html(session, TEST_URL_INVALID)

        # Ejecutamos la función de prueba asíncrona
        asyncio.run(run_test())

    # --- 2. Prueba del Extractor de Metadatos ---
    def test_metadata_extractor(self):
        """Prueba la función síncrona extract_metadata."""
        
        html = """
        <html><head>
            <title>  Título de Prueba  </title>
            <meta name="description" content="Descripción de prueba.">
            <meta name="keywords" content="key1, key2">
            <meta property="og:title" content="Título OG">
        </head></html>
        """
        soup = BeautifulSoup(html, 'lxml')
        
        data = extract_metadata(soup)
        
        self.assertIsInstance(data, dict)
        # Verificar que el título se limpió (strip)
        self.assertEqual(data["title"], "Título de Prueba")
        self.assertEqual(data["meta_tags"]["description"], "Descripción de prueba.")
        self.assertEqual(data["meta_tags"]["keywords"], "key1, key2")
        self.assertEqual(data["meta_tags"]["og:title"], "Título OG")

    # --- 3. Prueba del Parser Principal ---
    def test_html_parser(self):
        """Prueba la función síncrona parse_html_data."""
        
        base_url = "https://midominio.com"
        html = """
        <html><head>
            <title>Título Completo</title>
            <meta name="description" content="Desc Completa">
        </head><body>
            <h1>Un H1</h1>
            <h1>Dos H1</h1>
            <h2>Un H2</h2>
            <a href="/pagina_relativa">Relativo</a>
            <a href="https://google.com">Absoluto</a>
            <img src="logo.png">
            <img src="/imgs/banner.jpg">
            <img src="https://externo.com/img.png">
        </body></html>
        """
        
        data = parse_html_data(html, base_url)
        
        # Verificar datos de metadata (delegados)
        self.assertEqual(data["title"], "Título Completo")
        self.assertEqual(data["meta_tags"]["description"], "Desc Completa")
        
        # Verificar estructura
        self.assertEqual(data["structure"]["h1"], 2)
        self.assertEqual(data["structure"]["h2"], 1)
        self.assertEqual(data["structure"]["h3"], 0)
        
        # Verificar imágenes
        self.assertEqual(data["images_count"], 3)
        self.assertIn("logo.png", data["image_urls"])
        self.assertIn("/imgs/banner.jpg", data["image_urls"])
        
        # Verificar links (y resolución de URLs)
# tests/test_scraper.py
        self.assertIn("https://midominio.com/pagina_relativa", data["links"])
        self.assertIn("https://google.com", data["links"])
        self.assertEqual(len(data["links"]), 2)


# --- Cómo ejecutar el archivo ---
if __name__ == "__main__":
    unittest.main()