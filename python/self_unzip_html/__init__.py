#!/usr/bin/env python3
import argparse
import os
import sys
# local
from .static_js import JS_DOWNLOAD, JS_DOWNLOAD_SVG, JS_DRIVEBY_REDIRECT, JS_DRIVEBY_REDIRECT_SVG, JS_EVAL, JS_REPLACE, JS_SHOW_TEXT, JS_SHOW_TEXT_SVG
from .util import print_info, PRINT_INFO_MESSAGES
from .page_builder import PageBuilder, Compression, Encoding
from .template import get_svg_template, get_html_template
from .crypto import NullEncryptor
from .cli.action import register_action_argument_parser, get_javascript
from .cli.encryption import register_encryption_argument_parser, get_encryptor

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_SVG_FILE = os.path.join(SCRIPT_DIR, "default.svg")
DEFAULT_TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "template.html")

class OperationNotImplemented(Exception):
    pass


def main_wrapped() -> None:
    # @TODO: Support multiple input files for certain options (download, driveby, etc)?
    ap = argparse.ArgumentParser(description="This tools can create self-decompressing HTML pages, that can be used to minify documents or circumvent web proxy download restrictions and filtering.")
    # ap_input = ap.add_argument_group("input options")
    # ap_input_mutex = ap_input.add_mutually_exclusive_group(required=True)
    ap.add_argument("file", help="the file to encode. Use '-' to read from standard input")
    # ap_input_mutex.add_argument("-F", "--file-list", help="a list of files to") # @TODO: If i add this, how will output options work?

    ap_output = ap.add_argument_group("output options")
    ap_output.add_argument("-o", "--output", help="the location to write the output to. If not specified stdout will be used instead")
    ap_output.add_argument("-O", "--open", action="store_true", help="if writing output to a file, try to immediately open the file in the default web browser afterwards")
    ap_output.add_argument("-q", "--quiet", action="store_true", help="minimize console output")

    register_action_argument_parser(ap)
    register_encryption_argument_parser(ap)

    ap_settings = ap.add_argument_group("settings")
    ap_settings.add_argument("-c", "--compression", default="auto", choices=["auto", "none", "gzip"], help="how to compress the contents (default: auto)")
    ap_settings.add_argument("-e", "--encoding", default="auto", choices=["auto", "base64", "ascii85", "hex"], help="how to encode the binary data  (default: auto). base64 may not work for large contents (>65kB) due to different browser limitations")
    ap_settings.add_argument("--console-log", action="store_true", help="insert debug statements to see the output of the individual steps")

    ap_template = ap.add_argument_group("template settings")
    ap_template_mutex = ap_template.add_mutually_exclusive_group()
    ap_template_mutex.add_argument("--svg", metavar="SVG_FILE_PATH", nargs="?", const=DEFAULT_SVG_FILE, help="use this SVG instead of a normal HTML page for the smuggling")
    ap_template_mutex.add_argument("--template", help="use this template file instead of the default one")
    ap_template.add_argument("--title", default="Self Extracting Page", help="set the title of the HTML page")
    initial_page_contents_mutex = ap_template.add_mutually_exclusive_group()
    initial_page_contents_mutex.add_argument("--html", metavar="HTML_STRING", help="the HTML to show when the page is first loaded or if the unpacking fails")
    initial_page_contents_mutex.add_argument("--html-file", metavar="FILE", help="like --html, but read the contents from the given file")
    ap_template.add_argument("--obscure-action", action="store_true", help="obscures the action JavaScript code")
    args = ap.parse_args()

    if not args.quiet:
        global PRINT_INFO_MESSAGES
        PRINT_INFO_MESSAGES = True

    if args.html != None:
        initial_page_contents = args.html
    elif args.html_file != None:
        try:
            with open(args.html_file, "r") as f:
                initial_page_contents = f.read()
        except Exception as e:
            print(f"[!] Failed to read file '{args.html_file}' from argument --html-file: {e}")
            exit(1)
    else:
        # No argument give, use the default
        initial_page_contents = "<h1>Unpacking...</h1><p>If you can read this, the extraction probably did not work. Please disable plugins (such as NoScript), which may block this page from running the extraction JavaScript code.</p>"
        if args.console_log:
            initial_page_contents += "<p>This page was built with debugging enabled, so you should be able to see the hexdumps of the intermediate steps in the browser's console (F12).</p>"
        else:
            initial_page_contents += "<p>Tip: You can use the --console-log option when building the page to show hexdumps of the intermediate steps in the browser console. This may help with debugging.</p>"


    template_file = args.template or DEFAULT_TEMPLATE_FILE
    file_name = os.path.basename(args.file)
    is_svg = args.svg != None

    if is_svg:
        try:
            template = get_svg_template(args.svg)
        except:
            raise Exception(f"Failed to load SVG file '{args.svg}'. Try specifying a different file with the --svg option")
    else:
        try:
            template = get_html_template(template_file, args.title, initial_page_contents)
        except:
            raise Exception(f"Failed to load template file '{template_file}'. Try specifying a different file with the --template option")

    try:
        if args.file == "-":
            # Read the buffer to get data as binary
            input_data = sys.stdin.buffer.read()
        else:
            with open(args.file, "rb") as f:
                input_data = f.read()
    except:
        print(f"[!] Failed to load input file '{args.file}'")
        exit(1)


    compression_list = [Compression.GZIP, Compression.NONE] if args.compression == "auto" else [Compression(args.compression)]
    # Hex is never much shorter than base64 (both have short stagers), so for performance reasons we just always ignore it in favor of base64
    encoding_list = [Encoding.BASE64, Encoding.ASCII85] if args.encoding == "auto" else [Encoding(args.encoding)]
    page_builder = PageBuilder(template,
                               get_javascript(args, file_name, is_svg),
                               get_encryptor(args),
                               obscure_action=args.obscure_action,
                               encode_library_as_base64=is_svg, insert_debug_statements=args.console_log, compression_list=compression_list,
                               encoding_list=encoding_list
                               )
    html_page = page_builder.build_page(input_data)

    if args.output:
        with open(args.output, "w") as f:
            f.write(html_page)

        if args.open:
            url = f"file://{os.path.realpath(args.output)}"
            if args.password:
                url += f"#{args.password}"
            print_info(f"Opening {url} in webbrowser")
            import webbrowser
            webbrowser.open(url)
    else:
        print(html_page)
        if args.open:
            print_info("Ignoring -O/--open since the output is stdout")

def main():
    try:
        main_wrapped()
    except OperationNotImplemented as e:
        print(f"[-] This operation is not implemented for this combination of flags. Reason: {e}")


if __name__ == "__main__":
    main()