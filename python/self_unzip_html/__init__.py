#!/usr/bin/env python3
import argparse
import base64
import gzip
import os
import sys
from typing import Optional
# local
from .crypto import encrypt

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "template.html")

JS_EVAL = "const og_text=new TextDecoder().decode(og_data);console.debug(`Evaluating code:\n${og_text}`);eval(og_text)"
JS_REPLACE = 'const og_text=new TextDecoder().decode(og_data);setTimeout(()=>{console.log("replacing");let n=document.open("text/html","replace");n.write(og_text);n.close()}, 50);' # since decryption is async we do not catch the onload event anymore
JS_DOWNLOAD = 'let b=new Blob([og_data],{type:"application/octet-stream"});let u=URL.createObjectURL(b);document.body.innerHTML=`<h1>Unpacked {{NAME}}</h1><a href="${u}" download="{{NAME}}">Click here to download</a>`'

CRYPTO_CODE = """// Based loosely on https://github.com/rndme/aes4js/blob/master/aes4js.js, MIT License, dandavis
const fns2b=a=>(new TextEncoder("utf-8")).encode(a);async function fndrv(a,b){a=fns2b(a);var c=fns2b("six-two/self-unzip.html");c=new Uint8Array([...a,...c,...b]);c=await crypto.subtle.digest("SHA-256",c);b=1E6+a.length+b[0];a=await window.crypto.subtle.importKey("raw",a,"PBKDF2",!1,["deriveBits","deriveKey"]);return await window.crypto.subtle.deriveKey({name:"PBKDF2",salt:c,iterations:b,hash:"SHA-256"},a,{name:"AES-GCM",length:256},!0,["encrypt","decrypt"])}
async function fndec(a,b){const c=b.slice(0,12);b=b.slice(12);a=await fndrv(a,c);return await window.crypto.subtle.decrypt({name:"AES-GCM",iv:c,tagLength:128},a,b)}
async function decryptLoop(a){if(!isSecureContext)throw alert("Decryption only possible in secure context. Please load via file://, https://, or from localhost."),Error("Insecure Context");let b;b=location.hash?location.hash.slice(1):prompt("Please enter the decryption password");try{return await fndec(b,a)}catch(c){alert(`"Decryption failed" with error: ${c}`),location.hash="",location.reload()}};
"""

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

    if encryption_password:
        # Encrypt before compression
        file_contents = encrypt(encryption_password.encode(), file_contents)
        # print(file_contents.hex())
        template = template.replace("{{GLUE_CODE}}", "decryptLoop(decompress(c_data)).then(action);")
        template = template.replace("{{CRYPTO_CODE}}", CRYPTO_CODE)
        java_script = "console.log('Decrypted', og_data);" + java_script # debugging, should I keep it?
    else:
        template = template.replace("{{GLUE_CODE}}", "action(decompress(c_data));")
        template = template.replace("{{CRYPTO_CODE}}", "")



    encoded_data = encode_bytes(file_contents)
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
