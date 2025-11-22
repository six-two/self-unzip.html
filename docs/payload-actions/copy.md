# Copy Actions

These actions copy a file's contents to the clipboard.

## Copy Text

This action just copies the contents of the file to your clipboard when you press the copy buttton.

Example command:

```bash
self-unzip-html html --copy-text -i PrivescCheck.ps1 -o docs/demos/copy_text.html
```

[Example output file](../demos/copy_text.html)


### Example: Powershell In-Memory Execution

If you can do an AMSI bypass in powershell, but some AV solution still monitors files that you write to the disk.
This makes it hard to download a tool like `Privesc-Check.ps1` to the disk, since the AV will scan it when you download or try to source it with powershell.
Instead you can use HTML smuggling to show a page that copies the contents of `Privesc-Check.ps1` into your clipboard.
Then you can just run `Get-Clipboard -Raw | iEx` and it have your tool imported.

## Copy Base64

This action converts the file to base64 and adds a copy buftton.
Additionally it shows decoding commands for macOS, Linux and Windows.

Example command:

```bash
self-unzip-html html --copy-base64 -i PsExec.exe -o docs/demos/copy_base64.html
```

[Example output file](../demos/copy_base64.html)


### Example: Bypass Download Restrictions in Some Remote Browsing Solutions

Some remote browsing solutions used in companies with high security posture will scan any browser downloads, even those done via HTML smuggling.
But some of them may not restrict clipboard access to the host system.
So you can copy your executable as a base64 encoded string and decode it using powershell to download your tools.

### Example: .NET In-Memory Execution

Similarly to the powershell in-memory execution, you could copy a .NET binary as base64 and then decode and execute it using powershell.

@TODO command?

