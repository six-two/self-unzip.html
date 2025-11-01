// IMPORTANT NOTE: After compiling the code, replace the 'window.something' (usually it was 'window.g') with 'og_data'. Also remove the 'use strict' at the beginning.
// Basically just paste it into https://jscompressor.treblereel.dev/, select "Advanced", copy the output and post process it with the following (use xclip instead of pbpaste/pbcopy on linux):
// pbpaste | sed -e "s/.*'use strict';//" -e "s/window.g/og_data/" -e 's/[[:space:]]*$//' | pbcopy

async function uint8ToBase64Async(uint8Array) {
  const blob = new Blob([uint8Array]);
  const reader = new FileReader();

  return new Promise((resolve, reject) => {
    reader.onload = () => {
      // reader.result is a Data URL like: "data:application/octet-stream;base64,AAAA..."
      resolve(reader.result.split(',')[1]);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function handle_base64(base64) {
    let doc = document.open();
    doc.write(
        '<style>textarea {width: 100%;}</style>'
        + '<h1>{{NAME}}</h1>'
        + '<h2>Decode on Windows (PowerShell)</h2><textarea>[IO.File]::WriteAllBytes("{{WINDOWS_PATH}}", [Convert]::FromBase64String((Get-Clipboard)))</textarea>'
        + '<h2>Decode on Linux</h2><textarea>xclip --out --selection clipboard | base64 -d > {{LINUX_PATH}}</textarea>'
        + '<h2>Decode on macOS</h2><textarea>pbpaste | base64 -d > {{MAC_PATH}}</textarea>'
        + '<h2>Base64 to copy</h2><textarea id=base64 rows=20>' + base64 + '</textarea>'
    );
}

setTimeout(()=>uint8ToBase64Async(window.og_data).then(handle_base64), 50);
