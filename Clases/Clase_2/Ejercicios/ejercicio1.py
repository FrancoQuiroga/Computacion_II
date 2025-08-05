import os

proccessid = os.fork() #El padre esto es el PID del hijo, el hijo esto es 0

if proccessid == 0:
    print(f'Hola soy el proceso hijo, mi id es: {os.getpid()} y la de mi padre es: {os.getppid()}')

else:
    print(f'Hola, soy el proceso padre, mi id es: {os.getpid()}')

