#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import random
import codecs
import os
from pathlib import Path

from hashtable import HashTable

FLAG = os.environ.get('FLAG', 'not_a_real_flag')
FORTUNE_LOCATION = Path(__file__).parent / 'fortune'

def get_fortunes(location, transform=lambda x: x):
    data = {}
    for f in location.glob('*'):
        if f.is_file() and f.suffix == '':
            data[f.name] = list(filter(None, map(transform, f.read_text().split('\n%\n'))))

    return data

NORMAL = get_fortunes(FORTUNE_LOCATION)
OFFENSIVE = get_fortunes(FORTUNE_LOCATION / 'off', lambda x: codecs.encode(x, 'rot13'))
TEMPLATE_PATH = Path(__file__).parent / 'template.html'

class TooManyArguments(Exception):
    pass

def random_fortune(offensive=False, category=None):
    fort = NORMAL
    if offensive and random.randint(0,1) == 1:
        fort = OFFENSIVE
    cat = random.choice(list(fort))
    return random.choice(fort[cat])

def parse_url(path):
    if '?' not in path:
        return (path, HashTable())

    path, params = path.split('?', maxsplit=1)
    parsed_params = HashTable()
    par_list = params.split('&')
    if len(par_list) > 512:
        raise TooManyArguments()
    for p in par_list:
        if '=' not in p:
            parsed_params[p] = ''
        else:
            k, v = p.split('=', maxsplit=1)
            parsed_params[k] = v

    return path, parsed_params

class Server(BaseHTTPRequestHandler):
    def _bad_request(self):
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Bad request')

    def _error(self):
        self.send_response(500)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(FLAG.encode('utf-8'))

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        try:
            path, params = parse_url(self.path)
            self._set_response()
            offensive=False
            if 'offensive' in params:
                offensive = params['offensive'].lower() == 'true'
            self.wfile.write(TEMPLATE_PATH.read_text()
                    .replace('%%FORTUNE%%', random_fortune(offensive=offensive)).encode('utf-8'))
        except TooManyArguments:
            self._bad_request()
        except:
            logging.exception('Something went wrong')
            self._error()

def run(server_class=HTTPServer, handler_class=Server, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    run()
