from argparse import ArgumentParser
# local
from . import Subcommand
from ..template import get_svg_template, get_html_template, DEFAULT_HTML_TEMPLATE_PATH, DEFAULT_SVG_TEMPLATE_PATH


def register_template_argument_parser(ap: ArgumentParser, subcommand: Subcommand):
    ap_template = ap.add_argument_group("Template Settings")
    if subcommand in [Subcommand.SVG, Subcommand.SVG_ENCRYPTED, Subcommand.SERVE]:
        ap_template.add_argument("--svg", metavar="SVG_FILE_PATH", nargs="?", default=DEFAULT_SVG_TEMPLATE_PATH, help="use this SVG instead of a normal HTML page for the smuggling")
    if subcommand in [Subcommand.HTML, Subcommand.HTML_ENCRYPTED, Subcommand.SERVE]:
        ap_template.add_argument("--template", help="use this template file instead of the default one")
        ap_template.add_argument("--title", default="Self Extracting Page", help="set the title of the HTML page")
        initial_page_contents_mutex = ap_template.add_mutually_exclusive_group()
        initial_page_contents_mutex.add_argument("--html", metavar="HTML_STRING", help="the HTML to show when the page is first loaded or if the unpacking fails")
        initial_page_contents_mutex.add_argument("--html-file", metavar="FILE", help="like --html, but read the contents from the given file")


def is_svg(args) -> bool:
    return args.encoder in [Subcommand.SVG.value, Subcommand.SVG_ENCRYPTED.value]


def get_page_template(args) -> str:
    if is_svg(args):
        try:
            return get_svg_template(args.svg)
        except:
            raise Exception(f"Failed to load SVG file '{args.svg}'. Try specifying a different file with the --svg option")
    else:
        template_file = args.template or DEFAULT_HTML_TEMPLATE_PATH
        initial_page_contents = get_initial_page_contents(args)
        try:
            return get_html_template(template_file, args.title, initial_page_contents)
        except:
            raise Exception(f"Failed to load template file '{template_file}'. Try specifying a different file with the --template option")


def get_initial_page_contents(args) -> str:
    if args.html != None:
        return args.html
    elif args.html_file != None:
        try:
            with open(args.html_file, "r") as f:
                return f.read()
        except Exception as e:
            print(f"[!] Failed to read file '{args.html_file}' from argument --html-file: {e}")
            exit(1)
    else:
        # No argument give, use the default
        initial_page_contents = "<h1>Unpacking...</h1><p>If you can read this, the extraction probably did not work. Please disable plugins (such as NoScript), which may block this page from running the extraction JavaScript code.</p>"
        if args.console_log:
            return initial_page_contents + "<p>This page was built with debugging enabled, so you should be able to see the hexdumps of the intermediate steps in the browser's console (F12).</p>"
        else:
            return initial_page_contents + "<p>Tip: You can use the --console-log option when building the page to show hexdumps of the intermediate steps in the browser console. This may help with debugging.</p>"

