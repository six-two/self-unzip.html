#!/usr/bin/env bash

# Switch to the script's directory
cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null

echo "[*] Install libraries & tools"
npm install .

python_escape() {
    # Escape single backslashes
    sed "s|\\\\|\\\\\\\\|g" "output/$1"
}

# # build output/main.js
# ./node_modules/.bin/rollup -c rollup.config.js
# # build the minified version
# closure-compiler output/main.js --js_output_file output/main.min.js

# build output/decrypt.min.js
echo "[*] Minifying decryption code"
closure-compiler decrypt.js --js_output_file output/decrypt.min.js

echo "[*] Minifying unzip code"
./node_modules/.bin/rollup -c rollup.config.js -i unzip
closure-compiler output/unzip.js --js_output_file output/unzip.min.js

echo "[*] Minifying base85 decoding code"
closure-compiler b85decode.js --js_output_file output/b85decode.min.js

echo "[*] Minifying base64 decoding code"
closure-compiler b64decode.js --js_output_file output/b64decode.min.js

echo "[*] Generating minified_js.py"
cat << EOF > ../python/self_unzip_html/minified_js.py
B85DECODE="""// https://github.com/nE0sIghT/ascii85.js, MIT License, Copyright (C) 2018  Yuri Konotopov (Юрий Конотопов) <ykonotopov@gnome.org>
$(python_escape b85decode.min.js)
"""
B64DECODE="""$(python_escape b64decode.min.js)
"""
DECRYPT="""// Based loosely on https://github.com/rndme/aes4js/blob/master/aes4js.js, MIT License, dandavis
$(python_escape decrypt.min.js)
"""
UNZIP="""// https://github.com/101arrowz/fflate, MIT License, Copyright (c) 2020 Arjun Barrett
$(python_escape unzip.min.js)
"""
EOF
