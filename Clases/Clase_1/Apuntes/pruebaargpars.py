import argparse

parser = argparse.ArgumentParser(description='Procesa Archivos de entrada y salida')

parser.add_argument('-i','--input',help='Archivo de entrada',required=True)
parser.add_argument('-o','--output',help='Archivo de salida',default='salida_default.txt')
args = parser.parse_args()

print(f"Archivo de entrada: {args.input}")
print(f"Archivo de salida: {args.output}")