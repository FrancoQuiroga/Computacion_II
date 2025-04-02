import os,time

def crear_hijo():
    return os.fork()


#if hijo_recursivo == 0:
#    print(f'Soy el primer hijo {os.getpid()}, y mi padre es: {os.getppid()}')
def crear_hijos_recursivos(hijos_por_crear):
    for i in range(hijos_por_crear):
        indiceactual= i
        hijoactual = crear_hijo()
        if hijoactual == 0:
            print(f'Soy el hijo nro {i+1},mi pid:{os.getpid()},mi padre:{os.getppid()}')
            continue
        else:
            break

def crear_5hijos():
    print(f'Soy el padre de todos {os.getpid()}')
    crear_hijos_recursivos(5)
    
    #hijo_recursivo = crear_hijo()


if __name__ == '__main__':
    crear_5hijos()