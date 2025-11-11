from selenium import webdriver
from .__chrome_browser import setup_chrome_driver_for_performance as chrome_browser
import json
import time # Para medir el tiempo total, si requests.elapsed no es suficiente


def process_cdp_logs(logs):
    """Analiza los logs de CDP para extraer métricas de red."""
    
    num_requests = 0
    total_size_bytes = 0
    
    # Usamos un set para no contar el mismo request ID múltiples veces
    request_ids = set() 

    for entry in logs:
        try:
            # Convertir el mensaje de log (string) a JSON
            message_data = json.loads(entry['message'])
            message = message_data['message']
            
            # A. Contar Requests
            # 'Network.responseReceived' se dispara por cada recurso (CSS, JS, IMG, XHR)
            if message['method'] == 'Network.responseReceived':
                num_requests += 1
                
            # B. Sumar Tamaño Total
            # 'Network.loadingFinished' nos da el tamaño codificado (transferido)
            if message['method'] == 'Network.loadingFinished':
                request_id = message['params']['requestId']
                
                # Evitar doble conteo (aunque 'loadingFinished' es único por request)
                if request_id not in request_ids:
                    size = message['params'].get('encodedDataLength', 0)
                    total_size_bytes += size
                    request_ids.add(request_id)

        except Exception:
            # Ignorar logs que no son JSON o no tienen la estructura esperada
            pass

    return {
        "total_size_kb": round(total_size_bytes / 1024, 2),
        "num_requests": num_requests
        # El load_time_ms se agregará en la función principal
    }

def analyze_performance(url):
    """
    Calcula el tiempo de carga, tamaño total de recursos y num_requests
    usando Selenium y los logs de Performance (CDP).
    
    Esta función es síncrona y está diseñada para el pool de multiprocessing.
    """
    
    browser = None
    try:
        browser = chrome_browser(True)
        # Configurar timeout de página (requisito del TP)
        browser.set_page_load_timeout(30) 
        
        # 1. Medir el tiempo de carga (Load Time)
        # Usamos time para medir cuánto tarda 'browser.get()' como una 
        # aproximación del "tiempo de carga" total.
        start_time = time.time()
        browser.get(url) # Carga la página y genera los logs
        end_time = time.time()
        
        load_time_ms = int((end_time - start_time) * 1000)
        
        
        
        # 2. Obtener los logs de performance
        logs = browser.get_log('performance')
        
        # 3. Procesar los logs para obtener métricas
        # (Esta es la parte compleja, ver Lógica de Procesamiento)
        
        performance_metrics = process_cdp_logs(logs)
        
        # 4. Consolidar resultados
        performance_metrics["load_time_ms"] = load_time_ms
        
        return performance_metrics

    except Exception as e:
        return {"error": f"Error en análisis de performance: {e}", "status": "performance_failed"}
        
    finally:
        if browser:
            browser.quit()
if __name__ == "__main__":
    print(analyze_performance('http://www.google.com/'))