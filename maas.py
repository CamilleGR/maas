import logging
import argparse
import time
import sys
import os 

# Lecture du fichier de reponse HTTP 
def read_file_content(fileName):
    if not os.path.exists(fileName):
        raise Exception("File "+fileName+" doesn't exists or is not readable.")
    with open(fileName, 'r') as fichier:
        contenu = fichier.read()
    return contenu

# parsing des headers
def get_headers(headers_str):
    headers = {}
    if not headers_str.strip():
        return headers

    for header in headers_str.split(';'):
        # On ignore les entrees vides
        if  header.strip():
            key_value = header.split(':', 1)
            if len(key_value) == 2:
                headers[key_value[0].strip()] = key_value[1].strip()
    return headers

# Detection de la version de Python
if sys.version_info[0] == 2:
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import TCPServer
    ServerClass = TCPServer
    HandlerClass = SimpleHTTPRequestHandler
elif sys.version_info[0] == 3:
    from http.server import SimpleHTTPRequestHandler, HTTPServer
    ServerClass = HTTPServer
    HandlerClass = SimpleHTTPRequestHandler


def get_banner():
    banner_str = ""
    banner_str += "      _______     ___ ___       ____       ____       _____ " + os.linesep
    banner_str += "    _|_______|   |   |   |     /    |     /    |     / ___/ " + os.linesep
    banner_str += "  / _|-------|   | _   _ |    |  o  |    |  o  |    (   \\_  " + os.linesep
    banner_str += " | | | | | | |   |  \\_/  |    |     |    |     |     \\__  | " + os.linesep
    banner_str += " | |_| | | | |   |   |   |    |  _  |    |  _  |     /  \\ | " + os.linesep
    banner_str += "  \\__| | | | |   |   |   |    |  |  |    |  |  |     \\    | " + os.linesep
    banner_str += "     |_______|   |___|___|    |__|__|    |__|__|      \\___| " + os.linesep
    return banner_str

### CLI Configuration
def print_banner():
    print(get_banner());

print_banner()
parser = argparse.ArgumentParser()
parser.add_argument("-v","--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-p","--port", type=int, help="port to serve", default=1337)
parser.add_argument("-d","--delay", help="delay to apply (in ms)", default=0)
parser.add_argument("-rf","--responseFile", help="File containing the body response", default=None)
parser.add_argument("-rh","--responseHeaders", help="Response headers (separated by ;)", default="Content-Type: application/json")
parser.add_argument("-rc","--responseCode", type=int, help="Response code", default=200)
args = parser.parse_args()



if not args.responseFile : 
    SERVICE_RESPONSE = '{"status":"ok"}\r\n'.encode()
else : 
    SERVICE_RESPONSE = read_file_content(args.responseFile).encode()

### SELECT VERBOSITY

if args.verbose : 
    logging.basicConfig(filename=None, level=logging.DEBUG,
                        format='%(asctime)s - %(message)s')
else: 
    logging.basicConfig(filename=None, level=logging.INFO,
                        format='%(asctime)s - %(message)s')



HEADERS = get_headers(args.responseHeaders)

class Handler(HandlerClass):
    
     def do_GET(self):
        time.sleep(float(args.delay)*0.001)
        logging.info("Client: %s | Methode: %s | Chemin: %s | Query: %s" %
                     (self.client_address[0], self.command, self.path,
                      self.path.split('?')[1] if '?' in self.path else 'None'))
        self.send_response(args.responseCode)
        logging.debug("Client: %s | Methode: %s | Chemin: %s | Headers: %s " %
                    (self.client_address[0], self.command, self.path, dict(self.headers)))
        
        for k,v in HEADERS.items():
            self.send_header(k,v)
        if 'Content-Length' in HEADERS.keys() :
            self.send_header('Content-Length', len(SERVICE_RESPONSE))
        self.end_headers()
        self.wfile.write(SERVICE_RESPONSE)

    def do_POST(self):
        time.sleep(float(args.delay)*0.001)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else ''
        logging.info("Client: %s | Methode: %s | Chemin: %s | Body size: %d" %
                     (self.client_address[0], self.command, self.path, len(body)))
        logging.debug("Client: %s | Methode: %s | Chemin: %s | Headers: %s | Body size: %d | Body: " %
                    (self.client_address[0], self.command, self.path,
                    dict(self.headers), len(body)))
        logging.debug(body.decode("utf-8"))
        self.send_response(args.responseCode)
        for k,v in HEADERS.items():
            self.send_header(k,v)
        if 'Content-Length' in HEADERS.keys() :
            self.send_header('Content-Length', len(SERVICE_RESPONSE))
        self.end_headers()
        self.wfile.write(SERVICE_RESPONSE)







httpd = ServerClass(("", args.port), Handler)
logging.info("[*] Serving at port "+str(args.port))

httpd.serve_forever()
