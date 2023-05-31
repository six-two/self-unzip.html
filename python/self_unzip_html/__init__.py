#!/usr/bin/env python3
import argparse
import base64
import gzip
import os
import sys
from typing import Optional
# local
from .crypto import encrypt
from .minified_js import B85DECODE, DECRYPT, UNZIP

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "template.html")

JS_EVAL = "const og_text=new TextDecoder().decode(og_data);console.debug(`Evaluating code:\n${og_text}`);eval(og_text)"
JS_REPLACE = 'const og_text=new TextDecoder().decode(og_data);setTimeout(()=>{console.log("replacing");let n=document.open("text/html","replace");n.write(og_text);n.close()}, 50);' # since decryption is async we do not catch the onload event anymore
JS_DOWNLOAD = 'let b=new Blob([og_data],{type:"application/octet-stream"});let u=URL.createObjectURL(b);document.body.innerHTML=`<h1>Unpacked {{NAME}}</h1><a href="${u}" download="{{NAME}}">Click here to download</a>`'


def get_javascript(page_type: str, file_name: str):
    if page_type == "download":
        return JS_DOWNLOAD.replace("{{NAME}}", file_name)
    elif page_type == "eval":
        return JS_EVAL
    elif page_type == "replace":
        return JS_REPLACE
    else:
        raise Exception(f"Unknown page type: '{page_type}'")


def encode_bytes(file_bytes: bytes) -> str:
    file_bytes = gzip.compress(file_bytes)
    file_bytes = base64.a85encode(file_bytes, adobe=True)
    file_bytes = file_bytes.replace(b'"', b"v").replace(b"\\", b"w")
    return file_bytes.decode("utf-8")


def create_page(input_file: str, template_file: str, java_script: str, encryption_password: Optional[str]):
    try:
        with open(template_file, "r") as f:
            template = f.read()
    except:
        raise Exception(f"Failed to load template file '{template_file}'. Try specifying a different file with the --template option")

    with open(input_file, "rb") as f:
        file_contents = f.read()

    file_contents = gzip.compress(file_contents)
    library_code = UNZIP + B85DECODE
    if encryption_password:
        # Encrypt before compression
        file_contents = encrypt(encryption_password.encode(), file_contents)
        # print(file_contents.hex())
        template = template.replace("{{GLUE_CODE}}", "console.log('Encoded data',c_data);d_data=b85decode(c_data);console.log('Decode data',d_data);decryptLoop(d_data).then(decrypted => {console.log('Decrypted',decrypted);u_data=unzip(decrypted);console.log('Unzipped data', u_data);action(u_data)});")
        library_code += DECRYPT
    else:
        template = template.replace("{{GLUE_CODE}}", "console.log('Encoded data',c_data);d_data=b85decode(c_data);console.log('Decode data',d_data);u_data=unzip(d_data);console.log('Unzipped data', u_data);action(u_data);")

    file_contents = base64.a85encode(file_contents, adobe=True)
    file_contents = file_contents.replace(b'"', b"v").replace(b"\\", b"w")
    encoded_data = file_contents.decode("utf-8")

    template = template.replace("{{LIBRARY_CODE}}", library_code)
    template = template.replace("{{DATA}}", encoded_data)
    template = template.replace("{{PAYLOAD_CODE}}", java_script)
    return template


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="the file to encode")
    ap.add_argument("-o", "--output", help="the location to write the output to. If not specified stdout will be used instead")
    ap.add_argument("-t", "--type", default="replace", choices=["download", "eval", "replace"], help="the output type (default: replace)")
    ap.add_argument("--template", help="use this template file instead of the default one")
    ap.add_argument("-p", "--password", help="encrypt the compressed data using this password")
    args = ap.parse_args()

    template_file = args.template or DEFAULT_TEMPLATE_FILE
    file_name = os.path.basename(args.file)
    java_script = get_javascript(args.type, file_name)

    html_page = create_page(args.file, template_file, java_script, args.password)

    if args.output:
        with open(args.output, "w") as f:
            f.write(html_page)
    else:
        print(html_page)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
