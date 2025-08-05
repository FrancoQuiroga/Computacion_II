import os

pipe_escritura, pipe_lectura = os.pipe()

nuevo_proceso = os.fork() # 0 es cuando el proceso es el hijo, pid cuando es el proceso padre

if nuevo_proceso != 0:
    os.close(pipe_lectura) #Cierra el extremo que el proceso no va a utilizar
    mensaje = {'Hola':'soy','Un':'diccionario'}
    escribo=os.fdopen(pipe_escritura,'w')
    escribo.write(str(mensaje))
    escribo.flush()
    escribo.close()
    os.waitpid(nuevo_proceso, 0)


else:#hijo
    os.close(pipe_escritura)
    leo= os.fdopen(pipe_lectura,'r')
    leo.read().readline().strip()
    leo.close(pipe_lectura)



