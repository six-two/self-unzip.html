// Based on https://github.com/rndme/aes4js/blob/master/aes4js.js, but modified to remove that DataUrl en-/decoding, simplified code for my use and converted to async

// aes4js, by dandavis. MIT applies.

console.log("start loading aes4js")

async function sha256(str) {
	const x = await crypto.subtle.digest("SHA-256", new TextEncoder("utf-8").encode(str));
    return bytes_to_hex(x);
}

const bytes_to_hex = x => {
    return Array.from(new Uint8Array(x)).map(function (b) {
        return ('00' + b.toString(16)).slice(-2);
    }).join('');
}

async function derive(plainText) { // key derivation using 1,000,000x pbkdf w/sha256
	if(plainText.length < 10) plainText = plainText.repeat(12 - plainText.length);
	const salt = await sha256("349d" + plainText + "9d3458694307" + plainText.length); // @TODO: add IV too
    console.debug("salt", salt);
    var passphraseKey = new TextEncoder().encode(plainText), saltBuffer = new TextEncoder().encode(salt);
    const key = await window.crypto.subtle.importKey('raw', passphraseKey, 'PBKDF2', false, ['deriveBits', 'deriveKey']);
    const encryption_key = await window.crypto.subtle.deriveKey({
        "name": 'PBKDF2',
        "salt": saltBuffer,
        "iterations": 1000000 + plainText.length,
        "hash": 'SHA-256'
    }, key, {
        "name": 'AES-GCM',
        "length": 256
    }, true, ["encrypt", "decrypt"]);

    // debugging
    crypto.subtle.exportKey("raw", encryption_key).then(raw_key => console.debug("encryption key: ", bytes_to_hex(raw_key)));

    return encryption_key;
}

async function encrypt(password, encodedString) {
	var iv = window.crypto.getRandomValues(new Uint8Array(12));

	try {
        const key = await derive(password);
        console.debug("key", key);
        const encrypted = await window.crypto.subtle.encrypt({
            name: "AES-GCM",
            iv: iv,
            tagLength: 128,
        }, key, encodedString);
        return {
            encrypted: encrypted,
            iv: [...iv], // iv
        };
    } catch (data) {
        return console.error(data);
    }
}

async function decrypt(password, iv, ciphertext) {
    try {
        const key = await derive(password);
        return await window.crypto.subtle.decrypt({
                name: "AES-GCM",
                iv: new Uint8Array(iv),
                tagLength: 128,
            }, key, ciphertext);
    } catch (e) {
        throw e;
    }
}

console.log("aes4js loaded")
