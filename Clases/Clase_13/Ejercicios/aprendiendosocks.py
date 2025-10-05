import socket , os, sys

# Crear un socket TCP para comunicación a través de Internet
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Crear un socket UDP para comunicación a través de Internet
sock_udp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

# Crear un socket Unix para comunicación local
sock_unix = socket.socket(socket.AF_UNIX, socket.SOCK_RAW)


sock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Diferentes formas de especificar la misma dirección
address1 = ("www.google.com", 80)
address2 = ("8.8.8.8", 53)
address3 = ("localhost", 8080)
address4 = ("", 9000)  # Bind a todas las interfaces disponibles



# request= b'GET / HTTP/1.1\r\nHost: www.example.com\r\n\r\n'
# cliente_sck.send(request)

# response= cliente_sck.recv(1024)
# print(cliente_sck)
# print(response.decode(encoding="utf-8"))

# cliente_sck.close()


# Seteamos al socket a una dirección en particular, en donde escuchará todo lo que entre a su dirección
# Además apropiará esta dirección como destino al momento de realizar una comunicación 
def cliente_side():
    cliente_sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente_sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    cliente_sck.connect(('127.0.0.1',8080))
    i = 0
    while i < 10:
        cliente_sck.send(b'HOLA EL CLIENTE ENVIO UN DATO \n')
        print(cliente_sck.recv(1024).decode("utf-8"))
        i += 1

    print('EL CLIENTE CIERRA SU SOCKET')
    cliente_sck.close()

def server_side():

    #Creamos un pequeño server, usando sockets
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Asocia el socket a una dirección y un puerto específico
    server_socket.bind(('127.0.0.1', 8080))
    #Escuchamos el puerto bindeado (5 conexiones como máximo), el socket está listo para escuchar conexiones entrantes
    server_socket.listen(5)
    print('EL SERVER ESTÁ ESCUCHANDO EN EL PUERTO 8080')
    i = 0

    # El proceso (y socket) se bloquean hasta que un cliente se conecte
    client_scket, client_addrs = server_socket.accept()
    print(f'Conectado al cliente {client_addrs}')
    with client_scket:
        while i < 10:

            ###HACER OTRO ARCHIVITO DE CLIENTE QUE ENVÍE DATOS AL SERVIDOR
            data= client_scket.recv(1024)
            print(f'Recibí: {data.decode("utf-8")}')

            response = b"Hola desde el servidor"

            client_scket.send(data)
            print(i)
            i +=1
    print('EL SERVER CIERRA LA CONEXION')
    client_scket.close()
    server_socket.close()

hijo_client = os.fork()
if hijo_client == 0:
    cliente_side()
    os._exit(0)

else:
    server_side()
    os.waitpid(hijo_client,0)

