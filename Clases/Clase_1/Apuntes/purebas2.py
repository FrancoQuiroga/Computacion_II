import argparse
"python3 pruebas.py -i 1 -o salida_custom.txt"
parser = argparse.ArgumentParser(description='Pruebas del parseo de argumentos')
parser.add_argument('-i', '--input', required=True,type=int, help='El argumento del archivo de entrada')
parser.add_argument('-o','--output',default='default_exit.txt', required=False,help='Archivo de salida')
parser.add_argument('archivo',help='Argumento posicional')
parser.add_argument("--modo", choices=["rapido", "lento"], help="Modo de ejecución")
args= parser.parse_args()

print(f'Archivo de entrada [{args.input}]')
print(f'Archivo de salida [{args.output}]')