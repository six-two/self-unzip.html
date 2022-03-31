//the code for unpacking a file. This file gets bundled/minified and converted to ./output/main.min.js
import {decompressSync, strFromU8} from 'fflate';

// Source: https://raw.githubusercontent.com/nE0sIghT/ascii85.js/master/ascii85.js
// ASCII85 a.k.a. Base85 implementation in JavaScript
// Copyright (C) 2018  Yuri Konotopov (Юрий Конотопов) <ykonotopov@gnome.org>
// MIT License

const LINE_WIDTH = 80;
const TUPLE_BITS = [24, 16, 8, 0];
const POW_85_4 = [
    85*85*85*85,
    85*85*85,
    85*85,
    85,
    1
];

function getByteArrayPart(tuple, bytes = 4)
{
    let output = new Uint8Array(bytes);

    for(let i = 0; i < bytes; i++)
    {
        output[i] = (tuple >> TUPLE_BITS[i]) & 0x00ff;
    }

    return output;
}

function toByteArray (text)
{
    function pushPart()
    {
        let part = getByteArrayPart(tuple, tupleIndex - 1);
        for(let j = 0; j < part.length; j++)
        {
            output.push(part[j]);
        }
        tuple = tupleIndex = 0;
    }

    let output = [];
    let stop = false;

    let tuple = 0;
    let tupleIndex = 0;

    let i = text.startsWith("<~") && text.length > 2 ? 2 : 0;
    do
    {
        // Skip whitespace
        if(text.charAt(i).trim().length === 0)
            continue;

        let charCode = text.charCodeAt(i);

        switch(charCode)
        {
            case 0x7a: // z
                if(tupleIndex != 0)
                {
                    console.error("Unexpected 'z' character at position " + i);
                }

                for(let j = 0; j < 4; j++)
                {
                    output.push(0x00);
                }
                break;
            case 0x7e: // ~
                let nextChar = '';
                let j = i + 1;
                while(j < text.length && nextChar.trim().length == 0)
                {
                    nextChar = text.charAt(j++);
                }

                if(nextChar != '>')
                {
                    console.error("Broken EOD at position " + j);
                }

                if(tupleIndex)
                {
                    tuple += POW_85_4[tupleIndex - 1];
                    pushPart();
                }

                stop = true;
                break;
            default:
                if(charCode < 0x21 || charCode > 0x75)
                {
                    console.error("Unexpected character with code " + charCode + " at position " + i);
                }

                tuple += (charCode - 0x21) * POW_85_4[tupleIndex++];
                if(tupleIndex >= 5)
                {
                    pushPart();
                }
        }
    }
    while(i++ < text.length && !stop)

    return new Uint8Array(output);
}


// My code
log = (name, value) => {
    console.log(name);
    console.debug(value);
}

decompress = (enc) => {
    log("input", enc)

    dec = toByteArray(enc);
    log("after ascii85", dec)

    dec = decompressSync(dec);
    log("after fflate", dec)

    // dec = strFromU8(dec);
    // log("output", dec)

    return dec;
}
