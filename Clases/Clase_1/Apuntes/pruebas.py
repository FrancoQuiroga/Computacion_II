import sys
##print('Argumentos ingresados: ', sys.argv)
#import getopt
#try:
#    opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "input=", "output="])
#except getopt.GetoptError as err:
#    print(err)
#    sys.exit(2)
#
#for opt, arg in opts:
#    if opt in ("-h", "--help"):
#        print("Uso: script.py -i <archivo_entrada> -o <archivo_salida>")
#        sys.exit()
#    elif opt in ("-i", "--input"):
#        input_file = arg
#    elif opt in ("-o", "--output"):
#        output_file = arg

import argparse
"python3 pruebas.py -i listado.txt -o salida_custom.txt"
parser = argparse.ArgumentParser(description='Pruebas del parseo de argumentos')
parser.add_argument('-i', '--input', required=True, help='El argumento del archivo de entrada')
parser.add_argument('-o','--output',default='default_exit.txt', required=False,help='Archivo de salida')
args= parser.parse_args()

print(f'Archivo de entrada [{args.input}]')
print(f'Archivo de salida [{args.output}]')