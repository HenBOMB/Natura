const fs = require('fs')
const path = require('path')

console.log(`I: ${path.join(__dirname, '.././.././')}`)
console.log(`I: ${path.join(__dirname, './~/')}`)
console.log(`II: ${path.join(__dirname, '../')}`)
console.log(`III: ${path.join(__dirname, './')}`)