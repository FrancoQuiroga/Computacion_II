#!/bin/bash

# Script para ejecutar el proyecto completo TP2
# Uso: ./run_project.sh "https://url-a-probar.com"

# --- Función de Limpieza ---
# Se ejecuta al salir del script (EXIT) o al presionar Ctrl+C (INT)
cleanup() {
    echo -e "\n[SCRIPT] Cerrando servidores..."
    # Matar los procesos del servidor por sus PIDs
    if [ -n "$SERVER_A_PID" ]; then
        kill $SERVER_A_PID 2>/dev/null
        echo "Servidor A (PID $SERVER_A_PID) detenido."
    fi
    if [ -n "$SERVER_B_PID" ]; then
        kill $SERVER_B_PID 2>/dev/null
        echo "Servidor B (PID $SERVER_B_PID) detenido."
    fi
    echo "[SCRIPT] Todos los procesos han sido detenidos."
}

# Registrar la función 'cleanup' para que se ejecute al salir o interrumpir
trap cleanup EXIT INT

# --- 1. Activar Entorno Virtual ---
# Asume que el entorno está en una carpeta 'env'
if [ -d "env" ]; then
    echo "[SCRIPT] Activando entorno virtual..."
    source env/bin/activate
else
    echo "[SCRIPT] Advertencia: No se encontró el directorio 'env'. Asumiendo que las dependencias están instaladas globalmente."
fi

# --- 2. Validar URL de entrada ---
if [ -z "$1" ]; then
    echo "Error: Debes pasar una URL como primer argumento."
    echo "Uso: ./run_project.sh \"https://google.com\""
    exit 1
fi

URL_CLIENTE=$1

# --- 3. Iniciar Servidor B (Procesamiento) ---
echo "[SCRIPT] Iniciando Servidor B (Procesamiento) en 127.0.0.1:8001..."
python3 server_processing.py -i 127.0.0.1 -p 8001 &
# Guardar el Process ID (PID) del último comando ejecutado en segundo plano
SERVER_B_PID=$!

# --- 4. Iniciar Servidor A (Scraping) ---
echo "[SCRIPT] Iniciando Servidor A (Scraping) en 127.0.0.1:8000..."
python3 server_scraping.py -i 127.0.0.1 -p 8000 --b-host 127.0.0.1 --b-port 8001 &
SERVER_A_PID=$!

# --- 5. Esperar a que los servidores se levanten ---
echo "[SCRIPT] Esperando 3 segundos a que los servidores se inicien..."
sleep 3

# --- 6. Ejecutar el Cliente ---
echo "[SCRIPT] Ejecutando el cliente para la URL: $URL_CLIENTE"
# Ejecuta el cliente en primer plano. El script esperará aquí.
python3 client.py "$URL_CLIENTE" --port 8000 --save

echo "[SCRIPT] El cliente ha finalizado."
# El trap 'cleanup' se ejecutará automáticamente al llegar a este punto.