// IMPORTANT NOTE: After compiling the code, replace the last value 'window.something' (passed to the function like '[...]})})(window.g);') with 'og_data'. Also remove the 'use strict' at the beginning.

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

function main(og_data) {
  // Create new page
  let doc = document.open();
  doc.write(
      '<style>textarea {width: 100%;}</style>'
      + '<h2>Copy button</h2><button>copy as base64</button>'
      + '<h2>Decode on Windows (PowerShell)</h2><textarea>[IO.File]::WriteAllBytes("decoded.png", [Convert]::FromBase64String((Get-Clipboard)))</textarea>'
      + '<h2>Decode on Linux</h2><textarea>xclip --out --selection clipboard | base64 -d > decoded.png</textarea>'
      + '<h2>Decode on macOS</h2><textarea>pbpaste | base64 -d > decoded.png</textarea>'
      + '<h2>Text for manual copy</h2><textarea id=base64 rows=20>Loading...</textarea>'
  );

  let setButtonText = (button, text) => {
      button.textContent = text;
      setTimeout(() => button.textContent="copy as base64", 2000);
  }

  uint8ToBase64Async(og_data).then((base64) => {
      let button = doc.querySelector("button");
      button.onclick=()=>{
        navigator.clipboard.writeText(base64)
          .then(()=>() => setButtonText(button, "copied"))
          .catch(e=>{console.error(e); setButtonText(button, "copy failed")})};
      doc.querySelector("#base64").value = base64;
  });
}

main(window.og_data);
