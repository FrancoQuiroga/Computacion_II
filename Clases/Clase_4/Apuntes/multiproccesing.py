from multiprocessing import Process, Pipe

def proceso_hijo(conection):
    conection.send("Hola desde el hijo") #escribe en el extremo w del pipe
    respuesta = conection.recv() #recibe la conexión del pipe
    print(f"Hijo recibió: {respuesta}")
    conection.close()

if __name__ == "__main__":
    parent_conection, child_conection = Pipe()
    current_process = Process(target=proceso_hijo, args=(child_conection,))
    current_process.start()
    
    print(f"Padre recibió: {parent_conection.recv()}")
    parent_conection.send("Hola de vuelta desde el padre")
    
    current_process.join()