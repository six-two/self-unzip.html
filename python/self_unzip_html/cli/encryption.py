from argparse import ArgumentParser
# local
from . import Subcommand
from ..crypto import BaseEncryptor, NullEncryptor

def register_encryption_argument_parser(ap: ArgumentParser, subcommand: Subcommand) -> None:
    if subcommand in [Subcommand.HTML_ENCRYPTED, Subcommand.SVG_ENCRYPTED]:
        # Only show encryption options when an encrypted subcommand is used
        ap_encryption = ap.add_argument_group("Encryption Options")
        ap_encryption.add_argument("-p", "--password", required=True, help="encrypt the compressed data using this password")
        ap_encryption.add_argument("-P", "--password-prompt", default="Please enter the decryption password", help="provide your custom password prompt, that can for example be used to provide a password hint")
        ap_encryption.add_argument("-C", "--cache-password", action="store_true", help="cache password to localStorage, so that you can reload the page without entering password again")
        ap_encryption.add_argument("--iterations", "-I", type=int, default=1_000_000, help="minimum number of iterations for the PBKDF2 key derivation function")
    

def get_encryptor(args) -> BaseEncryptor:
    if args.password:
        try:
            # Conditional import, since it is not always needed and loads an external library
            from ..crypto_aes import AesEncryptor
            return AesEncryptor(args.password.encode(), args.password_prompt, args.cache_password, pbkdf_iteration_count=args.iterations)
        except Exception as ex:
            print("[-]", ex)
            print("[*] Hint: Please make sure, that 'pycryptodomex' is installed. You can install it by running:")
            print("python3 -m pip install pycryptodomex")
            exit(1)
    else:
        return NullEncryptor()
