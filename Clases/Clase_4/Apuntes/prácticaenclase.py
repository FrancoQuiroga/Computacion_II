import os

# Crear un pipe
read_pipe, write_pipe = os.pipe()
print(type(read_pipe),type(write_pipe))
# En el proceso padre
pid = os.fork()

if pid > 0:  # Proceso padre(escritor)
    os.close(read_pipe)  # Cerramos el extremo que no usamos
    mensaje = "Hola desde el padre".encode()
    os.write(write_pipe, mensaje)
    mensaje2 = 'HOLA DESDE EL PADRE 2'.encode()
    os.write(write_pipe,mensaje2)
    os.close(write_pipe)
else:  # Proceso hijo(lector)
    os.close(write_pipe)  # Cerramos el extremo que no usamos
    datos = os.read(read_pipe, 100)
    print(f"Hijo recibió: {datos.decode()}")
    os.close(read_pipe)

