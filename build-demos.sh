#!/usr/bin/env bash

# Switch to the script's directory
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null

set -e # exit on error

echo "[*] Installing python package"
python3 -m pip install .

# for docs/payload-actions/download.md
self-unzip-html html --download-link -i PsExec.exe -o docs/demos/download_link.html
self-unzip-html html --download-auto -i PsExec.exe -o docs/demos/download_auto.html
self-unzip-html encrypted-html --download-auto -i PsExec.exe -o docs/demos/download_auto_pw.html -p pw123!
self-unzip-html html --driveby-redirect='https://learn.microsoft.com/en-us/sysinternals/downloads/psexec' -i PsExec.exe -o docs/demos/download_driveby.html

# docs/payload-actions/copy.md
self-unzip-html html --copy-text -i PrivescCheck.ps1 -o docs/demos/copy_text.html
self-unzip-html html --copy-base64 -i PsExec.exe -o docs/demos/copy_base64.html

# docs/payload-actions/show.md
self-unzip-html html --show-text -i PrivescCheck.ps1 -o docs/demos/show_text.html
self-unzip-html html --show-base64 -i PsExec.exe -o docs/demos/show_base64.html

