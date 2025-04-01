import os

pid = os.fork()
if pid == 0:
    os.execlp("ls", "ls", "-l")  # Solo se ejecuta en el hijo
else:
    os.wait()  # El padre espera que el hijo termine