# self-unzip.html

## Installation

Install with npm:

```bash
npm install .
```

### Create the decompression JavaScript

First use rollup to only select the actually used code:

```bash
./node_modules/.bin/rollup -c rollup.config.js
```

This command should create `output/main.js`

The next step is optional.
If you want to skip it, just rename `main.min.js` to `main.js` in the `output` directory.
Otherwise minify the code (may require you to install an external minifier like closure-compiler).

```bash
closure-compiler output/main.js --js_output_file output/main.min.js
```
