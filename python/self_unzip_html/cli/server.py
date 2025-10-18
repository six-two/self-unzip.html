#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import posixpath
from urllib.parse import unquote
from http.server import HTTPServer, BaseHTTPRequestHandler
# local
from . import Subcommand
from .template import get_initial_page_contents
from .encryption import get_encryptor
from .output import get_compression_list, get_encoding_list
from ..template import get_html_template, get_svg_template, DEFAULT_HTML_TEMPLATE_PATH
from ..page_builder import PageBuilder
from ..static_js import JS_DOWNLOAD, JS_DOWNLOAD_SVG


def register_server_argument_parser(ap: ArgumentParser, subcommand: Subcommand):
    if subcommand == Subcommand.SERVE:
        ap_server = ap.add_argument_group("Server options")
        ap_server.add_argument("-b", "--bind", default="0.0.0.0", help="IP address to bind to (default: 0.0.0.0)")
        ap_server.add_argument("port", nargs="?", type=int, default=8000, help="port to bind to (default: 8000)")

class HTMLSmugglingServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, args):
        super().__init__(server_address, RequestHandlerClass)

        try:
            self.svg_template = get_svg_template(args.svg)
        except:
            raise Exception(f"Failed to load SVG file '{args.svg}'. Try specifying a different file with the --svg option")

        template_file = args.template or DEFAULT_HTML_TEMPLATE_PATH
        initial_page_contents = get_initial_page_contents(args)
        try:
            self.html_template = get_html_template(template_file, args.title, initial_page_contents)
        except:
            raise Exception(f"Failed to load template file '{template_file}'. Try specifying a different file with the --template option")

        self.compression_list = get_compression_list(args)
        self.encoding_list = get_encoding_list(args)
        self.obscure_action = args.obscure_action
        self.insert_debug_statements = args.console_log

        self.encryptor = get_encryptor(args)

        # self.html_template = get_html_template(DEFAULT_TEMPLATE_FILE, "File Download", "File download link should be shown immediately")
        # self.svg_template = get_svg_template(DEFAULT_SVG_FILE)
        # self.encryptor = NullEncryptor()


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

        file_contents = self.build_page(file_name, file_contents, self.server.html_template, JS_DOWNLOAD, False)

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(file_contents)

    def serve_svg(self, path):
        file_name = os.path.basename(path)
        with open(path, "rb") as f:
            file_contents = f.read()

        file_contents = self.build_page(file_name, file_contents, self.server.svg_template, JS_DOWNLOAD_SVG, True)

        self.send_response(200)
        self.send_header("Content-type", "image/svg+xml")
        self.end_headers()
        self.wfile.write(file_contents)

    def build_page(self, file_name: str, file_contents: bytes, template: str, js_payload: str, is_svg: bool) -> bytes:
        html_page_builder = PageBuilder(
            template,
            js_payload.replace("{{NAME}}", file_name),
            self.server.encryptor,
            obscure_action=self.server.obscure_action,
            encode_library_as_base64=False,
            insert_debug_statements=self.server.insert_debug_statements,
            compression_list = self.server.compression_list,
            encoding_list = self.server.encoding_list,
        )
        html_str = html_page_builder.build_page(file_contents)
        return html_str.encode()

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


def start_server(bind_ip: str, bind_port: int, args):
    try:
        server_address = (bind_ip, bind_port)
        httpd = HTMLSmugglingServer(server_address, HTMLSmugglingRequestHandler, args)
        print(f"Serving at http://{bind_ip}:{bind_port}")
        httpd.serve_forever()
    except KeyboardInterrupt:
        # Allow Ctrl-C without traceback
        pass
