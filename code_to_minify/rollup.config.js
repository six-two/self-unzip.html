import { nodeResolve } from '@rollup/plugin-node-resolve';
import minify from 'rollup-plugin-minify'

export default {
  input: 'main.js',
  output: {
    dir: 'output',
    format: 'iife'
  },
  plugins: [
    nodeResolve(),
    minify({iife: 'iife.min.js'})
  ]
};
