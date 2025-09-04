from argparse import ArgumentParser
import os
import sys
# local
from ..page_builder import PageBuilder, Compression, Encoding
from ..util import print_info

def register_output_argument_parser(ap: ArgumentParser):
    ap_output = ap.add_argument_group("output options")
    ap_output.add_argument("-o", "--output", help="the location to write the output to. If not specified stdout will be used instead")
    ap_output.add_argument("-O", "--open", action="store_true", help="if writing output to a file, try to immediately open the file in the default web browser afterwards")
    ap_output.add_argument("-c", "--compression", default="auto", choices=["auto", "none", "gzip"], help="how to compress the contents (default: auto)")
    ap_output.add_argument("-e", "--encoding", default="auto", choices=["auto", "base64", "ascii85", "hex"], help="how to encode the binary data  (default: auto). base64 may not work for large contents (>65kB) due to different browser limitations")
    ap_output.add_argument("--console-log", action="store_true", help="insert debug statements to see the output of the individual steps")


def read_input_file(args) -> tuple[bytes,str]:
    """
    Returns file contents and file name as a tuple
    """
    try:
        if args.file == "-":
            # Read the buffer to get data as binary
            return (sys.stdin.buffer.read(), "stdin.txt")
        else:
            file_name = os.path.basename(args.file)
            with open(args.file, "rb") as f:
                return (f.read(), file_name)
    except:
        print(f"[!] Failed to load input file '{args.file}'")
        exit(1)


def write_output_file(args, html_page: str) -> None:
    if args.output:
        with open(args.output, "w") as f:
            f.write(html_page)

        if args.open:
            url = f"file://{os.path.realpath(args.output)}"
            if args.password:
                url += f"#{args.password}"
            print_info(f"Opening {url} in webbrowser")
            import webbrowser
            webbrowser.open(url)
    else:
        print(html_page)
        if args.open:
            print_info("Ignoring -O/--open since the output is stdout")


def get_compression_list(args) -> list[Compression]:
    if args.compression == "auto":
        return [Compression.GZIP, Compression.NONE]
    else:
        return [Compression(x) for x in args.compression.lower().split(",")]


def get_encoding_list(args) -> list[Encoding]:
    if args.encoding == "auto":
        # Hex is never much shorter than base64 (both have short stagers), so for performance reasons we just always ignore it in favor of base64
        return [Encoding.BASE64, Encoding.ASCII85]
    else:
        return [Encoding(x) for x in args.encoding.lower().split(",")]

