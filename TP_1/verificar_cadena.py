import json
import hashlib
import os
def verificar_blockchain():
    """ El archivo json tiene el siguiente formato:
    [bloque1,bloque2,...,bloqueN]
    donde bloqueN tiene el siguiente formato:
{"alerta": false, 
"datos": {
"frecuencia": {"media": 109.0, "desv": 0.0}, 
"presion": {"media": [196.0, 102.0], "desv": [0.0, 0.0]}, 
"oxigeno": {"media": 95.0, "desv": 0.0}},
"prev_hash": "", "hash":"",
"indice": 0}  
Necesitamos recalcular el hash de la siguiente manera:  
hashlib.sha256
(string=f'{str(bloque["prev_hash"])}{str(bloque["datos"])}{timestamp}'\
                                        .encode(encoding="utf-8")).hexdigest()
    """
    hash_previo_calculado = ""
    with open("blockchain.json","r") as file:
        try:
            blockchain = json.load(file)
        except json.JSONDecodeError:
            print("El ARCHIVO BLOCKCHAIN ESTA VACÍO O CORRUPTO")

        for bloque in blockchain:
            #primero recalculamos el hash(como esto es determinístico podemos usar los datos para el hash actual)
            indice = bloque["indice"]
            if hash_previo_calculado != bloque["prev_hash"] and hash_previo_calculado != "": 
                print(f'Hay un problema de encadenamiento entre el bloque {indice -1} y {indice} \n ')
            
            hash_recalculado = hashlib.sha256(f'{str(bloque["prev_hash"])}{json.dumps(bloque["datos"],sort_keys=True)}{str(bloque["timestamp"])}'.encode(encoding="utf-8")).hexdigest()
        
            if hash_recalculado != bloque["hash"]:
                print(f"El bloque {indice} está corrupto\n")
                #hash_previo_calculado = bloque["prev_hash"]
                continue
            else: print(f"El bloque {indice} no tiene problemas.")
            

            
                







if __name__ == "__main__":
    verificar_blockchain()