#!/usr/bin/env python3
import argparse
import base64
import gzip
import os
import sys
from typing import Optional
# local
from .crypto import encrypt, EfficientEncryptor
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


class PageBuilder:
    def __init__(self, input_file: str, template_file: str, js_payload: str, encryption_password: Optional[str]) -> None:
        try:
            with open(template_file, "r") as f:
                self.template = f.read()
        except:
            raise Exception(f"Failed to load template file '{template_file}'. Try specifying a different file with the --template option")

        try:
            with open(input_file, "rb") as f:
                self.input_data = f.read()
        except:
            raise Exception(f"Failed to load input file '{input_file}'")

        self.js_payload = js_payload
        self.encryptor = EfficientEncryptor(encryption_password.encode()) if encryption_password else None # since only one of the results should be used (we may need to encrypt multiple time if some parameters have the `auto` value)

    def build_page(self, compression: str, encoding: str) -> str:
        compression_list = ["none", "gzip"] if compression == "auto" else [compression]
        encoding_list = ["base64", "ascii85"] if encoding == "auto" else [encoding]
        variants = []

        for c in compression_list:
            for e in encoding_list:
                page = self.build_page_no_auto(c, e)
                print(f"[*] Testing combination: {c} & {e} => {len(page)} bytes")
                variants.append(page)

        # Return the shortest result
        return sorted(variants, key=lambda x: len(x))[0]

    def build_page_no_auto(self, compression: str, encoding: str) -> str:
        library_code = ""
        encoded_data = self.input_data

        if compression == "gzip":
            library_code += UNZIP
            encoded_data = gzip.compress(encoded_data)
        elif compression == "none":
            pass
        else:
            raise Exception(f"Unknown compression method '{compression}'")

        if self.encryptor:
            library_code += DECRYPT
            encoded_data = self.encryptor.encrypt_with_reused_iv(encoded_data)

        if encoding == "ascii85":
            library_code += B85DECODE
            decode_fn = "b85decode"
            encoded_data = base64.a85encode(encoded_data, adobe=True).replace(b'"', b"v").replace(b"\\", b"w")
        elif encoding == "base64":
            decode_fn = "atob"
            encoded_data = base64.b64encode(encoded_data)
            print("base64 is broken for now") # SEE https://developer.mozilla.org/en-US/docs/Glossary/Base64#solution_1_%E2%80%93_escaping_the_string_before_encoding_it
        else:
            raise Exception(f"Unknown encoding method '{compression}'")

        
        glue_code = ("console.log('Encoded data',c_data);" 
            + f"d_data={decode_fn}(c_data);console.log('Decode data',d_data);")
        if self.encryptor:
            if compression == "gzip":
               glue_code += "decryptLoop(d_data).then(decrypted => {console.log('Decrypted',decrypted);u_data=unzip(decrypted);console.log('Unzipped data', u_data);action(u_data)});"
            else:
               glue_code += "decryptLoop(d_data).then(decrypted => {console.log('Decrypted',decrypted);action(decrypted)});"
        else:
            if compression == "gzip":
                glue_code += "u_data=unzip(d_data);console.log('Unzipped data', u_data);action(u_data);"
            else:
                glue_code += "action(d_data);"


        return self.replace_in_template(library_code, glue_code, self.js_payload, encoded_data)

    def replace_in_template(self, library_code: str, glue_code: str, payload_code: str, encoded_data: bytes) -> str:
        return (self.template
                .replace("{{LIBRARY_CODE}}", library_code)
                .replace("{{GLUE_CODE}}", glue_code)
                .replace("{{PAYLOAD_CODE}}", payload_code)
                .replace("{{DATA}}", encoded_data.decode())
        )


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
    ap.add_argument("-c", "--compression", default="auto", choices=["none", "auto", "gzip"], help="how to compress the contents")
    ap.add_argument("-e", "--encoding", default="auto", choices=["auto", "base64", "ascii85"], help="how to encode the binary data")
    ap.add_argument("--template", help="use this template file instead of the default one")
    ap.add_argument("-p", "--password", help="encrypt the compressed data using this password")
    args = ap.parse_args()

    template_file = args.template or DEFAULT_TEMPLATE_FILE
    file_name = os.path.basename(args.file)
    java_script = get_javascript(args.type, file_name)

    page_builder = PageBuilder(args.file, template_file, java_script, args.password)
    html_page = page_builder.build_page(args.compression, args.encoding)

    if args.output:
        with open(args.output, "w") as f:
            f.write(html_page)
    else:
        print(html_page)

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
