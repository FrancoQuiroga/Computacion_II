import socket,os 

def cliente():
    
    with  socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.connect(('127.0.0.1', 9001))
        texto = b"Hola Mundo \n"
        client_socket.send(texto)

if __name__ == "__main__":
    clienteserver = cliente()