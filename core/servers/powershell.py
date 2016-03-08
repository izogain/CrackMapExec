import BaseHTTPServer
import ssl
import string
from random import sample
from threading import Thread
from BaseHTTPServer import BaseHTTPRequestHandler
from core.helpers import strip_powershell_comments, change_function_name

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path[1:] == self.urlpath:
            self.send_response(200)
            self.end_headers()
            with open(self.psfile_path, 'r') as script:
                script = change_function_name(script.read(), self.obfs_function_name)
                script = strip_powershell_comments(script)
                self.wfile.write(script)

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        length = int(self.headers.getheader('content-length'))
        data = self.rfile.read(length)

        self.output_callback(data)

class PowershellServer:

    def __init__(self, server_type, port, urlpath, psfile_path, output_callback):

        self.server_type = str(server_type).lower()
        self.port = int(port)
        self.urlpath = urlpath
        self.obfs_function_name = ''.join(sample(string.ascii_letters, 10))
        self.psfile_path = psfile_path
        self.output_callback = output_callback

    def start_server(self):
        if self.server_type == 'http':
            print 'Starting HTTP server on port {}'.format(self.port)
            http_server = BaseHTTPServer.HTTPServer(('0.0.0.0', self.port), RequestHandler)
            http_server.urlpath = self.urlpath
            http_server.obfs_function_name = self.obfs_function_name
            http_server.psfile_path = self.psfile_path
            http_server.output_callback = self.output_callback

            t = Thread(name='http_server', target=http_server.serve_forever)
            t.setDaemon(True)
            t.start()

        elif self.server_type == 'https':
            print 'Starting HTTPS server on port {}'.format(self.port)
            https_server = BaseHTTPServer.HTTPServer(('0.0.0.0', self.port), RequestHandler)
            https_server.socket = ssl.wrap_socket(https_server.socket, certfile='data/cme.crt', keyfile='data/cme.key', server_side=True)
            https_server.urlpath = self.urlpath
            https_server.obfs_function_name = self.obfs_function_name
            https_server.psfile_path = self.psfile_path
            https_server.output_callback = self.output_callback

            t = Thread(name='https_server', target=https_server.serve_forever)
            t.setDaemon(True)
            t.start()