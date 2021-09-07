from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread


class Http_Handler(BaseHTTPRequestHandler):
    def __init__(self, on_receive, *args, **kwargs):
        self.on_receive = on_receive
        # BaseHTTPRequestHandler calls do_GET **inside** __init__ !!!
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        #print("GET request,\nPath: %s\nHeaders:\n%s\n",
              #str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(
            self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')

        keys = []
        values = []
        fields = post_data.split('&')

        for field in fields:
            (key, value) = field.split('=')
            keys.append(key)
            values.append(value)

        asnwer = self.on_receive(keys, values)
        self._set_response()
        self.wfile.write(asnwer.encode('utf-8'))

class HttpServer:
    def __init__(self, port, on_receive):
        server_address = ('', port)
        http_handler = partial(Http_Handler, on_receive)
        httpd = HTTPServer(server_address, http_handler)

        self.thread = Thread(target=self.run, args=([httpd, ]))
        self.thread.start()

    def run(self, httpd):

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

        httpd.server_close()
        print('HTTP_SERVER: closing')
