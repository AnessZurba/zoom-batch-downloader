import logging
import multiprocessing as mp
import os
import sys
import threading
import time

import psutil
from flask import Flask, request


def get_auth_code(port, timeout):
    mp_context = mp.get_context('spawn')
    queue = mp_context.Queue()
    server_process = _start_server(mp_context, queue, port)
    try:
        start_time = time.time()
        while queue.empty():
            if not server_process.is_alive():
                raise RuntimeError("OAuth server terminated unexpectedly")
            if timeout is not None and time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for authorization code")
            
            time.sleep(1)

        auth_code = queue.get()
        return auth_code
    finally:
        _stop_server(server_process)

def _start_server(mp_context, queue, port):
    server_process = mp_context.Process(
        name="zoom-downloader-oauth-server", daemon=True,
        target=_run_server_internal, args=(queue, port, os.getpid(),) 
    )
    server_process.start()
    return server_process
    
def _stop_server(server_process):
    if server_process.is_alive():
        server_process.terminate()

def _run_server_internal(queue, port, ppid):
    threading.Thread(target=_check_for_parent, args=(ppid,)).start()
    _suppress_flask_logging()

    app = Flask(__name__)

    @app.route('/')
    def home():
        auth_code = request.args.get('code')
        if auth_code:
            queue.put(auth_code) 
            return "Authorization code received! Please go back to the script."
        else:
            return "Code parameter not found."

    app.run(port=port)

def _check_for_parent(ppid, poll_interval=5):
    while True:
        time.sleep(poll_interval)
        if not psutil.pid_exists(ppid):
            os._exit(1)

def _suppress_flask_logging():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None