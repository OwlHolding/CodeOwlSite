import sys
from multiprocessing import Process, Pipe
from threading import RLock
from pylint import epylint as lint

sand_lock = RLock()

blocked = ['absl-py', 'astunparse', 'cachetools', 'certifi', 'charset-normalizer', 'colorama', 'flatbuffers', 'gast',
           'google-auth', 'google-auth-oauthlib', 'google-pasta', 'gpt-2-simple', 'grpcio', 'h5py', 'idna',
           'importlib-metadata', 'keras', 'keras-preprocessing', 'libclang', 'markdown', 'numpy', 'oauthlib',
           'opt-einsum', 'protobuf', 'pyasn1', 'pyasn1-modules', 'regex', 'requests', 'requests-oauthlib', 'rsa', 'six',
           'tensorboard', 'tensorboard-data-server', 'tensorboard-plugin-wit', 'tensorflow',
           'tensorflow-io-gcs-filesystem', 'termcolor', 'tf-estimator-nightly', 'toposort', 'tqdm', 'typing-extensions',
           'urllib3', 'werkzeug', 'wheel', 'wrapt', 'zipp']


def debug(pipe):
    while pipe.poll(None):
        text = pipe.recv()
        for lib in blocked:
            if lib in text:
                pipe.send("Unable to import")
        with open("sandbox_element.py", "w", encoding='utf-8') as file:
            print(text)
            file.write(text)
        a, pylint_stderr = lint.py_run('sandbox_element.py', return_std=True)
        a = a.getvalue()
        a = a.split("\n")
        Ans = []
        for i in range(len(a)):
            if a[i].find('error (E') != -1:
                Ans.append(a[i])
        e = []
        for line in Ans:
            if line.find(") ") != -1:
                e.append(line[line.find(") ")+1:])
        pipe.send("\n".join(e))


def sand_init():
    global pipe
    pipe, endpipe = Pipe()
    server = Process(target=debug, args=(endpipe,), daemon=True)
    server.start()


def sand_generate(code):
    text = code
    pipe.send(text)
    data = pipe.recv()
    print(data)
    return data


if __name__ == 'main':
    sand_init()
    pipe.send(sys.argv[1])
    print(pipe.recv())
