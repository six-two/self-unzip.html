const fns2b = string => new TextEncoder("utf-8").encode(string);

async function fndrv(password_str, iv_bytes) {
    const password_bytes = fns2b(password_str);
    const application_name_bytes = fns2b("six-two/self-unzip.html");
    const salt_pre_hash_bytes = new Uint8Array([...password_bytes, ...application_name_bytes, ...iv_bytes]);
    const salt = await crypto.subtle.digest("SHA-256", salt_pre_hash_bytes);
    // console.debug("Salt", bytes_to_hex(salt));
    const iteration_count = 1000000 + password_bytes.length + iv_bytes[0];

    const password_key = await window.crypto.subtle.importKey('raw', password_bytes, 'PBKDF2', false, ['deriveBits', 'deriveKey']);
    const derived_key = await window.crypto.subtle.deriveKey({
        "name": 'PBKDF2',
        "salt": salt,
        "iterations": iteration_count,
        "hash": 'SHA-256'
    }, password_key, {
        "name": 'AES-GCM',
        "length": 256
    }, true, ["encrypt", "decrypt"]);
    // crypto.subtle.exportKey("raw", derived_key).then(raw_key => console.debug("encryption key: ", bytes_to_hex(raw_key)));

    return derived_key;
}

async function fndec(password_str, payload_bytes) {
    console.log("Decrypting with password", password_str);
    const iv_bytes = payload_bytes.slice(0, 12);
    const ciphertext_bytes = payload_bytes.slice(12)
    const key = await fndrv(password_str, iv_bytes);
    const decrypted = await window.crypto.subtle.decrypt({
        name: "AES-GCM",
        iv: iv_bytes,
        tagLength: 128,
    }, key, ciphertext_bytes);
    // Cache the key (not the password), so that we do not need to derive it on page reload / page change again
    localStorage.setItem("self_unzip_pw", password_str);
    return new Uint8Array(decrypted);
}

async function decryptLoop(data_bytes) {
    if (!isSecureContext) {
        alert("Decryption only possible in secure context. Please load via file://, https://, or from localhost.");
        throw new Error("Insecure Context");
    }

    // The URL hash is the sipmlest way to make automatically decrypting links 
    const urlHash = (location.hash || "#").slice(1); // remove leading #
    // But we can also use the "self_unzip_pw" value from localStorage, which can help decrypting multiple pages on the same server
    const pwFromLocalStorage = localStorage.getItem("self_unzip_pw");
    // Both of these options do not expose the password to the server
    for (const pw of [urlHash, pwFromLocalStorage]) {
        if (pw) {
            try {
                return await fndec(pw, data_bytes);
            } catch (e) {
                console.log(`Automatic decryption using password "${pw}" from URL or cookie failed`);
            }
        }
    }

    while (true) {
        const pw = prompt("PW_PROMPT");
        try {
            return await fndec(pw, data_bytes);
        } catch (e) {
            alert(`"Decryption failed" with error: ${e}`);
        }
    }
}
