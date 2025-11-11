"""Considera usar modo headless para eficiencia
    Configura timeouts para páginas que tardan mucho
    Maneja páginas que requieren JavaScript vs HTML estático
"""
from selenium import webdriver
#Drivers para esperar que la pag web cargue los componentes
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .__chrome_browser import setup_chrome_driver_for_performance as chrome_browser



def generate_screenshot(url):
    """Genera un screenshot de la URL y devuelve la imagen codificada en base64."""

    try:
        browser = chrome_browser(False)
        browser.set_page_load_timeout(30)
        browser.get(url)
        # Espera a que carguen todos los componentes de la página web
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        # Screenshot debugger line
        # screenshot= browser.save_screenshot("fotito.png")
        
        # Devolver base64_encoded_image
        scrn_shot_base64 = browser.get_screenshot_as_base64()
        return scrn_shot_base64
    

    except Exception as e:     
        print(f"Error al generar screenshot de {url}: {e}")
        return {"error": str(e), "status": "screenshot_failed"}
    finally:
        if browser:
            browser.quit()

    
if __name__ == '__main__':
    generate_screenshot('http://www.google.com/')