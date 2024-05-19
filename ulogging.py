import os

def do_log(msg: str):
    os.write(1, (msg + '\n').encode('utf-8'))
