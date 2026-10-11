// Syntax + import-path check for the web source (no npm install needed; uses a globally installed TypeScript).
const ts = require('typescript'), fs = require('fs'), path = require('path')
let bad = 0
function walk(d) { return fs.readdirSync(d, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]) }
for (const f of walk('src').filter(f => /\.(jsx?|mjs)$/.test(f))) {
  const src = fs.readFileSync(f, 'utf8')
  const out = ts.transpileModule(src, { fileName: f, reportDiagnostics: true, compilerOptions: { jsx: ts.JsxEmit.Preserve, target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext, allowJs: true } })
  for (const d of out.diagnostics) { bad++; console.log('SYNTAX', f, ts.flattenDiagnosticMessageText(d.messageText, '\n')) }
  for (const m of src.matchAll(/from\s+['"](\.[^'"]+)['"]/g)) {
    const p = path.resolve(path.dirname(f), m[1])
    if (!['', '.js', '.jsx', '.json', '.css'].some(e => fs.existsSync(p + e) && fs.statSync(p + e).isFile())) { bad++; console.log('MISSING IMPORT', f, m[1]) }
  }
  for (const m of src.matchAll(/^import\s+['"](\.[^'"]+)['"]/gm)) {
    if (!fs.existsSync(path.resolve(path.dirname(f), m[1]))) { bad++; console.log('MISSING IMPORT', f, m[1]) }
  }
  console.log('checked', f)
}
console.log(bad ? `${bad} PROBLEM(S)` : 'all files parse; all relative imports resolve')
process.exit(bad ? 1 : 0)
