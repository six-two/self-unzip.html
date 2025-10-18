import argparse
from enum import Enum

class Subcommand(Enum):
    SVG = "svg"
    HTML = "html"
    SVG_ENCRYPTED = "encrypted-svg"
    HTML_ENCRYPTED = "encrypted-html"

# local
from ..util import PRINT_INFO_MESSAGES, OperationNotImplemented
from ..page_builder import PageBuilder
from .action import register_action_argument_parser, get_javascript
from .encryption import register_encryption_argument_parser, get_encryptor
from .template import register_template_argument_parser, get_page_template, is_svg
from .output import register_output_argument_parser, read_input_file, write_output_file, get_compression_list, get_encoding_list
from .server import register_server_argument_parser, start_server


def main_wrapped() -> None:
    # @TODO: Support multiple input files for certain options (download, driveby, etc)?
    ap = argparse.ArgumentParser(description="This tool can create self-decompressing (and unencrypting) HTML pages, that can be used to minify documents or circumvent web proxy download restrictions and filtering.")

    subparsers = ap.add_subparsers(dest="encoder", required=True)
    for subcommand, description in [
        (Subcommand.HTML, "Create an unencrypted HTML smuggling page"),
        (Subcommand.HTML_ENCRYPTED, "Create an encrypted HTML smuggling page"),
        (Subcommand.SVG, "Create an unencrypted SVG with HTML smuggling code"),
        (Subcommand.SVG_ENCRYPTED, "Create an encrypted SVG with HTML smuggling code"),
    ]:
        ap_subcommand = subparsers.add_parser(subcommand.value, description=description, help=description)
        ap_subcommand.add_argument("-q", "--quiet", action="store_true", help="minimize console output")
        
        register_output_argument_parser(ap_subcommand, subcommand)
        register_action_argument_parser(ap_subcommand, subcommand)
        register_encryption_argument_parser(ap_subcommand, subcommand)
        register_template_argument_parser(ap_subcommand, subcommand)
    
    ap_serve = subparsers.add_parser("serve", description="start HTTP server", help="start HTTP server")
    ap_serve.add_argument("-q", "--quiet", action="store_true", help="minimize console output")
    register_server_argument_parser(ap_serve)

    args = ap.parse_args()

    if not args.quiet:
        global PRINT_INFO_MESSAGES
        PRINT_INFO_MESSAGES = True

    if args.encoder == "serve":
        main_serve(args)
    else:
        main_encode(args)

def main_serve(args):
    start_server(args.bind, args.port)

def main_encode(args):
    input_data, file_name = read_input_file(args)
    page_builder = PageBuilder(
        get_page_template(args),
        get_javascript(args, file_name, is_svg(args)),
        get_encryptor(args),
        obscure_action=args.obscure_action,
        encode_library_as_base64=is_svg(args),
        insert_debug_statements=args.console_log,
        compression_list=get_compression_list(args),
        encoding_list=get_encoding_list(args)
    )
    html_page = page_builder.build_page(input_data)
    write_output_file(args, html_page)




def main():
    try:
        main_wrapped()
    except OperationNotImplemented as e:
        print(f"[-] This operation is not implemented for this combination of flags. Reason: {e}")
