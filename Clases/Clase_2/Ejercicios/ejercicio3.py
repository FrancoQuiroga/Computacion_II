import os

child = os.fork()

if child==0:
    os.execlp('deamonejercicio3','python3')

else:
    os.wait()