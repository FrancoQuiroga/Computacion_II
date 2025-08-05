"""
5.1 Ejercicios Prácticos

    Escribe un script que acepte tres argumentos: -i (entrada), -o (salida) y -n (número de líneas a procesar).
    Modifica el script para validar que -n sea un entero positivo.
    Añade una opción --verbose para imprimir mensajes detallados.
    Usa argparse para definir argumentos obligatorios y opcionales.
    Implementa un comando --help para que el usuario vea la documentación.
"""
import argparse
parser = argparse.ArgumentParser(description='Ejercicio 1')
parser.add_argument('-i','--input', required=True,help='Entrada entera, y positiva')
parser.add_argument('-o', '--output',help='Salida del programa')
parser.add_argument('-n', type=int, required=True, help='Cantidad de líneas a analizar')
parser.add_argument('--verbose', default=True,action='store_true',help='Modo detallado activado')
args=parser.parse_args()
if args.verbose:
    print('Analizando si n es entero')
if args.n < 0:
    parser.error('El numero de n debería ser entero, mayor que cero')