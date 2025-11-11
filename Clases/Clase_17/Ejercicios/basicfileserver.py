import http.server as serv_mod
import os,json
from urllib.parse import urlparse, parse_qs
ADDRS = "localhost"
PORT = 9001
DIRECTORY = "/carpeta_prueba"
MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.txt': 'text/plain',
    # Puedes añadir más tipos si es necesario
}

def get_mime_type(file_path):
    """Obtiene el tipo MIME basado en la extensión del archivo."""
    # os.path.splitext separa el nombre base del archivo y la extensión
    _, extension = os.path.splitext(file_path)
    # Usa .lower() para manejar extensiones en mayúsculas
    return MIME_TYPES.get(extension.lower(), 'application/octet-stream')

class FileHandler(serv_mod.BaseHTTPRequestHandler):
    def do_GET(self):
        
        parsed_path = urlparse(self.path)
        # DEBUGGING
        print(parsed_path)
        print(parsed_path.path.split("/")[-1])

        if parsed_path.path == "/":
            self.send_error(404, "Directorio no encontrado")

        if parsed_path.path == DIRECTORY:
            archivos = os.listdir(DIRECTORY.strip('/'))
            respuesta_json = json.dumps({
                    "directorio": DIRECTORY.strip('/'),
                    "archivos": archivos,
                    "total_elementos": len(archivos)
                })
            self._send_json(respuesta_json, "Listado de Archivos")

        if parsed_path.path == f"{DIRECTORY}/{parsed_path.path.split("/")[-1]}":
                    # Obtenemos el nombre del archivo solicitado (ej: index.html)
            nombre_archivo_solicitado = parsed_path.path.split("/")[-1]
            self._send_file(nombre_archivo_solicitado)

        else:
            self.send_error(404, "Directorio no encontrado")

    def _send_json(self, data:json, msj:str):
        self.send_response(200, msj)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_file(self,file_name):
        mime_type = get_mime_type(file_name)
        full_path = f".{DIRECTORY}/{file_name}"
        with open(full_path,"rb") as file:
            contenido = file.read()
        self.send_response(200)
        self.send_header("Content-type", mime_type)
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        print(contenido)
        self.wfile.write(contenido)
        
    
if __name__ == '__main__':
    with serv_mod.ThreadingHTTPServer((ADDRS,PORT),FileHandler) as http_server:
        try:
            print("Iniciando Server")
            http_server.serve_forever()
        except KeyboardInterrupt:
            print("Finalizando Server")
            exit()
