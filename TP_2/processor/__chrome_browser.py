from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


def setup_chrome_driver_for_performance(perf_test:bool):
    """Configura el driver de Chrome para capturar logs de performance (red)."""
    
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if perf_test == True:
        # Esta es la clave: Habilitar el logging de 'performance'
        # Necesitamos pedirle a Chrome que registre los eventos de Red (Network)
        logging_prefs = {'performance': 'ALL'}
        chrome_options.set_capability('goog:loggingPrefs', logging_prefs)
        
        # Opcional: A veces se necesita 'browser' también
    # logging_prefs['browser'] = 'ALL' 
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver