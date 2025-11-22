# self-unzip.html

This tool creates HTML smuggling pages, that can be used to transfer files normaly blocked by proxies (for example .exe files).
The tool has various ways of transfering files, allows to protect files with a password and supports both HTML and SVG output.

## Installation

### Last release

Install the latest stable version:

=== "pip"

    ```bash
    python3 -m pip install -U self-unzip-html[all]
    ```

=== "pipx"

    ```bash
    pipx install self-unzip-html[all]
    ```

=== "docker"

    ```bash
    docker pull ghcr.io/six-two/self-unzip-html
    ```

### Bleeding edge

You can install the development version (`main` branch), however it is sometimes broken and new features may be buggy and undocumented.

First clone the repository:
```bash
git clone https://github.com/six-two/self-unzip-html
cd self-unzip-html/
```

Make sure you have the latest changes:
```bash
git pull
```

Then install it with a tool of your choice:

=== "pip"

    ```bash
    python3 -m pip install .[all]
    ```

=== "pipx"

    ```bash
    pipx install .[all] --force
    ```

=== "docker"

    ```bash
    docker build -t ghcr.io/six-two/self-unzip-html .
    ```

