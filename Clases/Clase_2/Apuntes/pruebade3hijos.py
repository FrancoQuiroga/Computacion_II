import os, time, random

for _ in range(3):
    pid = os.fork()
    if pid == 0:
        nrohijo = _+1
        print(f"Hijo {os.getpid()} iniciando, nro:{nrohijo}")
        time.sleep(random.randint(1,3))
        print(f"Hijo {os.getpid()} terminando, nro: {nrohijo}")
        os._exit(0)  # Importante!

# Padre espera hijos
for _ in range(3):
    os.wait()