"""escribe un programa que cree dos procesos hijo
 mediante multiprocessing.
 Process, cada uno imprimiendo su propio pid. 
 El proceso padre debe esperar a que ambos terminen 
 sy luego imprimir un mensaje de cierre."""
from multiprocessing import Process, current_process
def process_funct(id):
    #print(type(processlist[id]))
    print(f'Mi id de proceso es: {processlist[id].pid}')
processlist = []
if __name__ == '__main__':

    for id in range(2):
        p = Process(target=process_funct,args=(id,))
        processlist.append(p)

    for proc in processlist:
        print('EMPEZANDO LA EJECUCIÓN')
        print(proc.pid)
        proc.start()
    for proc in processlist:
        print(proc.pid)
        print('Uniendo Procesos')
        proc.join()
print(processlist)
print('TERMINANDO EJECUCIÓN',f'Mi id de proceso es: {current_process().pid}')

