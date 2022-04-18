# self-unzip.html
[![PyPI version](https://img.shields.io/pypi/v/self-unzip-html)](https://pypi.org/project/self-unzip-html/)
![License](https://img.shields.io/pypi/l/self-unzip-html)
![Python versions](https://img.shields.io/pypi/pyversions/self-unzip-html)

This [repo](https://github.com/six-two/self-unzip.html) contains tools to create self-extracting HTML pages.
It works by taking a payload, compressing it, and encoding the results using ASCII85.
It then puts the resulting string in a template file, that contains the code to decode and decompress the payload again.

Currently there are three actions implemented, that can be executed, after the payload is decoded:

- Execute payload as JavaScript code (example usecase: obfuscate malicious JS code)
- Show payload as HTML page (example usecase: compress a big web page)
- Download the payload as a file (example usecase: bypass antivirus / filters)

## Demo

You can try the online demo at [self-extracting-html.six-two.dev](https://self-extracting-html.six-two.dev/).
This version is the same as the web version described below.
It is entirely client-site, your files do not get uploaded to a server.

## Installation

### Web version

There is a bare-bones page generator written in plain HTML and JavaScript.
To use it, just clone the repo and put the contents of the `site` directory somewhere in your web server directory.

### Python version

A Python script to generate self extracting web pages is under `python/main.py`.
It just requires a modern Python version (probably Python3.9+) and has no external dependencies.

You can also install it with `pip`:

```
python3 -m pip install self-unzip-html
```


## template.html

This basically just explains, how I generated the obfuscated script in `template.html`.
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
