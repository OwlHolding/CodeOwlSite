'''GPT-2 multithread controller. Call init() before use '''

import gpt_2_simple as gpt2
import os
import sys
from multiprocessing import Process, Pipe
from threading import RLock

MODEL_DIR = os.path.abspath(__file__).replace('neuralengine.py', 
    'static/checkpoint')
MODEL_NAME = "355M"
LENGTH = 100

lock = RLock()

def gptserver(pipe):
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, model_dir=MODEL_DIR, model_name=MODEL_NAME)
    print('Model uploaded successfully')
    while pipe.poll(None):
        print('Response generation started...')
        pipe.send(gpt2.generate(sess, 
        prefix=pipe.recv(), model_dir=MODEL_DIR, 
            model_name=MODEL_NAME, length=LENGTH, return_as_list=True)[0])

def init():
    global pipe
    pipe, endpipe = Pipe()
    server = Process(target=gptserver, args=(endpipe,), daemon=True)
    server.start()

def generate(text):
    pipe.send(text)
    return pipe.recv()

if __name__ == '__main__':
    init()
    pipe.send(sys.argv[1])
    print(pipe.recv())
