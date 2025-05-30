import os
from urllib.parse import unquote

from socketserver import TCPServer
from datetime import datetime
from http.server import SimpleHTTPRequestHandler
from requests import HTTPError
from Label import create_voucher, generate_label

# Define the port number to listen on
PORT = 8000


class RequestHandler(SimpleHTTPRequestHandler):
    # Override the do_GET() method to handle GET requests
    def do_POST(self):
        # Get the input and date values from the request body
        input_value = unquote(
            self.rfile.read(int(self.headers["Content-Length"])).decode()
        )
        room, date = map(lambda x: x.split("=")[1], input_value.split("&"))
        message = "Data submitted successfully!"
        try:
            unifi(room, datetime.strptime(date, "%m/%d/%Y"))
            self.send_response(200)
        except HTTPError as e:
            self.send_response(e.response.get("statusCode"))
            message = e.response.get("message")
        except ValueError as e:
            self.send_response(400)
            message = f"Invalid date provided: {date}"

        # Send a response to the client
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))

    def do_GET(self):
        # Get the requested path
        path = self.path

        # If the requested path is the root path, serve the index.html file
        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.copyfile(f, self.wfile)

        # Otherwise, serve the requested file
        else:
            super().do_GET()


def unifi(room, checkout):
    filename = generate_label(*create_voucher(room, checkout))
    return_code = os.system(f".venv/bin/brother_ql print -l 62red --red {filename}")
    if return_code:
        raise HTTPError(
            response={
                "statusCode": 500,
                "message": f"Failed to print label, error code {return_code}.",
            }
        )
    os.remove(filename)


if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Create a TCPServer instance and bind it to the specified port
    server = TCPServer(("", PORT), RequestHandler)

    # Start the server
    print(f"Server running on port {PORT}")
    try:
        server.serve_forever()
    except Exception:
        server.shutdown()
