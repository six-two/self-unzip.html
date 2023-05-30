#!/usr/bin/env bash

cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null

# Install cobraries & tools
npm install .

# build output/main.js
./node_modules/.bin/rollup -c rollup.config.js
# build the minified version
closure-compiler output/main.js --js_output_file output/main.min.js

# build output/decrypt.min.js
closure-compiler decrypt.js --js_output_file output/decrypt.min.js
