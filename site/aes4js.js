// Loosely based on https://github.com/rndme/aes4js/blob/master/aes4js.js, but modified to remove that DataUrl en-/decoding, simplified code for my use and converted to async. Also changed how the salt is generated (see https://github.com/rndme/aes4js/issues/3) and streamlined the key derivation a bit
// aes4js, by dandavis. MIT applies.

const str2bytes = string => new TextEncoder("utf-8").encode(string);


const bytes_to_hex = x => {
    return Array.from(new Uint8Array(x)).map(function (b) {
        return ('00' + b.toString(16)).slice(-2);
    }).join('');
}

async function deriveKey(password_str, iv_bytes) {
    const password_bytes = str2bytes(password_str);
    const application_name_bytes = str2bytes("six-two/self-unzip.html");
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

async function encryptBytes(password_str, cleartext_bytes) {
	const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveKey(password_str, iv);

    const encrypted = await window.crypto.subtle.encrypt({
        name: "AES-GCM",
        iv: iv,
        tagLength: 128,
    }, key, cleartext_bytes);

    return new Uint8Array([...iv, ...new Uint8Array(encrypted)]);
}

async function decryptBytes(password_str, payload_bytes) {
    const iv_bytes = payload_bytes.slice(0, 12);
    const ciphertext_bytes = payload_bytes.slice(12)
    const key = await deriveKey(password_str, iv_bytes);
    return await window.crypto.subtle.decrypt({
        name: "AES-GCM",
        iv: iv_bytes,
        tagLength: 128,
    }, key, ciphertext_bytes);
}
