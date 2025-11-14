# tests/test_processor.py

import unittest
import sys
import os

# --- Configuración del PYTHONPATH ---
# Esto es crucial para que 'tests/' pueda encontrar 'processor/'
# Agrega el directorio raíz (TP2) al path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
# ------------------------------------

# Importar las funciones que queremos probar
from processor.screenshot import generate_screenshot
from processor.performance import analyze_performance
from processor.image_processor import process_images

# --- URLs de Prueba ---
# Usaremos 'httpbin.org' y 'example.com' porque son estables
# y no dependen de JavaScript pesado (para tests rápidos)
TEST_URL_STATIC = "https://example.com"
TEST_URL_DYNAMIC = "https://httpbin.org/html" # Una página HTML simple
TEST_URL_IMAGES = "https://httpbin.org/image" # Una página con imágenes

class TestProcessorWorkers(unittest.TestCase):

    def setUp(self):
        """Se ejecuta antes de cada prueba."""
        print(f"\nEjecutando: {self._testMethodName}...")

    def tearDown(self):
        """Se ejecuta después de cada prueba."""
        print("Prueba finalizada.")

    # --- 1. Prueba de Screenshot ---
    def test_screenshot(self):
        """Prueba la función generate_screenshot."""
        
        # Ejecutar la función
        result = generate_screenshot(TEST_URL_STATIC)
        
        # Verificación 1: ¿Devolvió un string?
        self.assertIsInstance(result, str, "El screenshot no es un string (debería ser base64)")
        
        # Verificación 2: ¿Es un string base64 válido? (Simple)
        self.assertTrue(len(result) > 500, "El string base64 es demasiado corto")
        
        # Verificación de error (ej: URL inválida)
        result_fail = generate_screenshot("http://invalid-url-that-does-not-exist.xyz")
        self.assertIsInstance(result_fail, dict, "La falla no devolvió un diccionario de error")
        self.assertEqual(result_fail.get("status"), "screenshot_failed")

    # --- 2. Prueba de Performance ---
    def test_performance(self):
        """Prueba la función analyze_performance."""
        
        # Ejecutar la función
        result = analyze_performance(TEST_URL_DYNAMIC)
        
        # Verificación 1: ¿Devolvió un diccionario?
        self.assertIsInstance(result, dict, "El análisis de performance no devolvió un diccionario")
        
        # Verificación 2: ¿Tiene las llaves requeridas?
        self.assertIn("load_time_ms", result)
        self.assertIn("total_size_kb", result)
        self.assertIn("num_requests", result)
        
        # Verificación 3: ¿Los tipos de datos son correctos?
        self.assertIsInstance(result["load_time_ms"], int)
        self.assertIsInstance(result["num_requests"], int)
        
        # Verificación de error (ej: URL inválida)
        result_fail = analyze_performance("http://invalid-url-that-does-not-exist.xyz")
        self.assertIsInstance(result_fail, dict, "La falla no devolvió un diccionario de error")
        self.assertEqual(result_fail.get("status"), "performance_failed")


    # --- 3. Prueba de Procesamiento de Imágenes ---
    def test_image_processor(self):
        """Prueba la función process_images."""
        
        base_url = "https://httpbin.org/"
        image_urls = [
            "/image/png",  # Relativa
            "https://httpbin.org/image/jpeg" # Absoluta
        ]
        
        # Ejecutar la función
        result = process_images(base_url, image_urls)
        
        # Verificación 1: ¿Devolvió una lista?
        self.assertIsInstance(result, list, "El procesador de imágenes no devolvió una lista")
        
        # Verificación 2: ¿La lista contiene strings base64?
        self.assertEqual(len(result), 2, "No se procesaron 2 imágenes")
        self.assertIsInstance(result[0], str, "El thumbnail 1 no es un string base64")
        self.assertTrue(len(result[0]) > 100, "El thumbnail 1 es demasiado corto")

# --- Cómo ejecutar el archivo ---
if __name__ == "__main__":
    """
    Esto permite ejecutar el archivo directamente desde la terminal.
    """
    unittest.main()