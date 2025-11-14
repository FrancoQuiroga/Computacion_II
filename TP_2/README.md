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
    git clone [https://github.com/FrancoQuiroga/Computacion_II.git]
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
### Terminal 2: Iniciar Servidor A (Scraping)
```bash
(env) [TP_2]-(main)$ python3 server_scraping.py -i 127.0.0.1 -p 8000 --b-host 127.0.0.1 --b-port 8001
# Salida esperada: Servidor sirviendo en [http://127.0.0.1:8000](http://127.0.0.1:8000)
```

### Terminal 3: Ejecutar el Cliente
```bash
(env) [TP_2]-(main)$ python3 client.py "[https://google.com](https://google.com)" --port 8000 --save
# Salida esperada: --- Resumen del Scraping --- ...
```

### Modo 2: Script Automatizado (Recomendado para Probar)

El script `run_project.sh` automatiza los 3 pasos anteriores.

*   Dar permisos de ejecución (solo la primera vez):
    ```bash
    (env) [TP_2]-(main)$ chmod +x run_project.sh
    ```

*   Ejecutar el script: Pasa la URL que deseas probar como argumento (entre comillas).
    ```bash
    (env) [TP_2]-(main)$ ./run_project.sh "[https://es.wikipedia.org/wiki/Python](https://es.wikipedia.org/wiki/Python)"
    ```

    El script iniciará ambos servidores, ejecutará el cliente (con la opción `--save`) y cerrará los servidores automáticamente.

## Estructura del Proyecto

```
TP2/
├── server_scraping.py          # Servidor asyncio (Parte A)
├── server_processing.py        # Servidor multiprocessing (Parte B)
├── client.py                   # Cliente de prueba
├── run_project.sh              # Script de ejecución
├── scraper/
│   ├── async_http.py           # Cliente HTTP asíncrono
│   ├── html_parser.py          # Parser principal (BeautifulSoup)
│   └── metadata_extractor.py   # Extractor de metadatos
├── processor/
│   ├── screenshot.py           # Worker: Selenium Screenshot
│   ├── performance.py          # Worker: Selenium CDP Performance
│   └── image_processor.py      # Worker: Pillow Thumbnails
├── common/
│   ├── protocol.py             # Protocolo de sockets (prefijo de longitud)
│   └── serialization.py        # Serializador JSON
├── tests/
│   ├── test_scraper.py         # Pruebas unitarias (Servidor A)
│   └── test_processor.py       # Pruebas unitarias (Servidor B)
├── requirements.txt            # Dependencias
└── README.md                   # Este archivo
```