// Maps a predicted probability (0..1) to a colour and a display band.
// One place only, so the 3D arteries, the labels and the dashboard always agree.

// Colour ramp: green (low) -> amber (mid) -> red (high).
export const RISK_STOPS = [
  [0.0, [46, 204, 113]],
  [0.5, [241, 196, 15]],
  [1.0, [229, 57, 53]],
]
export const NO_DATA_COLOR = '#8a93a0'

const hex = (n) => Math.round(n).toString(16).padStart(2, '0')

export function isValidProb(p) {
  return typeof p === 'number' && Number.isFinite(p)
}

export function riskToColor(p) {
  if (!isValidProb(p)) return NO_DATA_COLOR
  const x = Math.min(1, Math.max(0, p))
  for (let i = 0; i < RISK_STOPS.length - 1; i++) {
    const [x0, c0] = RISK_STOPS[i]
    const [x1, c1] = RISK_STOPS[i + 1]
    if (x <= x1) {
      const t = (x - x0) / (x1 - x0)
      return '#' + [0, 1, 2].map((k) => hex(c0[k] + (c1[k] - c0[k]) * t)).join('')
    }
  }
  return '#' + RISK_STOPS[RISK_STOPS.length - 1][1].map(hex).join('')
}

// Display bands ONLY - these are not clinical decision thresholds.
export function riskBand(p) {
  if (!isValidProb(p)) return { key: 'none', label: 'No prediction' }
  if (p < 0.3) return { key: 'low', label: 'Lower' }
  if (p < 0.6) return { key: 'mid', label: 'Intermediate' }
  return { key: 'high', label: 'Higher' }
}

export function formatPct(p) {
  return isValidProb(p) ? `${Math.round(Math.min(1, Math.max(0, p)) * 100)}%` : '—'
}

// CSS gradient string that matches the ramp above (used for the legend bar).
export const RISK_GRADIENT =
  'linear-gradient(90deg, ' +
  RISK_STOPS.map(([x, c]) => `rgb(${c.join(',')}) ${x * 100}%`).join(', ') +
  ')'
