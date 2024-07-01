import logging
import multiprocessing as mp
import sys
import time

from flask import Flask, request

app = Flask(__name__)

mp_context = mp.get_context('spawn')
queue = None  # Holds the queue in the child process

@app.route('/')
def home():
    auth_code = request.args.get('code')
    if auth_code:
        queue.put(auth_code) 
        return "Authorization code received! Please go back to the script."
    else:
        return "Code parameter not found."

def _run_server_internal(passed_queue, port):
    global queue
    queue = passed_queue

    # Suppress Flask and Werkzeug logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    app.run(port=port)

def _start_server(queue, port):
    server_process = mp_context.Process(target=_run_server_internal, args=(queue, port,))
    server_process.start()
    return server_process
    
def _stop_server(server_process):
    if server_process and server_process.is_alive():
        server_process.terminate()

def get_auth_code(port, timeout):
    queue = mp_context.Queue()
    server_process = _start_server(queue, port)
    try:
        start_time = time.time()
        while queue.empty():
            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for authorization code")
            time.sleep(1)

        auth_code = queue.get()
        return auth_code
    finally:
        _stop_server(server_process)
