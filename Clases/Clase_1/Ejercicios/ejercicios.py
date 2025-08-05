"""Ejercicio 1: Redirección de Salida Básica
Objetivo: Crear un archivo con el listado de archivos y carpetas de un directorio.
Instrucción: Ejecuta un comando que guarde la salida del listado de archivos de tu directorio actual en un archivo llamado
 listado.txt.
"""
"ls > listado.txt"

"""Ejercicio 2: Redirección de Entrada y Contar Líneas
Objetivo: Leer un archivo y contar sus líneas sin usar la interfaz interactiva de wc.
Instrucción: Utiliza redirección para contar cuántas líneas tiene el archivo listado.txt que creaste en el ejercicio anterior.
"""
"cat listado.txt | wc -l" "Bien realizado"
"Sin usar wc: (parcialmente hecho)"
"nl listado.txt | egrep -o  [0-9]\{1,2\}"

"""Ejercicio 3: Redirección de Errores
Objetivo: Capturar errores generados por comandos inválidos.
Instrucción: Ejecuta un comando que intente listar un directorio inexistente y redirige el mensaje de error a un archivo llamado errores.log.
"""
"cat noexiste.txt 2> errores.log"

"""Ejercicio 4: Uso de Pipes
Objetivo: Encadenar comandos para filtrar información.
Instrucción: Lista los archivos de tu directorio actual y usa grep para mostrar solo los archivos que contienen la palabra "log" en su nombre.
"""
"ls | grep '.log'"

"""Ejercicio 5: Contar Archivos con Pipes
Objetivo: Contar cuántos archivos cumplen con un criterio.
Instrucción: Usa un pipe para contar cuántos archivos en tu directorio contienen la palabra "txt" en su nombre.
"""
"ls | grep 'txt'| wc -l"

"""Ejercicio 6: Redirección Combinada de Salida y Errores
Objetivo: Guardar la salida estándar y los errores en un solo archivo.
Instrucción: Ejecuta un comando que liste un directorio válido e inválido al mismo tiempo,
y redirige toda la salida (éxito y errores) a resultado_completo.log.
"""
"cat listado.txt &>> resultado_completo.log & cat noexiste.txt &>> resultado_completo.log"

"""
Ejercicio 7: Uso de /dev/null para Silenciar Salida
Objetivo: Ejecutar un comando sin mostrar nada en pantalla.
Instrucción: Ejecuta un comando que intente listar un directorio inexistente y envía toda su salida a /dev/null."""
"ls > /dev/null"

"""
Ejercicio 8: Creación de Alias con Descriptores de Archivo
Objetivo: Manipular descriptores de archivo manualmente.
Instrucción: Ejecuta un comando que cree un descriptor de archivo adicional para stdout,
lo use para escribir en salida_custom.log y luego lo cierre."""
"exec 3>salida_custom.txt & echo 'Prueba salida customs' >&3 & exec 3>&-"
"3>salida_custom.txt crea el file descriptor"
">&3 manda la salida del echo al file descriptor 3"
"exec 3>&- cierra el file descriptor 3"
