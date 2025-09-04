import argparse
# local
from ..util import PRINT_INFO_MESSAGES, OperationNotImplemented
from ..page_builder import PageBuilder
from .action import register_action_argument_parser, get_javascript
from .encryption import register_encryption_argument_parser, get_encryptor
from .template import register_template_argument_parser, get_page_template, is_svg
from .output import register_output_argument_parser, read_input_file, write_output_file, get_compression_list, get_encoding_list


def main_wrapped() -> None:
    # @TODO: Support multiple input files for certain options (download, driveby, etc)?
    ap = argparse.ArgumentParser(description="This tool can create self-decompressing (and unencrypting) HTML pages, that can be used to minify documents or circumvent web proxy download restrictions and filtering.")
    # ap_input = ap.add_argument_group("input options")
    # ap_input_mutex = ap_input.add_mutually_exclusive_group(required=True)
    ap.add_argument("file", metavar="INPUT_FILE", help="the file to encode. Use '-' to read from standard input")
    # ap_input_mutex.add_argument("-F", "--file-list", help="a list of files to") # @TODO: If i add this, how will output options work?
    ap.add_argument("-q", "--quiet", action="store_true", help="minimize console output")

    register_action_argument_parser(ap)
    register_output_argument_parser(ap)
    register_encryption_argument_parser(ap)
    register_template_argument_parser(ap)

    args = ap.parse_args()

    if not args.quiet:
        global PRINT_INFO_MESSAGES
        PRINT_INFO_MESSAGES = True

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
