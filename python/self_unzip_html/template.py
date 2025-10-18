import os

SCRIPT_TAG_TEMPLATE_FOR_SVG_FILES = """
    <script><![CDATA[
        {{LIBRARY_CODE}}
        // My code (c) six-two, MIT License
        const action = (og_data) => { {{PAYLOAD_CODE}} };
        const c_data = "{{DATA}}";
        {{GLUE_CODE}}
    ]]></script>
"""

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_SVG_TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "default.svg")
DEFAULT_HTML_TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "template.html")



def get_svg_template(template_path: str) -> str:
    with open(template_path, "r") as f:
        template = f.read()

    return template.replace("</svg>", SCRIPT_TAG_TEMPLATE_FOR_SVG_FILES + "</svg>")

def get_html_template(template_path: str, page_title: str, initial_page_contents: str):
    with open(template_path, "r") as f:
        template = f.read()

    template = template.replace("{{TITLE}}", page_title)
    template = template.replace("{{HTML}}", initial_page_contents)
    return template

