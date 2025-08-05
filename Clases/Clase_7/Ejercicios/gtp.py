import signal
import os
import time
contador=0
contadorsignal=0
def handler(signum, frame):
    global contador    
    contador+=1
    print(f"\nSeñal {signum} recibida.No puedo ser interrumpido!")
    print(f"Soy el contador de Ctrl+c: {contador}")
def manejador_alrm(signum,frame):
    #print('Se terminó el programa!')
    #exit()
    global contadorsignal
    contadorsignal+=1
    print(f"Atrapé la señal SIGALRM, nro de señal:{signum}")
    print(f"Soy el contador de SIGALRM: {contadorsignal}")


# Paso 1: Registrar el manejador para SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, handler)
signal.signal(14,manejador_alrm) #Se puede reemplazar el manejador default de cualquier alarma, excepto las privilegiadas

# Paso 2: Simular trabajo
print(f"PID: {os.getpid()}. Esperando señales...")
print('Estoy emitiendo una señal SIGALRM!!')
signal.alarm(3) # Si no se maneja la señal alrm, el programa se interrumpe
signal.alarm(6) #Varias alarmas sucesivas se reemplazan entre sí
signal.alarm(9)
while True:
    time.sleep(1)
    print(".", end="", flush=True)