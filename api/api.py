import logging

from http.server import BaseHTTPRequestHandler

logger = logging.getLogger('api')
# HTTPRequestHandler class
class ApiRequestHandler(BaseHTTPRequestHandler):

  # GET
  def do_GET(self):
    # Send response status code
    self.send_response(200)

    # Send headers
    self.send_header('Content-type','text/html')
    self.end_headers()
    value = self.scale.read();

    # Send message back to client
    message = "Vekta viser: {0} gram".format(value)
    # Write content as utf-8 data
    self.wfile.write(bytes(message, "utf8"))
    return
