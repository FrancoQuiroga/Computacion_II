import socket,os, csv, time
HOST,PORT = "127.0.0.1", 9003
def csv_generator():
    with open('prueba.csv', 'w', newline='') as csvfile:
        trashwriterr = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        i = 0
        datos= []
        while i < 500:
            i+=1
            datos.append("a"*i)

        trashwriterr.writerows(datos)
def servidor():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.bind((HOST,PORT))
        server_socket.listen(1)
        clietn_sock, client_addr = server_socket.accept()
        
        with open('prueba.csv',newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            data_to_send = ""
            for row in spamreader:
                print("ROW",row)
                for item in row:
                    data_to_send += item
                #data_to_send.append(row)
            clietn_sock.sendall(data_to_send.encode())
        clietn_sock.shutdown(socket.SHUT_WR)
def recv_all(sock):
    #bytes
    chunks = []
    while True:
        
        b = sock.recv(64*1024)
        if not b: 
            break
        chunks.append(b)
    return b"".join(chunks)

def cliente():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.connect((HOST,PORT))
        data = recv_all(client_socket)
        print(f"Recibidos {len(data)} kilobytes de información")

if __name__ == "__main__":
    csv_generator() 
    
    client_procss = os.fork()
    
    if client_procss == 0:
        # Proceso hijo (servidor)
        try:
            print(f"Soy el server, mi PID es: {os.getpid()}")
            cliente()
        finally:
            # Es buena práctica asegurar que el hijo salga
            os._exit(0) 
            
    else:
        # Proceso padre (cliente)
        print(f"Soy el cliente, mi PID es: {os.getpid()}")
        
        # **SOLUCIÓN CRÍTICA PARA ConnectionRefusedError:**
        # Damos tiempo al servidor para que inicie (bind y listen).
        
        
        try:
            servidor()
        finally:
            # Esperamos que el proceso hijo (servidor) termine antes de que el padre termine
            # para evitar que el puerto quede en un estado indefinido.
            os.waitpid(client_procss, 0)
            print("Cliente y servidor terminados.")