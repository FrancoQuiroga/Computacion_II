from multiprocessing import Process, Queue
import random
def productor(q):
    for i in range(5):
        random_num = random.randint(0,100)
        q.put(random_num)
        print(f"Productor añadió: {i}")
def consumidor_cube(q,cube):
    while True:
        itemtocube= q.get()
        if itemtocube is None:
            break
        cubeditem = itemtocube**3
        cube.put(cubeditem)

def consumidor_square(q,square):
    while True:
        itemtosquare = q.get()
        if itemtosquare is None:  # Señal de terminación
            break
        squareditem = itemtosquare**2
        square.put(squareditem)

if __name__ == "__main__":
    q = Queue()  # Creación de la Queue
    cubes = Queue()
    squares = Queue()

    p = Process(target=productor, args=(q,))
    cons_cube = Process(target=consumidor_cube, args=(q,cubes,))
    cons_sqre = Process(target=consumidor_square, args=(q,squares,)) 
    p.start()
    cons_cube.start()
    cons_sqre.start()
    
    q.put(None)  # Envía señal de terminación
    cubes.put(None)
    squares.put(None)
    p.join()

    cons_cube.join()
    cons_sqre.join()
