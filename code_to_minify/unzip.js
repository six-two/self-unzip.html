import {decompressSync} from 'fflate';

window.unzip = decompressSync; // needed to "properly" export it in a way that I can access it later
