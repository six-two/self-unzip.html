#!/usr/bin/env python3
# This is the python implementation of my modified aes4js.js.
# Anything encrypted with this code can be decrypted by the JavaScript version
from secrets import token_bytes
from hashlib import pbkdf2_hmac, sha256
# pip install pycryptodomex
from Cryptodome.Cipher import AES


BITS_256 = 256//8

def deriveKey(password: bytes, iv: bytes):
    application_name = b"six-two/self-unzip.html"
    salt_pre_hash_bytes = password + application_name + iv
    salt = sha256(salt_pre_hash_bytes).digest()
    iteration_count = 1_000_000 + len(password) + iv[0]
    # print("[Debug] Salt:", salt.hex())
    # print(iteration_count)

    return pbkdf2_hmac("sha256", password, salt, iteration_count, BITS_256)


def encrypt(password: bytes, cleartext: bytes) -> bytes:
    iv = token_bytes(12)
    key = deriveKey(password, iv)
    # print("[Debug] Key:", key.hex())
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext = cipher.encrypt(cleartext)
    tag = cipher.digest()

    return iv + ciphertext + tag


class EfficientEncryptor:
    """
    Precomputes the key, so that it does not need to be computed multiple times.
    DO ONLY USE ONE OF THE OUTPUTS, since the IV IS REUSED.
    """
    def __init__(self, password: bytes) -> None:
        self.password = password
        self.iv = token_bytes(12)
        self.key = deriveKey(password, self.iv)

    def encrypt_with_reused_iv(self, cleartext: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=self.iv)
        ciphertext = cipher.encrypt(cleartext)
        tag = cipher.digest()

        return self.iv + ciphertext + tag


if __name__ == "__main__":
    password = b"Summer2023!"
    text = b"The quick brown fox jumps over the lazy dog"
    ciphertext = encrypt(password, text)
    print(ciphertext.hex())
