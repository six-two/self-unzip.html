# self-unzip.html

## Installation

Just clone the repo and put the contents of the `site` directory somewhere in your web server directory.


## Deprecated information

This basically just explains, how I generated the obfuscated script in template.html.
In case you are paranoid, you can reproduce the steps.
Or if there is an important update to `fflate` or `ascii85`, I will have to run them again.

Install with npm:

```bash
npm install .
```

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
