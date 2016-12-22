#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import urlparse
import subprocess
from ledstrip import LEDStrip

strip = LEDStrip()

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        self._set_headers()
        parsed_path = urlparse.urlparse(self.path)
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length)
        request = json.loads(post_data)

        if (request["action"]):
            method = getattr(strip, request["action"], None)
            if method:
                if (method(request)):
                    self.success("Success.")
                else:
                    self.error("Failure.")
            else:
                self.error("Invalid action given.")
        else:
            self.error("No action given.")

    def do_HEAD(self):
        self._set_headers()

    def success(self, message):
        self.send_response(200, json.dumps({"result": "success", "message": message}))

    def error(self, message):
        self.send_response(500, json.dumps({"result": "error", "message": message}))

def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
