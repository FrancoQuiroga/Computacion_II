import os,time
def hijo():
    print(os.getpid())
    os._exit(1)
print(os.getpid())
os.fork()
if os.getpid()!=0:time.sleep(10)
if os.getpid() == 0:
    os.execl(hijo)

os.wait()
