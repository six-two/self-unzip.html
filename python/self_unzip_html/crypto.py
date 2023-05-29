#!/usr/bin/env python3
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES

from hashlib import pbkdf2_hmac, sha256

BITS_256 = 256//8

def deriveKey(plainText: str):
    # @TODO    	if(plainText.length < 10) plainText = plainText.repeat(12 - plainText.length);

    salt = sha256(f"349d{plainText}9d3458694307{len(plainText)}".encode()).digest() # @TODO: add IV too
    print("salt", salt.hex())

    key = pbkdf2_hmac("sha256", plainText.encode(), salt.hex().encode(), 1_000_000 + len(plainText), BITS_256)
    print("key", key.hex())
    return key


def encrypt(password, cleartext):
    key = deriveKey(password)
    cipher = AES.new(key, AES.MODE_GCM)  # Create a cipher object to encrypt data
    print("nonce", cipher.nonce.hex())  # Write out the nonce to the output file under the salt
    ciphertext = cipher.encrypt(cleartext.encode())
    print("ciphertext", ciphertext.hex())
    print("tag", cipher.digest().hex())

if __name__ == "__main__":
    password = "Summer2023!"
    text = "The quick brown fox jumps over the lazy dog"
    encrypt(password, text)