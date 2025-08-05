import os

child = os.fork()
env = {'USER':'prueba','PATH':f'{os.get_exec_path()}'}

if child==0:
    os.

else:
    os.wait()