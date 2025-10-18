#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import posixpath
from urllib.parse import unquote
from http.server import HTTPServer, BaseHTTPRequestHandler
# local
from ..template import get_html_template, get_svg_template
from ..crypto import NullEncryptor
from ..page_builder import PageBuilder, Compression, Encoding, DEFAULT_TEMPLATE_FILE, DEFAULT_SVG_FILE
from ..static_js import JS_DOWNLOAD, JS_DOWNLOAD_SVG


def register_server_argument_parser(ap: ArgumentParser):
    ap.add_argument("-b", "--bind", default="0.0.0.0", help="IP address to bind to (default: 0.0.0.0)")
    ap.add_argument("-p", "--port", type=int, default=8000, help="port to bind to (default: 8000)")

class HTMLSmugglingServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.html_template = get_html_template(DEFAULT_TEMPLATE_FILE, "File Download", "File download link should be shown immediately")
        self.svg_template = get_svg_template(DEFAULT_SVG_FILE)
        self.encryptor = NullEncryptor()


class HTMLSmugglingRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server: HTMLSmugglingServer) -> None:
        super().__init__(request, client_address, server)

    def do_GET(self):
        # Translate the path to a local filesystem path
        path = self.translate_path(self.path)

        if os.path.isdir(path):
            self.list_directory(path)
        elif os.path.isfile(path):
            if self.path.endswith("?html"):
                self.serve_html(path)
            elif self.path.endswith("?svg"):
                self.serve_svg(path)
            else:
                self.serve_plain(path)
        else:
            self.send_error(404, "File not found")

    def serve_plain(self, path):
        file_name = os.path.basename(path)
        with open(path, "rb") as f:
            file_contents = f.read()

        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.send_header("Content-Disposition", f'attachment; filename="{file_name}"')
        self.end_headers()
        self.wfile.write(file_contents)

    def serve_html(self, path):
        file_name = os.path.basename(path)
        with open(path, "rb") as f:
            file_contents = f.read()

        html_page_builder = PageBuilder(
            self.server.html_template,
            JS_DOWNLOAD.replace("{{NAME}}", file_name),
            self.server.encryptor,
            compression_list = [Compression.NONE],
            encoding_list = [Encoding.BASE64],
        )
        html_str = html_page_builder.build_page(file_contents)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_str.encode())

    def serve_svg(self, path):
        file_name = os.path.basename(path)
        with open(path, "rb") as f:
            file_contents = f.read()

        html_page_builder = PageBuilder(
            self.server.svg_template,
            JS_DOWNLOAD_SVG.replace("{{NAME}}", file_name),
            self.server.encryptor,
            compression_list = [Compression.NONE],
            encoding_list = [Encoding.BASE64],
        )
        html_str = html_page_builder.build_page(file_contents)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html_str.encode())

    def list_directory(self, path):
        try:
            entries = os.listdir(path)
        except OSError:
            self.send_error(403, "Cannot list directory")
            return

        entries.sort()
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        displaypath = unquote(self.path)
        self.wfile.write(f"<!DOCTYPE html><html><head><title>Directory listing for {displaypath}</title></head>".encode())
        self.wfile.write(f"<body><h2>Directory listing for {displaypath}</h2><ul>".encode())

        for name in entries:
            fullname = os.path.join(path, name)
            href = posixpath.join(self.path, name)
            if os.path.isdir(fullname):
                self.wfile.write(f'<li><a href="{href}">{name}/</a></li>'.encode())
            else:
                # Show direct, HTML and SVG links
                self.wfile.write(f'<li><a href="{href}">{name}</a> (<a href="{href}?html">HTML</a>, <a href="{href}?svg">SVG</a>)</li>'.encode())

        self.wfile.write(b"</ul></body></html>")

    def translate_path(self, path):
        # Remove query parameters and decode URL
        path = unquote(path.split('?',1)[0].split('#',1)[0])
        path = os.path.normpath(path)
        words = path.strip('/').split('/')
        base_path = os.getcwd()
        for word in words:
            if word in ('.', '..'): # Is this how ChatGPT thinks path traversal is prevented? @TODO: check
                continue
            base_path = os.path.join(base_path, word)
        return base_path


def start_server(bind_ip: str, bind_port: int):
    try:
        server_address = (bind_ip, bind_port)
        httpd = HTMLSmugglingServer(server_address, HTMLSmugglingRequestHandler)
        print(f"Serving at http://{bind_ip}:{bind_port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        # Allow Ctrl-C without traceback
        pass
