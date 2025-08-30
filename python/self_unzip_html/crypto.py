#!/usr/bin/env python3

ALGORITHM_NULL = "NULL"
ALGORITHM_AES_GCM = "AES_GCM"

class BaseEncryptor:
    """
    Base class for the null and AES crypto
    """

    def get_algorithm(self) -> str:
        raise Exception("Not implemented!")

    def rotate_iv(self) -> None:
        raise Exception("Not implemented!")
    
    def encrypt(self, cleartext: bytes) -> bytes:
        self.rotate_iv()
        return self.encrypt_with_reused_iv(cleartext)

    def encrypt_with_reused_iv(self, cleartext: bytes) -> bytes:
        raise Exception("Not implemented!")

    def get_js_library_code(self) -> str:
        raise Exception("Not implemented!")


class NullEncryptor(BaseEncryptor):
    """
    This is a implementation for when you do not want to encrypt the page
    """

    def get_algorithm(self) -> str:
        return ALGORITHM_NULL

    def rotate_iv(self) -> None:
        pass
    
    def encrypt(self, cleartext: bytes) -> bytes:
        return cleartext

    def encrypt_with_reused_iv(self, cleartext: bytes) -> bytes:
        return cleartext

    def get_js_library_code(self) -> str:
        return ""
