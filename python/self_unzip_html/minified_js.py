B85DECODE="""// https://github.com/nE0sIghT/ascii85.js, MIT License, Copyright (C) 2018  Yuri Konotopov (Юрий Конотопов) <ykonotopov@gnome.org>
const LINE_WIDTH=80,TUPLE_BITS=[24,16,8,0],POW_85_4=[52200625,614125,7225,85,1];function getByteArrayPart(b,g=4){let e=new Uint8Array(g);for(let c=0;c<g;c++)e[c]=b>>TUPLE_BITS[c]&255;return e}
function toByteArray(b){function g(){let l=getByteArrayPart(h,d-1);for(let k=0;k<l.length;k++)e.push(l[k]);h=d=0}let e=[];var c=!1;let h=0,d=0,f=b.startsWith("<~")&&2<b.length?2:0;do if(0!==b.charAt(f).trim().length){var a=b.charCodeAt(f);switch(a){case 122:0!=d&&console.error("Unexpected 'z' character at position "+f);for(a=0;4>a;a++)e.push(0);break;case 126:c="";for(a=f+1;a<b.length&&0==c.trim().length;)c=b.charAt(a++);">"!=c&&console.error("Broken EOD at position "+a);d&&(h+=POW_85_4[d-1],g());
c=!0;break;default:(33>a||117<a)&&console.error("Unexpected character with code "+a+" at position "+f),h+=(a-33)*POW_85_4[d++],5<=d&&g()}}while(f++<b.length&&!c);return new Uint8Array(e)}const decode=b=>toByteArray(b.replaceAll("v",'"').replaceAll("w","\\\\"));
"""
B64DECODE="""async function decodeAsync(a){fake_response=await fetch("data:;base64,"+a);blob=await fake_response.blob();buffer=await blob.arrayBuffer();return new Uint8Array(buffer)};
"""
DECRYPT="""// Based loosely on https://github.com/rndme/aes4js/blob/master/aes4js.js, MIT License, dandavis
const fns2b=a=>(new TextEncoder("utf-8")).encode(a);async function fndrv(a,b){a=fns2b(a);var c=fns2b("six-two/self-unzip.html");c=new Uint8Array([...a,...c,...b]);c=await crypto.subtle.digest("SHA-256",c);b=1E6+a.length+b[0];a=await window.crypto.subtle.importKey("raw",a,"PBKDF2",!1,["deriveBits","deriveKey"]);return await window.crypto.subtle.deriveKey({name:"PBKDF2",salt:c,iterations:b,hash:"SHA-256"},a,{name:"AES-GCM",length:256},!0,["encrypt","decrypt"])}
async function fndec(a,b){var c=b.slice(0,12);b=b.slice(12);a=await fndrv(a,c);c=await window.crypto.subtle.decrypt({name:"AES-GCM",iv:c,tagLength:128},a,b);return new Uint8Array(c)}
async function decryptLoop(a){if(!isSecureContext)throw alert("Decryption only possible in secure context. Please load via file://, https://, or from localhost."),Error("Insecure Context");let b;b=location.hash?location.hash.slice(1):prompt("Please enter the decryption password");try{return await fndec(b,a)}catch(c){alert(`"Decryption failed" with error: ${c}`),location.hash="",location.search.includes("noreload")||location.reload()}};
"""
UNZIP="""// https://github.com/101arrowz/fflate, MIT License, Copyright (c) 2020 Arjun Barrett
(function(){var n=Uint8Array,B=Uint16Array,L=Uint32Array,M=new n([0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0,0,0,0]),N=new n([0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13,0,0]),R=new n([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]),h=function(a,b){for(var c=new B(31),g=0;31>g;++g)c[g]=b+=1<<a[g-1];a=new L(c[30]);for(g=1;30>g;++g)for(b=c[g];b<c[g+1];++b)a[b]=b-c[g]<<5|g;return[c,a]},l=h(M,2),O=l[0];l=l[1];O[28]=258;l[258]=28;var S=h(N,0)[0],F=new B(32768);for(h=
0;32768>h;++h)l=(h&43690)>>>1|(h&21845)<<1,l=(l&52428)>>>2|(l&13107)<<2,l=(l&61680)>>>4|(l&3855)<<4,F[h]=((l&65280)>>>8|(l&255)<<8)>>>1;var D=function(a,b,c){for(var g=a.length,f=0,q=new B(b);f<g;++f)a[f]&&++q[a[f]-1];var z=new B(b);for(f=0;f<b;++f)z[f]=z[f-1]+q[f-1]<<1;if(c)for(c=new B(1<<b),q=15-b,f=0;f<g;++f){if(a[f]){var C=f<<4|a[f],d=b-a[f],k=z[a[f]-1]++<<d;for(d=k|(1<<d)-1;k<=d;++k)c[F[k]>>>q]=C}}else for(c=new B(g),f=0;f<g;++f)a[f]&&(c[f]=F[z[a[f]-1]++]>>>15-a[f]);return c};l=new n(288);for(h=
0;144>h;++h)l[h]=8;for(h=144;256>h;++h)l[h]=9;for(h=256;280>h;++h)l[h]=7;for(h=280;288>h;++h)l[h]=8;var P=new n(32);for(h=0;32>h;++h)P[h]=5;var T=D(l,9,1),U=D(P,5,1),G=function(a){for(var b=a[0],c=1;c<a.length;++c)a[c]>b&&(b=a[c]);return b},t=function(a,b,c){var g=b/8|0;return(a[g]|a[g+1]<<8)>>(b&7)&c},H=function(a,b){var c=b/8|0;return(a[c]|a[c+1]<<8|a[c+2]<<16)>>(b&7)},V=function(a,b,c){if(null==b||0>b)b=0;if(null==c||c>a.length)c=a.length;var g=new (2==a.BYTES_PER_ELEMENT?B:4==a.BYTES_PER_ELEMENT?
L:n)(c-b);g.set(a.subarray(b,c));return g},W=["unexpected EOF","invalid block type","invalid length/literal","invalid distance","stream finished","no stream handler",,"no callback","invalid UTF-8 data","extra field too long","date not in range 1980-2099","filename too long","stream finishing","invalid zip data"],u=function(a,b,c){b=Error(b||W[a]);b.code=a;Error.captureStackTrace&&Error.captureStackTrace(b,u);if(!c)throw b;return b},K=function(a,b,c){var g=a.length;if(!g||c&&c.f&&!c.l)return b||new n(0);
var f=!b||c,q=!c||c.i;c||={};b||=new n(3*g);var z=function(E){var Q=b.length;E>Q&&(E=new n(Math.max(2*Q,E)),E.set(b),b=E)},C=c.f||0,d=c.p||0,k=c.b||0,p=c.l,w=c.d,x=c.m,v=c.n,I=8*g;do{if(!p){C=t(a,d,1);var e=t(a,d+1,3);d+=3;if(e)if(1==e)p=T,w=U,x=9,v=5;else if(2==e){x=t(a,d,31)+257;w=t(a,d+10,15)+4;p=x+t(a,d+5,31)+1;d+=14;v=new n(p);var m=new n(19);for(e=0;e<w;++e)m[R[e]]=t(a,d+3*e,7);d+=3*w;e=G(m);w=(1<<e)-1;var J=D(m,e,1);for(e=0;e<p;)if(m=J[t(a,d,w)],d+=m&15,r=m>>>4,16>r)v[e++]=r;else{var A=m=0;
16==r?(A=3+t(a,d,3),d+=2,m=v[e-1]):17==r?(A=3+t(a,d,7),d+=3):18==r&&(A=11+t(a,d,127),d+=7);for(;A--;)v[e++]=m}p=v.subarray(0,x);e=v.subarray(x);x=G(p);v=G(e);p=D(p,x,1);w=D(e,v,1)}else u(1);else{var r=((d+7)/8|0)+4;d=a[r-4]|a[r-3]<<8;e=r+d;if(e>g){q&&u(0);break}f&&z(k+d);b.set(a.subarray(r,e),k);c.b=k+=d;c.p=d=8*e;c.f=C;continue}if(d>I){q&&u(0);break}}f&&z(k+131072);r=(1<<x)-1;J=(1<<v)-1;for(A=d;;A=d){m=p[H(a,d)&r];e=m>>>4;d+=m&15;if(d>I){q&&u(0);break}m||u(2);if(256>e)b[k++]=e;else if(256==e){A=
d;p=null;break}else{m=e-254;if(264<e){e-=257;var y=M[e];m=t(a,d,(1<<y)-1)+O[e];d+=y}e=w[H(a,d)&J];y=e>>>4;e||u(3);d+=e&15;e=S[y];3<y&&(y=N[y],e+=H(a,d)&(1<<y)-1,d+=y);if(d>I){q&&u(0);break}f&&z(k+131072);for(m=k+m;k<m;k+=4)b[k]=b[k-e],b[k+1]=b[k+1-e],b[k+2]=b[k+2-e],b[k+3]=b[k+3-e];k=m}}c.l=p;c.p=A;c.b=k;c.f=C;p&&(C=1,c.m=x,c.d=w,c.n=v)}while(!C);return k==b.length?b:V(b,0,k)};h=new n(0);l="undefined"!=typeof TextDecoder&&new TextDecoder;try{l.decode(h,{stream:!0})}catch(a){}window.unzip=function(a,
b){if(31==a[0]&&139==a[1]&&8==a[2]){var c=a.subarray;31==a[0]&&139==a[1]&&8==a[2]||u(6,"invalid gzip data");var g=a[3],f=10;g&4&&(f+=a[10]|(a[11]<<8)+2);for(var q=(g>>3&1)+(g>>4&1);0<q;q-=!a[f++]);c=c.call(a,f+(g&2),-8);b||(b=a.length,b=new n((a[b-4]|a[b-3]<<8|a[b-2]<<16|a[b-1]<<24)>>>0));a=K(c,b)}else 8!=(a[0]&15)||7<a[0]>>4||(a[0]<<8|a[1])%31?a=K(a,b):((8!=(a[0]&15)||7<a[0]>>>4||(a[0]<<8|a[1])%31)&&u(6,"invalid zlib data"),a[1]&32&&u(6,"invalid zlib data: preset dictionaries not supported"),a=K(a.subarray(2,
-4),b));return a}})();
"""
