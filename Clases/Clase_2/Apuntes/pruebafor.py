import os

pid = os.fork()
if pid == 0:
    print("Soy el hijo (PID:", os.getpid(), ") PPID:", os.getppid())
else:
    print("Soy el padre (PID:", os.getpid(), ") Hijo:", pid)