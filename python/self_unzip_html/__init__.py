#!/usr/bin/env python3
import argparse
import os
import sys
from typing import Any
# local
from .static_js import JS_DOWNLOAD, JS_DOWNLOAD_SVG, JS_DRIVEBY_REDIRECT, JS_DRIVEBY_REDIRECT_SVG, JS_EVAL, JS_REPLACE, JS_SHOW_TEXT, JS_SHOW_TEXT_SVG
from .util import print_info, PRINT_INFO_MESSAGES
from .page_builder import PageBuilder

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_SVG_FILE = os.path.join(SCRIPT_DIR, "default.svg")
DEFAULT_TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "template.html")

class OperationNotImplemented(Exception):
    pass

def get_javascript(args: Any, file_name: str, is_svg: bool) -> str:
    if args.download != None:
        # If args.downlaod is empty, use the name of the input file, otherwise use the user provided value
        base_code = JS_DOWNLOAD_SVG if is_svg else JS_DOWNLOAD
        return base_code.replace("{{NAME}}", args.download or file_name)
    elif args.eval:
        return JS_EVAL
    elif args.replace:
        if is_svg:
            raise OperationNotImplemented("Setting the innerHTML of a svg.text always resulted in errors. Use --show-text or remove the --svg flag")
        else:
            return JS_REPLACE
    elif args.show_text:
        return JS_SHOW_TEXT_SVG if is_svg else JS_SHOW_TEXT
    elif args.driveby_redirect != None:
        base_code = JS_DRIVEBY_REDIRECT_SVG if is_svg else JS_DRIVEBY_REDIRECT
        return base_code.replace("{{REDIRECT_URL}}", args.driveby_redirect).replace("{{NAME}}", file_name)
    elif args.custom != None:
        return args.custom
    else:
        raise Exception("Bug: Should not happen, since one of the payload parameters is required")


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

    payload_option_visual_group = ap.add_argument_group("action to perform with the payload")
    payload_option_mutex = payload_option_visual_group.add_mutually_exclusive_group(required=True)
    payload_option_mutex.add_argument("--download", nargs="?", metavar="FILE_NAME", const="", help="show a download link to download the payload as a file. If you specify an argument that is used as the name of the file to download")
    payload_option_mutex.add_argument("--eval", action="store_true", help="pass the payload to eval() to run it as JavaScript code")
    payload_option_mutex.add_argument("--replace", action="store_true", help="replace the page's content with the payload. Use this to compress HTML pages")
    payload_option_mutex.add_argument("--show-text", action="store_true", help="use this to show plain text. Unlike --replace this does not interpret HTML tags and does not change whitespace")
    payload_option_mutex.add_argument("--driveby-redirect", metavar="REDIRECT_URL", help="downlaod the payload as a file in the background and immediately redirect the user to another site. Useful for phishing")
    payload_option_mutex.add_argument("--custom", metavar="YOUR_JAVASCRIPT_CODE", help="run your own action. Provide a JavaScript snippet that uses the decoded payload, which is stored in the 'og_data' variable. Note that data is a byte array, so you likely want to use 'new TextDecoder().decode(og_data)' to convert it to Unicode")

    ap_settings = ap.add_argument_group("settings")
    ap_settings.add_argument("-c", "--compression", default="auto", choices=["auto", "none", "gzip"], help="how to compress the contents (default: auto)")
    ap_settings.add_argument("-e", "--encoding", default="auto", choices=["auto", "base64", "ascii85"], help="how to encode the binary data  (default: auto). base64 may not work for large contents (>65kB) due to different browser limitations")
    ap_settings.add_argument("-p", "--password", help="encrypt the compressed data using this password")
    ap_settings.add_argument("-P", "--password-prompt", default="Please enter the decryption password", help="provide your custom password prompt, that can for example be used to provide a password hint")
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

    if args.quiet:
        global PRINT_INFO_MESSAGES
        PRINT_INFO_MESSAGES = False

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
    java_script = get_javascript(args, file_name, is_svg)

    if is_svg:
        try:
            with open(args.svg, "r") as f:
                template = f.read()
        except:
            raise Exception(f"Failed to load SVG file '{args.svg}'. Try specifying a different file with the --svg option")

        template = template.replace("</svg>", """
    <script>
        {{LIBRARY_CODE}}
        // My code (c) six-two, MIT License
        const action = (og_data) => { {{PAYLOAD_CODE}} };
        const c_data = "{{DATA}}";
        {{GLUE_CODE}}
    </script>
</svg>
""")
    else:
        try:
            with open(template_file, "r") as f:
                template = f.read()
        except:
            raise Exception(f"Failed to load template file '{template_file}'. Try specifying a different file with the --template option")

        template = template.replace("{{TITLE}}", args.title)
        template = template.replace("{{HTML}}", initial_page_contents)


    page_builder = PageBuilder(args.file, template, java_script, args.password, args.password_prompt, args.obscure_action)
    html_page = page_builder.build_page(args.compression, args.encoding, args.console_log)

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