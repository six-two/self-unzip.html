from argparse import ArgumentParser
from typing import Any
# local
from ..static_js import JS_DOWNLOAD, JS_DOWNLOAD_SVG, JS_DRIVEBY_REDIRECT, JS_DRIVEBY_REDIRECT_SVG, JS_EVAL, JS_REPLACE, JS_SHOW_TEXT, JS_SHOW_TEXT_SVG
from ..util import OperationNotImplemented


def register_action_argument_parser(ap: ArgumentParser):
    payload_option_visual_group = ap.add_argument_group("action to perform with the payload")
    payload_option_mutex = payload_option_visual_group.add_mutually_exclusive_group(required=True)
    payload_option_mutex.add_argument("--download", nargs="?", metavar="FILE_NAME", const="", help="show a download link to download the payload as a file. If you specify an argument that is used as the name of the file to download")
    payload_option_mutex.add_argument("--eval", action="store_true", help="pass the payload to eval() to run it as JavaScript code")
    payload_option_mutex.add_argument("--replace", action="store_true", help="replace the page's content with the payload. Use this to compress HTML pages")
    payload_option_mutex.add_argument("--show-text", action="store_true", help="use this to show plain text. Unlike --replace this does not interpret HTML tags and does not change whitespace")
    payload_option_mutex.add_argument("--driveby-redirect", metavar="REDIRECT_URL", help="downlaod the payload as a file in the background and immediately redirect the user to another site. Useful for phishing")
    payload_option_mutex.add_argument("--custom", metavar="YOUR_JAVASCRIPT_CODE", help="run your own action. Provide a JavaScript snippet that uses the decoded payload, which is stored in the 'og_data' variable. Note that data is a byte array, so you likely want to use 'new TextDecoder().decode(og_data)' to convert it to Unicode")


def get_javascript(args: Any, file_name: str, is_svg: bool) -> str:
    if args.download != None:
        # If args.downlaod is empty, use the name of the input file, otherwise use the user provided value
        base_code = JS_DOWNLOAD_SVG if is_svg else JS_DOWNLOAD
        return base_code.replace("{{NAME}}", args.download or file_name)
    elif args.eval:
        return JS_EVAL
    elif args.replace:
        if is_svg:
            raise OperationNotImplemented("Setting the innerHTML of a svg.text always resulted in errors. Use --show-text or remove the --svg flag")
        else:
            return JS_REPLACE
    elif args.show_text:
        return JS_SHOW_TEXT_SVG if is_svg else JS_SHOW_TEXT
    elif args.driveby_redirect != None:
        base_code = JS_DRIVEBY_REDIRECT_SVG if is_svg else JS_DRIVEBY_REDIRECT
        return base_code.replace("{{REDIRECT_URL}}", args.driveby_redirect).replace("{{NAME}}", file_name)
    elif args.custom != None:
        return args.custom
    else:
        raise Exception("Bug: Should not happen, since one of the payload parameters is required")


