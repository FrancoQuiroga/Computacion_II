import random, time, json
from datetime import datetime
from multiprocessing import Queue
import numpy as np
import os


def proc_principal():
    """PROCESO PRINCIPAL

    Orquestador de todo el programa, debe ejecutar el flujo de  
    procesamiento en orden y correctamente
    No sé si es necesario :/
    """
    # 1-Genero el dato,(HECHO)
    # 2- Mando el dato al FIFO/PIPE (HECHO)
    # 2.1- Crear los 3 procesos (frecuencia,presion,oxigeno)
    # 3- El dato es leído por cada proceso(pero no modificado)
    # 4- El analizador debería verificar que los datos sean procesados
    # en orden (Es decir que los tiempos sean correctos)

def proceso_verficador(cola_frecuencia,cola_presion,cola_oxigeno):
    pass
def proc_analizador_datos(pipe_r, analz_var, cola_salida):
    """analz_var --> 0(frecuencia),1(presion),2(oxigeno)
    Esta funcion devuelve el siguiente diccionario:
    {
    'tipo': tipo_de_dato_analizado,
    'timestamp':...,
    'media':....,
    'desv':....
    }
    """
    #Primero nos aseguramos que analizamos el dato correcto
    enum = analz_var
    if enum == 0:
        enum = "frecuencia"
    elif enum == 1:
            enum = "presion"
    elif enum == 2:
            enum = "oxigeno"
    else:
        raise Exception('ERROR EN EL USO DE ANALIZADOR DE DATOS')
    
    
    diccionarios_entrada = []
    ventana_datos = []
    datos_sistolica = []
    datos_diastolica = []
    datos_salida = {}
    datos_salida["tipo"] = enum


    while True:
        if len(diccionarios_entrada) < 30: #Tenemos que asegurarnos que guardamos una ventana de los últimos 30 datos
            diccionarios_entrada.append(json.loads(os.read(pipe_r,100).decode()))
        elif len(diccionarios_entrada)>=30:
            diccionarios_entrada.pop(0)
            diccionarios_entrada.append(json.loads(os.read(pipe_r,100).decode()))

        ultimo_diccionario = diccionarios_entrada[-1]
        dato_analizar = ultimo_diccionario[enum]
        ventana_datos.append(dato_analizar)
        if len(ventana_datos) > 30:
            ventana_datos.pop(0)
        datos_salida["timestamp"] = ultimo_diccionario["timestamp"]

        #Media, y desviación estándar
        if type(dato_analizar) == list: #para presion sistolica/diastolica
            datos_sistolica.append(ventana_datos[-1][0])
            datos_diastolica.append(ventana_datos[-1][1])

            media_sistolica = np.mean(datos_sistolica)
            media_diastolica = np.mean(datos_diastolica)

            desv_sistolica = np.std(datos_sistolica,mean=media_sistolica)
            desv_diastolica = np.std(datos_diastolica,mean=media_diastolica)
            
            datos_salida["media"] = (media_sistolica,media_diastolica)
            datos_salida["desv"] = (desv_sistolica, desv_diastolica)
        
        else:
            #sumatoria_datos_media += dato_analizar
            datos_salida["media"] = np.mean(ventana_datos)
            datos_salida["desv"] = np.std(ventana_datos, mean=datos_salida["media"])


        #FALTA DEVOLVER LOS DATOS A LA QUEUE, QUE ES RECIBIDA MEDIANTE LA COLA DE SALIDA
        print(f'DATO PARA ANALIZAR: {(ultimo_diccionario)}')
        print(f'DATOS DE SALIDA {datos_salida}')
        #Guardar lo anterior en una ventana de 30 segundos

        

def proc_generador():
    """PROCESO GENERADOR DE DATOS  
    Este proceso genera datos simulados de presiones arteriales,
    Generará un dato por segundo retornando el sig diccionario:  
    {'timestamp': 'YYYY,MM,DDTHH:MM:SS',
    'frecuencia': int(60-180),
    'presion': type=tuple;(int(110-180),int(70-110));(sistólica/diastólica),
    'oxigeno': (%), int(90-100)
    }
    """
    #Líneas de Setup
    pipefrecuencia_r,pipefrecuencia_w = os.pipe() #Conecta al generador de datos ----> analizadores
    pipepresion_r,pipepresion_w = os.pipe()
    pipeoxigeno_r,pipeoxigeno_w = os.pipe()

    cola_frecuencia = Queue(maxsize=60)
    cola_presion = Queue(maxsize=60)
    cola_oxigeno = Queue(maxsize=60)

    #IMPORTANTE CERRAR LOS EXTREMOS DE LOS PIPES QUE NO SE USAN EN CADA PROCESO
    proceso_verificador = os.fork()
    if proceso_verificador == 0:
        proceso_verificador(cola_frecuencia=cola_frecuencia,cola_presion=cola_presion,cola_oxigeno=cola_oxigeno)

    proceso_frecuencia = os.fork()
    if proceso_frecuencia == 0:
        os.close(pipefrecuencia_w)
        os.close(pipepresion_r)
        os.close(pipepresion_w)
        os.close(pipeoxigeno_r)
        os.close(pipeoxigeno_w)
        proc_analizador_datos(pipe_r=pipefrecuencia_r, analz_var=0,cola_salida=cola_frecuencia)

    proceso_presion = os.fork()
    if proceso_presion == 0:
        os.close(pipefrecuencia_r)
        os.close(pipefrecuencia_w)
        os.close(pipepresion_w)
        os.close(pipeoxigeno_r)
        os.close(pipeoxigeno_w)
        proc_analizador_datos(pipe_r=pipepresion_r, analz_var=1,cola_salida=cola_presion)

    proceso_oxigeno = os.fork()
    if proceso_oxigeno == 0:
        os.close(pipefrecuencia_r)
        os.close(pipefrecuencia_w)
        os.close(pipepresion_r)
        os.close(pipepresion_w)
        os.close(pipeoxigeno_w)
        proc_analizador_datos(pipe_r=pipeoxigeno_r, analz_var=2,cola_salida=cola_oxigeno)

    else:
        os.close(pipefrecuencia_r)
        os.close(pipepresion_r)
        os.close(pipeoxigeno_r)
        #GENERAMOS LOS DATOS
        datos_generados={}
        while True:
            datos_generados["timestamp"] = datetime.now().strftime('%Y,%m,%dT%H:%M:%S')
            datos_generados["frecuencia"] = random.randint(60,180)
            datos_generados["presion"] = (random.randint(110,180),random.randint(70,110))
            datos_generados["oxigeno"] = random.randint(90,100)
            #ENVIO LOS DATOS AL LOS PIPES CORRESPONDIENTES
            os.write(pipefrecuencia_w, json.dumps(datos_generados).encode())
            os.write(pipepresion_w,json.dumps(datos_generados).encode())
            os.write(pipeoxigeno_w, json.dumps(datos_generados).encode())

            time.sleep(1)

    os.close(pipefrecuencia_w)
    os.close(pipepresion_w)
    os.close(pipeoxigeno_w)
    if os.WIFEXITED and os.WTERMSIG() == 2: ##REVISAR BIEN COMO TERMINA ESTO
        os.waitpid(proceso_verificador)
        os.waitpid(proceso_frecuencia)
        os.waitpid(proceso_presion)
        os.waitpid(proceso_oxigeno)

    
    
proc_generador()


