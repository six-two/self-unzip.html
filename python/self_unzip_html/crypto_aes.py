#!/usr/bin/env python3
# This is the python implementation of my modified aes4js.js.
# Anything encrypted with this code can be decrypted by the JavaScript version
# If you import this class, you should have installed pycryptodomex. It is not needed if you just use the .crypto.NullEncryptoer
import json
from hashlib import pbkdf2_hmac, sha256
from secrets import token_bytes
# pip install pycryptodomex
from Cryptodome.Cipher import AES
# local
from .crypto import BaseEncryptor, ALGORITHM_AES_GCM
from .minified_js import DECRYPT, DECRYPT_CACHE_PW


BITS_256 = 256//8

def deriveKey(password: bytes, iv: bytes):
    application_name = b"six-two/self-unzip.html"
    salt_pre_hash_bytes = password + application_name + iv
    salt = sha256(salt_pre_hash_bytes).digest()
    iteration_count = 1_000_000 + len(password) + iv[0]
    # print("[Debug] Salt:", salt.hex())
    # print(iteration_count)

    return pbkdf2_hmac("sha256", password, salt, iteration_count, BITS_256)


class AesEncryptor(BaseEncryptor):
    """
    This is the python implementation of my modified aes4js.js.
    Anything encrypted with this code can be decrypted by the JavaScript version
    """
    def __init__(self, password: bytes, password_hint: str, cache_password: bool) -> None:
        self.password = password
        self.iv_used = True # needed before rotate_iv call
        self.rotate_iv()

        escaped_hint_wrapped_in_quotes = json.dumps(password_hint)
        self.js_library_code = DECRYPT_CACHE_PW if cache_password else DECRYPT
        self.js_library_code = self.js_library_code.replace('"PW_PROMPT"', escaped_hint_wrapped_in_quotes)

    def get_algorithm(self) -> str:
        return ALGORITHM_AES_GCM

    def encrypt_with_reused_iv(self, cleartext: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=self.iv)
        ciphertext = cipher.encrypt(cleartext)
        tag = cipher.digest()

        return self.iv + ciphertext + tag

    def rotate_iv(self) -> None:
        # Since recalculating the key is compute expensive, we only do it if the key has actually been used before.
        # This way we can call 'rotate_iv' to flag a key for rotation without actually causing unnecessary calculations
        if self.iv_used:
            self.iv = token_bytes(12)
            self.key = deriveKey(self.password, self.iv)
            self.iv_used = False

    def get_js_library_code(self) -> str:
        return self.js_library_code

