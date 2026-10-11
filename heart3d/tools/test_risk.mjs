// Plain-node unit test for the colour/probability logic:  npm run test:lib
import assert from 'node:assert/strict'
import { riskToColor, riskBand, formatPct, NO_DATA_COLOR } from '../src/lib/risk.js'

assert.equal(riskToColor(0), '#2ecc71')
assert.equal(riskToColor(0.5), '#f1c40f')
assert.equal(riskToColor(1), '#e53935')
assert.equal(riskToColor(-3), '#2ecc71')          // clamped
assert.equal(riskToColor(7), '#e53935')           // clamped
assert.equal(riskToColor(null), NO_DATA_COLOR)
assert.equal(riskToColor(undefined), NO_DATA_COLOR)
assert.equal(riskToColor(NaN), NO_DATA_COLOR)
assert.match(riskToColor(0.25), /^#[0-9a-f]{6}$/)
assert.equal(riskBand(0.29).key, 'low'); assert.equal(riskBand(0.3).key, 'mid')
assert.equal(riskBand(0.59).key, 'mid'); assert.equal(riskBand(0.6).key, 'high')
assert.equal(riskBand(null).key, 'none')
assert.equal(formatPct(0.724), '72%'); assert.equal(formatPct(null), '—'); assert.equal(formatPct(1.4), '100%')
console.log('risk.js: all tests passed')
