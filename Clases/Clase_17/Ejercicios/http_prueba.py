import http.server as mod_server
import http.client as mod_client
import time, json
from urllib.parse import urlparse, parse_qs
Mihandler = mod_server.SimpleHTTPRequestHandler

ADDRS = ("localhost",8000)
# server = mod_server.HTTPServer(("localhost",8000),Mihandler)
# server_thrd = mod_server.ThreadingHTTPServer(("localhost",7000),Mihandler)
# server.serve_forever()

class HandlerPersonal(mod_server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Parseamos la URL para extraer la ruta y parámetros
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self._send_html_response('<h1>Página Principal</h1>')
        elif parsed_path.path == '/api/status':
            self._send_json_response({'status': 'active', 'version': '1.0'})
        else:
            self._send_error_response(404, 'Página no encontrada')
    
    def do_POST(self):
        # Leemos el cuerpo de la solicitud
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # Intentamos parsear como JSON
            data = json.loads(post_data.decode('utf-8'))
            response = {'received': data, 'timestamp': time.time()}
            self._send_json_response(response)
        except json.JSONDecodeError:
            self._send_error_response(400, 'JSON inválido')
    
    def _send_html_response(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error_response(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode())

with mod_server.ThreadingHTTPServer(ADDRS,HandlerPersonal) as server:
    print(f"Servidor ejecutándose en {ADDRS}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCerrando servidor")
        exit()


