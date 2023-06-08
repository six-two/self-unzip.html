#!/usr/bin/env bash

# Switch to the script's directory
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null

echo "[*] Building JavaScript code"
code_to_minify/build.sh

echo "[*] Installing python package"
python3 -m pip install .

echo "[*] Building test files: test_*.html"
# test each function / payload / encoding at least once (but not all combinations, that would be too many files)
# full auto decection
self-unzip-html.py README.md -o test_auto.html
self-unzip-html.py README.md -o test_auto_encrypted.html -p test
# simple encrypted
self-unzip-html.py README.md -o test_b64_encrypt.html -e base64 -c none -p test
# high efficiency (for large compressable files), encrypted
self-unzip-html.py README.md -o test_b85_gzip_encrypt.html -e ascii85 -c gzip -p test
# other modes
echo 'alert("Looks like it still works :)")' | self-unzip-html.py - -o test_eval_b64_gzip.html -e base64 -c gzip -t eval
self-unzip-html.py README.md -o test_download_b85_encrypt.html -e ascii85 -c none -p test -t download

echo -e "[*] Done.\nThe test files are in $(pwd)\nThe password for encrypted files is: test"
