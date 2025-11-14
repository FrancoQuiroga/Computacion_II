# TP2 - Sistema de Scraping y Análisis Web Distribuido

Este proyecto implementa un sistema distribuido de scraping web en Python, como parte del Trabajo Práctico 2. El sistema utiliza un servidor asíncrono (`asyncio`) como fachada y un servidor de procesamiento paralelo (`multiprocessing`) para tareas pesadas.

## Características

* **Servidor A (Fachada):** `server_scraping.py`
    * Maneja peticiones HTTP del cliente usando `aiohttp`.
    * Realiza el scraping de HTML de forma asíncrona (con `aiohttp` y `BeautifulSoup`).
    * Coordina con el Servidor B para tareas pesadas.
* **Servidor B (Worker):** `server_processing.py`
    * Maneja tareas CPU-bound usando `multiprocessing` y `socketserver`.
    * Genera screenshots de páginas web (usando `Selenium`).
    * Analiza la performance de la página (usando `Selenium CDP`).
    * Procesa y genera thumbnails de imágenes (usando `Pillow`).
* **Transparencia:** El cliente interactúa únicamente con el Servidor A, desconociendo la arquitectura interna.

---

## Instalación

Sigue estos pasos para configurar el entorno de desarrollo.

### 1. Prerrequisitos

* Python 3.10 o superior.
* `pip` y `venv`.
* Un WebDriver para Selenium (ej: **ChromeDriver** para Google Chrome). Asegúrate de que esté en el PATH de tu sistema.

### 2. Configuración del Entorno

1.  **Clonar el repositorio (si es necesario):**
    ```bash
    git clone [URL_DEL_REPOSITORIO]
    cd TP_2
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3.  **Instalar dependencias:**
    Crea un archivo `requirements.txt` con el siguiente contenido:
    ```txt
    aiohttp
    beautifulsoup4
    lxml
    Pillow
    selenium
    requests
    ```
    Luego, instálalas:
    ```bash
    pip install -r requirements.txt
    ```

---

## Ejecución

Puedes ejecutar el proyecto de forma manual (para depuración) o usando el script automatizado.

### Modo 1: Ejecución Manual (Recomendado para Depurar)

Necesitarás **3 terminales** separadas (todas con el entorno `env` activado).

**Terminal 1: Iniciar Servidor B (Procesamiento)**
```bash
(env) [TP_2]-(main)$ python3 server_processing.py -i 127.0.0.1 -p 8001
# Salida esperada: Servidor de Procesamiento escuchando en 127.0.0.1:8001