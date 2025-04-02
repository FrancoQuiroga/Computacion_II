import os,time
for i in range(2):
    process = os.fork()
    if process == 0:
        print(f'Soy un hijo, estoy laburando{os.getpid()}')
        time.sleep(15)
    else:
        print(f'Soy el padre: {os.getpid()}')
    



