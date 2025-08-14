import random, time, json
from datetime import datetime
from multiprocessing import Queue, Lock, Pipe, Process
import hashlib
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
def generar_reporte():
    """Genera en un reporte.txt lo siguiente:  
    . Cantidad total de bloques generado  
    . Número de bloques con alertas  
    . Promedio general de frecuencias presion y oxígeno
    """
    pass

def proceso_verificador(cola_frecuencia,cola_presion,cola_oxigeno, candado):
    """datoentrante == {
    'tipo': tipo_de_dato_analizado,
    'timestamp':datetime,
    'media: float,
    'desv':float,
    'dato':int/list
    }  
    verifica los datos y genera un bloque hash sha256
    """
    bloque = {}
    ###Datos para el reporte
    lista_frecuencias = []
    lista_presiones = []
    lista_oxigeno = []
    cantidad_alertas = 0
    bloques_generados = 0
    diccionario_reporte = {}
    ###
    bloque["alerta"] = False
    bloque["datos"] = {}
    bloque["prev_hash"] = bloque.get("prev_hash", "") 
    while True:

        datos_frecuencia = cola_frecuencia.get()
        datos_presion = cola_presion.get()
        datos_oxigeno = cola_oxigeno.get()
        #obtenemos el tiempo de los 3 bloques
        timestamp = datos_oxigeno["timestamp"]
        # La alerta nunca será True, ya que cuando generamos los datos, los rangos estan por debajo de estos límites
        lista_frecuencias.append(datos_frecuencia["dato"])
        if datos_frecuencia["dato"] > 200:
            bloque["alerta"] = True
            cantidad_alertas += 1
        lista_presiones.append(datos_presion["dato"])
        if datos_presion["dato"][0] > 200:
            bloque["alerta"] = True
            cantidad_alertas += 1
        lista_oxigeno.append(datos_oxigeno["dato"])
        if 90 >= datos_oxigeno["dato"]:
            bloque["alerta"] = True
            cantidad_alertas += 1
        #Generamos los datos para agregar al reporte
        diccionario_reporte["media_frecuencia"] = int(np.mean(lista_frecuencias))
        diccionario_reporte["media_presion"] = int(np.mean(lista_presiones))
        diccionario_reporte["media_oxigeno"] = int(np.mean(lista_oxigeno))
        diccionario_reporte["num_alertas"] = cantidad_alertas
         
        #Hacemos una media de los datos

        # Eliminamos los datos que son basura para el formato que necesitamos
        datos_a_borrar = ["timestamp","tipo","dato"]
        for data in [datos_frecuencia,datos_presion,datos_oxigeno]:
            for index in datos_a_borrar:
                del(data[index])
        
        # Creamos un diccionario de diccionarios
        bloque["datos"]["frecuencia"] = datos_frecuencia
        bloque["datos"]["presion"] = datos_presion
        bloque["datos"]["oxigeno"] = datos_oxigeno
        bloque["hash"] = hashlib.sha256(string=f'{str(bloque["prev_hash"])}{str(bloque["datos"])}{timestamp}'\
                                        .encode(encoding="utf-8")).hexdigest()
        candado.acquire()
        try:
            if not os.path.exists("blockchain.json"):
                blockchain = {"bloques": []}
            else:
                with open("blockchain.json", "r") as file:
                    try: #Verificamos que el archivo json no esté vacio, si lo esta, manejamos el error
                        blockchain = json.load(file)
                    except json.JSONDecodeError:
                        blockchain = {"bloques": []}

            indice = len(blockchain["bloques"])
            bloque["indice"] = indice
            blockchain["bloques"].append(bloque)
            with open("blockchain.json","w") as file:
                blockchain = json.dump(blockchain, file)
            bloques_generados += 1
            diccionario_reporte["bloques_generados"] = bloques_generados
            print('ESTOY ABRIENDO EL REPORTE')
            with open("reporte.txt","w") as file:
                    json.dump(diccionario_reporte,file)
        finally:
            candado.release()
        bloque["prev_hash"] = bloque["hash"]
        #with open("blockchain.json","w") as file:
        print('Este es el bloque verificado: ', bloque)

