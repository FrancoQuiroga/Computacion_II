import os, time

pid = os.fork()
if pid > 0:
    print("[PADRE] Terminando rápidamente")
    os._exit(0)
else:
    print("[HIJO] Huérfano. Padre desaparecido. Mi nuevo padre será init.")
    time.sleep(10)  # Observar con `ps -o pid,ppid,stat,cmd`
#import os, time
#
#pid = os.fork()
#if pid == 0:
#    print(f"Hijo {os.getpid()} terminando")
#else:
#    print(f"Padre {os.getpid()} no esperando al hijo")
#    time.sleep(20)  # Durante este tiempo, verifica con `ps aux | grep Z`