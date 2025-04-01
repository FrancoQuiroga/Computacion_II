import os, time

pid = os.fork()
if pid == 0:
    print("Hijo trabajando...")
    time.sleep(5)
    print("Hijo terminó")
else:
    print("Padre esperando...")
    os.wait()
    print("Padre continuando")