#!/usr/bin/env python3
import argparse
import base64
import gzip
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.join(SCRIPT_DIR, "..")
TEMPLATE_FILE = os.path.join(REPO_ROOT, "site", "template.html")

JS_EVAL = "const og_text=new TextDecoder().decode(og_data);console.debug(`Evaluating code:\n${og_text}`);eval(og_text)"
JS_REPLACE = 'const og_text=new TextDecoder().decode(og_data);window.onload=()=>{let n=document.open("text/html","replace");n.write(og_text);n.close()}'
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


def create_page(input_file: str, java_script: str):
    with open(TEMPLATE_FILE, "r") as f:
        template = f.read()

    with open(input_file, "rb") as f:
        file_contents = f.read()

    encoded_data = encode_bytes(file_contents)
    template = template.replace("{{DATA}}", encoded_data)
    template = template.replace("{{CODE}}", java_script)
    return template


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="the file to encode")
    ap.add_argument("-o", "--output", nargs="?", help="the location to write the output to. If not specified stdout will be used instead")
    ap.add_argument("-t", "--type", nargs="?", default="replace", choices=["download", "eval", "replace"], help="the output type")
    args = ap.parse_args()

    file_name = os.path.basename(args.file)
    java_script = get_javascript(args.type, file_name)
    html_page = create_page(args.file, java_script)

    if args.output:
        with open(args.output, "w") as f:
            f.write(html_page)
    else:
        print(html_page)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
