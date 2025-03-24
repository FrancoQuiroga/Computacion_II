import argparse

parser = argparse.ArgumentParser(description='Indicador de direccionamiento de archivos')

parser.add_argument('-i','--input',help='Archivo de entrada',required=True)
parser.add_argument('-o', '--output',help='Archivo de salida',default='salida.txt')

argumentos = parser.parse_args()
mensaje = f"Procesando el archivo de entrada: '{argumentos.input}'. Los resultados se guardarán en: '{argumentos.output}'"
if argumentos.output == 'salida.txt':
    mensaje += '(valor por defecto).'
print(f'{mensaje}')

