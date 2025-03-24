import getopt
import sys

#Estamos buscando un uso típico del tipo: script.py -i archivo.txt -o salida.txt

opciones, argumentos = getopt.getopt(sys.argv[1:], 'i:o:', ['input=','output='])
# - i: (Indica que i es una opcion, y los dos puntos que requier argumento) o: (Lo mismo que i) → -i -o ambos requieren un args

# ['input=','output='] --input y --output son dos opciones largas, y el = indica que ambas requieren un argumento
print (opciones, argumentos)



for opt,valor in opciones:
    if opt in ('-i', '--input'):
        archivo_entrada = valor

    if opt in ('-o', '--input'):
        archivo_salida = valor

print(f"Archivo de entrada: {archivo_entrada}")
print(f"Archivo de salida: {archivo_salida}")