def proc_analizador_datos(pipe_r, analz_var, cola_salida):
    """analz_var --> 0(frecuencia),1(presion),2(oxigeno)
    Esta funcion devuelve el siguiente diccionario:
    {
    'tipo': tipo_de_dato_analizado,
    'timestamp':datetime,
    'media: float,
    'desv':float,
    'dato':int/list
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
        # int o list que nos indica el valor del dato que analizamos
        ventana_datos.append(dato_analizar)
        if len(ventana_datos) > 30:
            ventana_datos.pop(0)
        datos_salida["timestamp"] = ultimo_diccionario["timestamp"]
        datos_salida["dato"] = dato_analizar

        #Media, y desviación estándar
        if type(dato_analizar) == list: #para presion sistolica/diastolica
            datos_sistolica.append(dato_analizar[0])
            datos_diastolica.append(dato_analizar[1])
            
            media_sistolica = float(np.mean(datos_sistolica))
            media_diastolica = float(np.mean(datos_diastolica))

            desv_sistolica = float(np.std(datos_sistolica,mean=media_sistolica))
            desv_diastolica = float(np.std(datos_diastolica,mean=media_diastolica))
            
            datos_salida["media"] = (media_sistolica,media_diastolica)
            datos_salida["desv"] = (desv_sistolica, desv_diastolica)
        
        else:
            datos_salida["media"] = float(np.mean(ventana_datos))
            datos_salida["desv"] = float(np.std(ventana_datos, mean=datos_salida["media"]))
        #Colocamos el diccionario en la Queue
        cola_salida.put(datos_salida)

        

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
    pipes= [pipefrecuencia_r,pipefrecuencia_w,pipepresion_r,pipepresion_w,pipeoxigeno_r,pipeoxigeno_w]
    cola_frecuencia = Queue()
    cola_presion = Queue()
    cola_oxigeno = Queue()
    colas = [cola_frecuencia,cola_presion,cola_oxigeno]
    candado_json = Lock()
    #IMPORTANTE CERRAR LOS EXTREMOS DE LOS PIPES QUE NO SE USAN EN CADA PROCESO
    proceso_verf_nuevo = Process(target=proceso_verificador,kwargs={
        'cola_frecuencia': cola_frecuencia,
        'cola_presion': cola_presion,
        'cola_oxigeno': cola_oxigeno,
        'candado': candado_json
    })
    proceso_verf_nuevo.start()
    

    #proceso_verificador_creado = os.fork()
    #if proceso_verificador_creado == 0:
    #    for pipe in pipes:
    #        os.close(pipe)
    #    proceso_verificador(cola_frecuencia=cola_frecuencia,cola_presion=cola_presion,cola_oxigeno=cola_oxigeno, candado=candado_json)

    proceso_frecuencia = os.fork()
    if proceso_frecuencia == 0:
        pipes.remove(pipefrecuencia_r)
        for pipe in pipes:
            os.close(pipe)
        proc_analizador_datos(pipe_r=pipefrecuencia_r, analz_var=0,cola_salida=cola_frecuencia)

    proceso_presion = os.fork()
    if proceso_presion == 0:
        pipes.remove(pipepresion_r)
        for pipe in pipes:
            os.close(pipe)
        proc_analizador_datos(pipe_r=pipepresion_r, analz_var=1,cola_salida=cola_presion)

    proceso_oxigeno = os.fork()
    if proceso_oxigeno == 0:
        pipes.remove(pipeoxigeno_r)
        for pipe in pipes:
            os.close(pipe)
        proc_analizador_datos(pipe_r=pipeoxigeno_r, analz_var=2,cola_salida=cola_oxigeno)
    for cola in colas:
        cola.close()
    else:
        os.close(pipefrecuencia_r)
        os.close(pipepresion_r)
        os.close(pipeoxigeno_r)
        #GENERAMOS LOS DATOS
        datos_generados={}
        while True:
            datos_generados["timestamp"] = datetime.now().strftime('%Y,%m,%dT%H:%M:%S')
            datos_generados["frecuencia"] = random.randint(60,205)
            datos_generados["presion"] = (random.randint(110,205),random.randint(70,110))
            datos_generados["oxigeno"] = random.randint(70,100)
            #ENVIO LOS DATOS AL LOS PIPES CORRESPONDIENTES
            os.write(pipefrecuencia_w, json.dumps(datos_generados).encode())
            os.write(pipepresion_w,json.dumps(datos_generados).encode())
            os.write(pipeoxigeno_w, json.dumps(datos_generados).encode())

            time.sleep(1)


    
    
    
if __name__ == "__main__":
    proc_generador()


