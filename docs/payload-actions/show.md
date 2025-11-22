# Show Contents

These actions display the contents of a file.

## Show Text

This action just shows the contents of the file as text:

Example command:

```bash
self-unzip-html html --show-text -i PrivescCheck.ps1 -o docs/demos/show_text.html
```

[Example output file](../demos/show_text.html)

## Show Base64

This action converts the file to base64 and shows the resulting base64 string.
Additionally, it shows decoding commands for macOS, Linux and Windows.

!!! note "Crashes for huge files"
    When you have files that are relatively large (say around 40MB+), this may sometimes crash and reload the page.
    I think this may happen, because the browser has trouble rendering such a huge textbox.
    If that happens, use the [copy base64](./copy.md) option instead, I did not notice that crashing.

Example command:

```bash
self-unzip-html html --show-base64 -i PsExec.exe -o docs/demos/show_base64.html
```

[Example output file](../demos/show_base64.html)


