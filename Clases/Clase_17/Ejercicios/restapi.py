import http.server as serv_mod
import os,json
from urllib.parse import urlparse, parse_qs

ADDRS = "localhost"
PORT = 9001

USUARIOS = {
    1: "Ana Gómez",
    2: "Luis Pérez",
    3: "Sofía Martínez",
    4: "Javier Rodríguez",
    5: "Elena Fernández",
    6: "Carlos López",
    7: "María Sánchez",
    8: "David García",
    9: "Laura Díaz",
    10: "Jorge Ruiz"
}
"""
-----> /users --------> /users/id
          |
          |
          |
          L ----> /users 

"""
class ApiHandler(serv_mod.BaseHTTPRequestHandler):
    def do_GET(self):
        # URL entera
        full_path,resource_path,user_id = self.path_verification()    
        if user_id != None:
                # 1. Obtener el nombre del usuario
                nombre_usuario = USUARIOS[user_id]
                # 2. Crear un DICCIONARIO para la respuesta (formato estándar de API)
                respuesta_data = {
                    "id": user_id,
                    "nombre": nombre_usuario
                }
                print(f"Usuario encontrado: {nombre_usuario}")
                # 3. Llamar a la función de respuesta con el objeto Python
                # Se ELIMINA el json.loads()
                self._send_json_response(
                    respuesta_data, 
                    f"El usuario con id {user_id} es: {nombre_usuario}\n"
                )
        
        if full_path == "/users":
            self._send_json_response(list(USUARIOS.values()), "Lista de todos los usuarios")
        elif resource_path[-1] == "users":
            self._send_json_response(list(USUARIOS.values()), "Lista de todos los usuarios")
        

    #TERMINAR DE COMPLETAR ESTOS MÉTODOS, NO OLVIDAR USAR EL PATH VERIFICATION CUANDO SEA NECESARIO
    def do_POST(self):
        full_path,resource_path,user_id = self.path_verification()
    def do_PUT(self):
        full_path,resource_path,user_id = self.path_verification()
    def do_DELETE(self):
        full_path,resource_path,user_id = self.path_verification()

    def path_verification(self):
        """ full_path -> str  
            resource_path -> path del recurso que se quiere acceder
            user_id_int -> int
        """
        url_object= urlparse(self.path)
        full_path = url_object.path
        #Path sin el id de usuario
        resource_path = full_path.split("/")
        user_id = full_path.split("/")[-1]
        #Verificar si la url contiene id de user
        try:
            user_id_int = int(full_path.split("/")[-1])
            return full_path, resource_path, user_id_int
        except ValueError:
            return full_path, resource_path, None
        except:
            return full_path, resource_path, None
    


    def _send_json_response(self, data:json, msj:str) -> None:
        self.send_response(200, msj)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_error_response(self,code,message):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode())

if __name__ == '__main__':
    with serv_mod.ThreadingHTTPServer((ADDRS,PORT),ApiHandler) as http_server:
        try:
            print("Iniciando Server")
            http_server.serve_forever()
        except KeyboardInterrupt:
            print("Finalizando Server")
            exit()
