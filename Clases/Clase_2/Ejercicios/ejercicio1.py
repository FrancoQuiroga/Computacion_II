import os

proccessid = os.fork()

if proccessid == 0:
    print(f'Hola soy el proceso hijo, mi id es: {os.getpid()} y la de mi padre es: {os.getppid()}')

else:
    print(f'Hola, soy el proceso padre, mi id es: {os.getpid()}')

