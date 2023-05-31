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
    const iv_bytes = payload_bytes.slice(0, 12);
    const ciphertext_bytes = payload_bytes.slice(12)
    const key = await fndrv(password_str, iv_bytes);
    const decrypted = await window.crypto.subtle.decrypt({
        name: "AES-GCM",
        iv: iv_bytes,
        tagLength: 128,
    }, key, ciphertext_bytes);
    return new Uint8Array(decrypted);
}

async function decryptLoop(data_bytes) {
    if (!isSecureContext) {
        alert("Decryption only possible in secure context. Please load via file://, https://, or from localhost.");
        throw new Error("Insecure Context");
    }

    let pw;
    if (location.hash) {
        pw = location.hash.slice(1); // remove leading #
    } else {
        pw = prompt("Please enter the decryption password");
    }
    try {
        return await fndec(pw, data_bytes);
    } catch (e) {
        alert(`"Decryption failed" with error: ${e}`);
        location.hash="";// delete the hash, since it was wrong
        if (!location.search.includes("noreload")){// use ?noreload in the URL for debugging
            location.reload();//this simplifies the code (no recursion, no loops, etc)
        }
    }
}
