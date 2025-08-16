import random, time, json
from datetime import datetime
from multiprocessing import Queue, Lock, Pipe, Process, Event
import hashlib
import numpy as np
import os
import signal

def proceso_verificador(cola_frecuencia,cola_presion,cola_oxigeno, candado, evento_stop):
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

    while not evento_stop.is_set():
        try:
            datos_frecuencia = cola_frecuencia.get(timeout=1)
            datos_presion = cola_presion.get(timeout=1)
            datos_oxigeno = cola_oxigeno.get(timeout=1)
            #obtenemos el tiempo de los 3 bloques
        except:
            break

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
        #Generamos los datos para agregar al reporte (A su vez calculamos las medias)
        diccionario_reporte["media_frecuencia"] = int(np.mean(lista_frecuencias))
        diccionario_reporte["media_presion"] = int(np.mean(lista_presiones))
        diccionario_reporte["media_oxigeno"] = int(np.mean(lista_oxigeno))
        diccionario_reporte["num_alertas"] = cantidad_alertas
         


        # Eliminamos las variables que son basura en el campo de datos para el formato que necesitamos
        datos_a_borrar = ["timestamp","tipo","dato"]
        for data in [datos_frecuencia,datos_presion,datos_oxigeno]:
            for index in datos_a_borrar:
                del(data[index])
        
        # Creamos un diccionario de diccionarios
        bloque["datos"]["frecuencia"] = datos_frecuencia
        bloque["datos"]["presion"] = datos_presion
        bloque["datos"]["oxigeno"] = datos_oxigeno
        bloque["timestamp"] = timestamp
        bloque["hash"] = hashlib.sha256(f'{str(bloque["prev_hash"])}{json.dumps(bloque["datos"],sort_keys=True)}{str(timestamp)}'\
                                        .encode(encoding="utf-8")).hexdigest()

        candado.acquire()
        try:
            if not os.path.exists("blockchain.json"):
                blockchain = []
            else:
                with open("blockchain.json", "r") as file:
                    try: #Verificamos que el archivo json no esté vacio, si lo esta, manejamos el error
                        blockchain = json.load(file)
                        bloque["prev_hash"] = blockchain[-1]["hash"]
                    except json.JSONDecodeError:
                        blockchain = []

            bloque["indice"] = len(blockchain)
            blockchain.append(bloque)

            with open("blockchain.json","w") as file:
                blockchain = json.dump(blockchain, file)
            bloques_generados += 1
            diccionario_reporte["bloques_generados"] = bloques_generados

            with open("reporte.txt","w") as file:
                    json.dump(diccionario_reporte,file)
        finally:
            candado.release()
        bloque["prev_hash"] = bloque["hash"]
        
        print('Este es el bloque verificado: ', bloque)

def proc_analizador_datos(pipe_r, analz_var, cola_salida, evento_stop):
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


    while not evento_stop.is_set():
        try:
            if len(diccionarios_entrada) < 30: #Tenemos que asegurarnos que guardamos una ventana de los últimos 30 datos
                diccionarios_entrada.append(json.loads(pipe_r.recv()))
            elif len(diccionarios_entrada)>=30:
                diccionarios_entrada.pop(0)
                diccionarios_entrada.append(json.loads(pipe_r.recv()))

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
        except:
            evento_stop.wait(timeout=2)
            
        

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
    pipefrecuencia_r,pipefrecuencia_w = Pipe(False)#Conecta al generador de datos ----> analizadores
    pipepresion_r,pipepresion_w = Pipe(False)
    pipeoxigeno_r,pipeoxigeno_w = Pipe(False)
    cola_frecuencia = Queue()
    cola_presion = Queue()
    cola_oxigeno = Queue()
    candado_json = Lock()
    evento_stop = Event()



    colas = [cola_frecuencia,cola_presion,cola_oxigeno]
    #IMPORTANTE CERRAR LOS EXTREMOS DE LOS PIPES QUE NO SE USAN EN CADA PROCESO
    proceso_verf_nuevo = Process(target=proceso_verificador,kwargs={
        'cola_frecuencia': cola_frecuencia,
        'cola_presion': cola_presion,
        'cola_oxigeno': cola_oxigeno,
        'candado': candado_json,
        'evento_stop': evento_stop
    })

    proceso_frecuencia = Process(
        target=proc_analizador_datos,
        kwargs={"pipe_r":pipefrecuencia_r,'analz_var': 0, 'cola_salida': cola_frecuencia,'evento_stop': evento_stop}
    )
    proceso_presion = Process(
        target=proc_analizador_datos,
        kwargs={"pipe_r":pipepresion_r,'analz_var': 1, 'cola_salida': cola_presion,'evento_stop': evento_stop}
    )
    proceso_oxigeno = Process(
        target=proc_analizador_datos,
        kwargs={"pipe_r":pipeoxigeno_r,'analz_var': 2, 'cola_salida': cola_oxigeno,'evento_stop': evento_stop}
    )
    
    proceso_verf_nuevo.start()
    proceso_frecuencia.start()
    proceso_presion.start()
    proceso_oxigeno.start()
    
    def handler_salida(sig, frame):
        #global SALIR
        print("Señal de salida recibida. Cerrando procesos...\n")
        evento_stop.set()
        #SALIR = True
    signal.signal(signal.SIGINT, handler_salida)
    signal.signal(signal.SIGTERM, handler_salida)

    for cola in colas:
        cola.close()
    else:
        pipefrecuencia_r.close()
        pipepresion_r.close()
        pipeoxigeno_r.close()
        #GENERAMOS LOS DATOS
        datos_generados={}
        try:
            while not evento_stop.is_set():
                datos_generados["timestamp"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                datos_generados["frecuencia"] = random.randint(60,205)
                datos_generados["presion"] = (random.randint(110,205),random.randint(70,110))
                datos_generados["oxigeno"] = random.randint(70,100)
                #ENVIO LOS DATOS AL LOS PIPES CORRESPONDIENTES
                pipefrecuencia_w.send(json.dumps(datos_generados))
                pipepresion_w.send(json.dumps(datos_generados))
                pipeoxigeno_w.send(json.dumps(datos_generados))
            
                time.sleep(1)
        
        finally:
            #print("Esperando a verificador...")
            #proceso_verf_nuevo.join()
            print("Cerrando colas en el generador de datos.")
            cola_frecuencia.close()
            cola_presion.close()
            cola_oxigeno.close()
            print("\nCerrando pipes de escritura")
            pipefrecuencia_w.close()
            pipeoxigeno_w.close()
            pipepresion_w.close()
            print("Esperando al resto de procesos")
            
            proceso_frecuencia.join()
            
            proceso_presion.join()
            
            proceso_oxigeno.join()
            
            proceso_verf_nuevo.join()
            print("Todos los procesos cerrados correctamente.")
        


    
    
    
if __name__ == "__main__":
    proc_generador()


