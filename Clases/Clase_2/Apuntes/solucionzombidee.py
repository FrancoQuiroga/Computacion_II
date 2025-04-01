# Ver zombis:
#ps aux | grep 'Z'

# Solución práctica (modificación al código anterior):
import os, signal

pid = os.fork()
if pid == 0:
    print("Hijo terminando")
else:
    # Ignora señales de hijo terminado (evita zombis)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    print("Padre continuando sin wait()")