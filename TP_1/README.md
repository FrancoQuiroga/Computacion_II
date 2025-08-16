# Trabajo Práctico N°1
- Proyecto de Franco Quiroga  
======================  
## Funcionalidades
======================  
### principal.py
Este script genera datos biométricos simulados de:
    - Frecuencia cardíaca (60-180 ppm)
    - Presión cardíaca (Presion sistólica[110-180], Presion Diastólica [70-110])
    - Oxigeno (Porcente % en sangre)
Una vez creados estos datos se calcula para cada uno lo siguiente:
    - Media de los últimos 30 segundos
    - Desviación estándar de los últimos 30 segundos
Por último se genera un sha256 con estos datos, guardado en blockchain.json
### verificar_cadena.py
Este script lee blockchain.json, recalcula los hashes, verifica encadenamiento e informa sobre bloques corruptos.

## Requisitos
======================  
Este proyecto usa de librerías externas:
    - numpy 2.2.6

Y de librerías internas (python 3.10.12):
    - random
    - time
    - datetime
    - json
    - multiprocessing
    - hashlib
    - os
    - signal

## Como usar el proyecto
======================  
1. Descargar la librería de numpy
```bash
pip install numpy 2.2.6
```
Es recomendado instalar esta librería en un entorno virtual
```bash
python3 -m venv [nombre_entorno_virtual]
source [nombre_entorno_virtual]/bin/activate
pip install numpy 2.2.6
```

2. Ejecutar principal.py (Si deseamos generar un nuevo blockchain)
. IMPORTANTE: tener en cuenta si tenemos entorno virtual o no.
```bash
python3 principal.py
```
Esto irá mostrando los hashes generados.
. IMPORTANTE: 
    Para detener el programa solo hace falta apretar "Ctrl+C"
El proyecto generará un archivo reporte.txt con información relevante del blockchain creado

3. Verificar la blockchain generada
Podemos verificar los bloque del hash en blockchain.json
(No es necesario estar en un entorno virtual, ni descargar numpy)
``` bash
python3 verificar_cadena.py
```

#### Gracias por leer

