#!/usr/bin/env bash

# Switch to the script's directory
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null

set -e # exit on error

# echo "[*] Building JavaScript code"
# code_to_minify/build.sh

echo "[*] Installing python package"
python3 -m pip install .

echo "[*] Building test files: test_*.html"
# test each function / payload / encoding at least once (but not all combinations, that would be too many files)
# full auto decection
self-unzip-html html -i README.md -o test_auto.html --replace

# SVG
self-unzip-html svg -i README.md -o test_auto.svg --show-text

# Encrypted SVG
self-unzip-html encrypted-svg -i README.md -o test_auto_encrypted.svg --show-text -p test

# test debugging outputs
self-unzip-html encrypted-html -i README.md -o test_debug.html -c gzip -p test --replace --console-log --obscure-action

# Test decoy page styling and code obfuscation
self-unzip-html html -i README.md -o test_decoy_content.html --title "Custom Title" --html '<h1>Custom content</h1>Your decoded payload is printed to the console.<br><img src="https://i1.sndcdn.com/artworks-SvzDuFfyt3AJ9fO1-iQrV9Q-t500x500.jpg">' --obscure-action --custom 'console.log(new TextDecoder().decode(og_data))'

# simple encrypted
self-unzip-html encrypted-html -i README.md -o test_auto_encrypted.html -p test --replace
self-unzip-html encrypted-html -i README.md -o test_b64_encrypt.html -e base64 -c none -p test --replace
# high efficiency (for large compressable files), encrypted
self-unzip-html encrypted-html -i README.md -o test_b85_gzip_encrypt.html -e ascii85 -c gzip -p test --replace
# other modes
echo 'alert("Looks like it still works :)")' | self-unzip-html html -i - -o test_eval_b64_gzip.html -e base64 -c gzip --eval
self-unzip-html encrypted-html -i README.md -o test_download_b85_encrypt.html -e ascii85 -c none -p test --download
self-unzip-html html -i README.md -e base64 -c none --show-text -o test_show.html
self-unzip-html encrypted-html -i README.md -o test_custom.html -e ascii85 -c none -p test --custom 'alert(og_data)'
# Usually you want to redirect to a thank you page, since this legitimizes the downlod you just started
self-unzip-html encrypted-html -i README.md -o test_driveby.html -e ascii85 -c none -p test --driveby-redirect https://anydesk.com/en/downloads/guide/thank-you

echo -e "[*] Done.\nThe test files are in $(pwd)\nThe password for encrypted files is: test"
