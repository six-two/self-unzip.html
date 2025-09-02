import sys

PRINT_INFO_MESSAGES = False

def print_info(message):
    # Since the output may be written to stdout, we write info messages to stderr.
    # This makes them visible to the user but not to the next program in the pipe
    if PRINT_INFO_MESSAGES:
        print(f"[*] {message}", file=sys.stderr)


class OperationNotImplemented(Exception):
    pass

