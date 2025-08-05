from multiprocessing import Process,Pipe
import os
import time

def tarea(nombre):
    print(f'{nombre} iniciado')
    print(os.getppid())
    time.sleep(2)
    if nombre==3:
        exit()
    print(f'{nombre} terminado')

if __name__ == '__main__':
    procesos = []
    for i in range(5):
        p = Process(target=tarea, args=(f'Proceso-{i}',),daemon=True)
        
        procesos.append(p)

        p.start()
    
    for p in procesos:
        p.join()

    print('Todos los procesos han terminado')