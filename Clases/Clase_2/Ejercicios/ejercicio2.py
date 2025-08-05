import os
#process2 =1 #Placeholder para que el padre no tenga problemas al comprobar proccess2
process1= os.fork()

if process1 > 0:
    process2 = os.fork()
#print(process1)

#print(process2)
if process1==0:
    print(f'Hola soy el hijo 1, me llamo {os.getpid()},mi padre es {os.getppid()}')
    os._exit(0)
if process2==0:
    print(f'Hola soy el hijo 2, me llamo {os.getpid()},mi padre es {os.getppid()}')
    os._exit(0)

else:
    print(f'Hola, soy el padre: {os.getpid()}')
    os.wait()

