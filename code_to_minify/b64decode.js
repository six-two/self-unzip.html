// atob only properly handles ASCII output. Since we might store binary files (images, encrypted/compressed data), this is not enough.
// While some escaping may work, that is suboptimal (harder to implement in Python and bloats the encoded size).
// So I (mis)use some other APIs to decode the data to arbitrary binary data

// This API may not work well across browsers, due to differing length limitations:
// https://developer.mozilla.org/en-US/docs/web/http/basics_of_http/data_urls

//     Browsers are not required to support any particular maximum length of data. For example, the Opera 11 browser limited URLs to 65535 characters long which limits data URLs to 65529 characters (65529 characters being the length of the encoded data, not the source, if you use the plain data:, without specifying a MIME type). Firefox version 97 and newer supports data URLs of up to 32MB (before 97 the limit was close to 256MB). Chromium objects to URLs over 512MB, and Webkit (Safari) to URLs over 2048MB.


async function decodeAsync(base64) {
    fake_response = await fetch("data:;base64," + base64);
    blob = await fake_response.blob();
    buffer = await blob.arrayBuffer();
    return new Uint8Array(buffer);
}
