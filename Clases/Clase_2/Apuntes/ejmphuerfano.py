import os, time

pid = os.fork()
if pid == 0:
    print(f"Hijo {os.getpid()} iniciado, PPID: {os.getppid()}")
    time.sleep(5)
    print(f"Hijo {os.getppid()} ahora es huérfano, nuevo PPID: {os.getppid()}")
else:
    print(f"Padre {os.getpid()} terminando pronto")