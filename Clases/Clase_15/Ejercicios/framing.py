import socket, os

def send_lines(sock, lines):
    for line in lines:
        if not line.endswith("\n"):
            line += "\n"
        sock.sendall(line.encode("utf-8"))

def recv_until_closed(sock):
    # Acumula hasta que el peer cierre; en un protocolo real pararíamos por un token/longitud
    chunks = []
    while True:
        b = sock.recv(1024)
        if not b:  # 0 bytes → peer cerró
            break
        chunks.append(b)
    
    print(f"Deje de esperar algo, este es el chunk {chunks} \n")
    return b"".join(chunks)
    
def data_sender():
    #Client
    HOST, PORT = "127.0.0.1", 9002
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        send_lines(s, ["uno", "dos", "tres"])  # desde la terminal del `nc` podés escribir respuestas
        s.shutdown(socket.SHUT_WR)  # anuncias que ya no enviarás más
        print(f"Ahora recibo datos, soy el data_sender, mi PID es:{os.getpid()}")
        data = recv_until_closed(s)
        print("Imprimiendo todos los bloques")
        print(data.decode("utf-8", errors="replace"))

def data_reciever():
    #Server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_reciver:
        socket_reciver.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        socket_reciver.bind(("127.0.0.1", 9002))
        socket_reciver.listen(1)
        conn, addr = socket_reciver.accept()
        recv_info = conn.recv(1024)
        print(f"Recibí el siguiente texto \n{recv_info.decode("utf-8")}")
        i= 0 
        while i< 5:
            conn.send(f"Hola soy {os.getpid()},enviando un bloque de texto \n".encode())
            i+=1
        socket_reciver.shutdown(socket.SHUT_WR)


        #GENERA UN TEXTO PARA QUE EL recv_until_closed HAGA ALGO

if __name__ == "__main__":
    data_sender_process = os.fork()
    if data_sender_process == 0:
        print(f"Soy el data sender, mi PID es: {os.getpid()}")
        data_sender()
    else:
        print(f"Soy el data reciver, mi PID es: {os.getpid()}")
        data_reciever()