# Download Actions

Multiple different actions allow downloading the file, each with different pros and cons.

## Download Link

This action shows a download link, that will download the file when clicked.
The link allows you to use right-click -> `Save As...` to store the file in a custom directory, which may allow you to bypass scans / monitoring that only applies to your `~/Downloads` folder.

Example command:
```bash
self-unzip-html html --download-link -i PsExec.exe -o docs/demos/download_link.html
```

[Example output file](../demos/download_link.html)

## Automatic Download

This action will automatically downloads the file in addition to showing the download link.

!!! note "OPSEC"
    This behavior may be flagged by any security sandboxes checking the link, so you may want to protect the page with a password.


### With Password

Example command without password:
```bash
self-unzip-html encrypted-html --download-auto -i PsExec.exe -o docs/demos/download_auto_pw.html -p pw123!
```

[Example output file](../demos/download_auto_pw.html) with password `pw123!`.


### Without Password

Example command without password:
```bash
self-unzip-html html --download-auto -i PsExec.exe -o docs/demos/download_auto.html
```

[Example output file](../demos/download_auto.html)


## Driveby Download

The driveby download action will automatically download the file and redirect to a page specified by you.
This makes it look, as if the other page (which is legitimate) downloaded the file.
It is designed for phishing or other social engineering attacks, where you trick the victim into downloading and installing malicious software.

!!! note "OPSEC"
    This behavior may be flagged by any security sandboxes checking the link, so you may want to take one of these measures:

    - Have a harmless dummy page when emailing the link and then replace the link with the real payload after a couple minutes (after the URLs are scanned).
    - Have some anti bot measure in place that stops security sandboxes.
    - Maybe password protect the link, but send the password in the URL hash so that the page automatically decrypts itself? I'm not sure if this helps against decent sandboxes, since if they evaluate the URL with the hash they may decrypt the page too.


Example command:
```bash
self-unzip-html html --driveby-redirect='https://learn.microsoft.com/en-us/sysinternals/downloads/psexec' -i PsExec.exe -o docs/demos/download_driveby.html
```

[Example output file](../demos/download_driveby.html)

