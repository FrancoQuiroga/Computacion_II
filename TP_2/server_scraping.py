"""Servidor Multiprocessing:  
Este modulo debe implementar multiprocessing y socketserver  
Este servidor debe:  
    - Escuchar conexiones en un puerto diferente al servidor principal
    - Recibir solicitudes del Server A a través de sockets
    - Ejecutar las siguientes operaciones(En distintos procesos)
        . Captura de screenshot: Generar un PNG de cómo se ve la página web renderizada
        . Anáñisis de Rendimiento: Calcular el tiempo de carga, tamaño total de recursos, cantidad de request necesarios
        . Análisis de Imagen: Descargar las imágenes principales de la página y generar thumbnails ¿optimizados?
    
    - Manejar múltiples solicitudes concurrentemente usando un process pool
    - Devolver los resultados al Server A, a través de sockets

La comunicación entre servidores debe hacerse mediante sockets y usar serialización (JSON)
"""