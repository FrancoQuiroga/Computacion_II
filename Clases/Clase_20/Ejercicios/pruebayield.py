import random, types
class generator:
    pass
def func_generadora():
    while True:
        frecuencia = random.randint(60,205)
        presion = random.randint(110,205)
        oxigeno = random.randint(70,100)
        ultimosdatos = [frecuencia,presion,oxigeno]
        print("DATOS GENERADOS")
        yield ultimosdatos


def func_alerta(generador):
    sum_datos = 0

    if isinstance(generador, types.GeneratorType):
        try:
            while True:
                datos = next(generador)
                print("DATOS SUMADOS")
                for dato in datos:
                    sum_datos += dato
        except KeyboardInterrupt:
            print('Programa cancelado')
            return sum_datos
        
    else: 
        print(f'La variable {generador} NO ES UN GENERADOR')
        raise BaseException

generador_falso= 'hola'
generador = func_generadora()
try:
    print(func_alerta(generador=generador_falso))
except BaseException as e:
    print("SE INTRODUJO UNA VARIABLE QUE NO ES GENERADORA")