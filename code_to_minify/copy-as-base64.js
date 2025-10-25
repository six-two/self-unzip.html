// IMPORTANT NOTE: After compiling the code, replace the 'window.something' (usually it was 'window.g') with 'og_data'. Also remove the 'use strict' at the beginning.

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
        + '<h1>{{NAME}}</h1><button>copy as base64</button>'
        + '<h2>Decode on Windows (PowerShell)</h2><textarea>[IO.File]::WriteAllBytes("{{NAME}}", [Convert]::FromBase64String((Get-Clipboard)))</textarea>'
        + '<h2>Decode on Linux</h2><textarea>xclip --out --selection clipboard | base64 -d > {{NAME}}</textarea>'
        + '<h2>Decode on macOS</h2><textarea>pbpaste | base64 -d > {{NAME}}</textarea>'
        + '<h2>Text for manual copy</h2><textarea id=base64 rows=20>Loading...</textarea>'
    );

    let setButtonText = (button, text) => {
        button.textContent = text;
        setTimeout(() => button.textContent="copy as base64", 2000);
    }

    let button = doc.querySelector("button");
    button.onclick = () => {
        navigator.clipboard.writeText(base64)
          .then(() => setButtonText(button, "copied"))
          .catch(e => {console.error(e); setButtonText(button, "copy failed")})
    };
    doc.querySelector("#base64").value = base64;
}

setTimeout(()=>uint8ToBase64Async(window.og_data).then(handle_base64), 50);
