import { useEffect, useState } from 'react'
import HeartViewer from './components/HeartViewer'
import { DisclaimerBanner, ModelNotes, Attribution } from './components/Disclaimer'
import { ARTERIES, ARTERY_IDS } from './config/anatomy'
import { riskToColor, riskBand, formatPct, RISK_GRADIENT, isValidProb } from './lib/risk'

// Placeholder input so the 3D colouring can be tested BEFORE the ML backend exists.
// These numbers are typed in by hand - they are NOT model predictions.
const DEMO_VALUES = { LAD: 0.8, LCX: 0.35, RCA: 0.15 }

export default function App() {
  const embedded = new URLSearchParams(window.location.search).get('embed') === '1'
  const [risks, setRisks] = useState(null)       // null = "no prediction"
  const [riskSource, setRiskSource] = useState('none')
  const [selected, setSelected] = useState(null)
  const [beat, setBeat] = useState(false)
  const [view, setView] = useState(null)
  const [calibrate, setCalibrate] = useState(false)
  const [offset, setOffset] = useState([0, 0, 0])
  const [scale, setScale] = useState(1)

  const sel = selected ? ARTERIES[selected] : null
  const selRisk = selected ? risks?.[selected] : null
  const goView = (name) => setView({ name, n: Date.now() })
  const handleVesselSelect = (id) => {
    setSelected(id)
    if (embedded) {
      window.parent.postMessage(
        { type: 'cardioscope:vessel-selected', vessel: id },
        window.location.origin,
      )
    }
  }

  useEffect(() => {
    if (!embedded) return undefined

    const handleMessage = (event) => {
      if (event.origin !== window.location.origin || event.source !== window.parent) return
      if (event.data?.type === 'cardioscope:prediction') {
        const nextRisks = Object.fromEntries(
          ARTERY_IDS.map((id) => {
            const probability = event.data.vessels?.[id]?.probability
            return [id, isValidProb(probability) ? probability : null]
          }),
        )
        setRisks(nextRisks)
        setRiskSource('model')
      } else if (event.data?.type === 'cardioscope:clear-prediction') {
        setRisks(null)
        setRiskSource('none')
      } else if (
        event.data?.type === 'cardioscope:select-vessel' &&
        (ARTERY_IDS.includes(event.data.vessel) || event.data.vessel === null)
      ) {
        setSelected(event.data.vessel)
      }
    }

    window.addEventListener('message', handleMessage)
    window.parent.postMessage({ type: 'cardioscope:viewer-ready' }, window.location.origin)
    return () => window.removeEventListener('message', handleMessage)
  }, [embedded])

  return (
    <div className={`app${embedded ? ' embedded' : ''}`}>
      {!embedded && <DisclaimerBanner />}

      <div className={`main${embedded ? ' embedded' : ''}`}>
        <section className="viewer">
          <HeartViewer
            risks={risks}
            selected={selected}
            onSelect={handleVesselSelect}
            beat={beat}
            showPoints={calibrate}
            offset={offset}
            scale={scale}
            viewRequest={view}
          />
          <div className="toolbar">
            {['front', 'back', 'left', 'right'].map((v) => (
              <button key={v} onClick={() => goView(v)}>{v[0].toUpperCase() + v.slice(1)}</button>
            ))}
            <button onClick={() => goView('default')}>Reset view</button>
            <button className={beat ? 'on' : ''} onClick={() => setBeat(!beat)}>Heartbeat</button>
          </div>
          <div className="hint">Drag to rotate · scroll/pinch to zoom · click a vessel to inspect</div>
        </section>

        {!embedded && <aside className="panel">
          <h2>Vessel stenosis risk</h2>
          <p className="muted small">
            {embedded
              ? 'Predicted vessel stenosis probabilities from the patient dashboard.'
              : 'Demo input (manual sliders) — not model predictions.'}
          </p>

          {ARTERY_IDS.map((id) => {
            const p = risks?.[id]
            return (
              <div
                key={id}
                className={`row${selected === id ? ' sel' : ''}`}
                onClick={() => handleVesselSelect(selected === id ? null : id)}
              >
                <span className="dot" style={{ background: riskToColor(p) }} />
                <span className="name">{id}</span>
                {!embedded && (
                  <input
                    type="range" min="0" max="100" disabled={!risks}
                    value={isValidProb(p) ? Math.round(p * 100) : 0}
                    onClick={(e) => e.stopPropagation()}
                    onChange={(e) => {
                      setRisks({ ...risks, [id]: Number(e.target.value) / 100 })
                      setRiskSource('demo')
                    }}
                    aria-label={`${id} probability`}
                  />
                )}
                <span className="pct">{formatPct(p)}</span>
              </div>
            )
          })}

          {!embedded && (
            <div className="btn-row">
              <button onClick={() => { setRisks(null); setRiskSource('none') }}>Clear (no prediction)</button>
              <button onClick={() => { setRisks(DEMO_VALUES); setRiskSource('demo') }}>Demo values</button>
            </div>
          )}

          <div className="legend">
            <div className="bar" style={{ background: RISK_GRADIENT }} />
            <div className="ticks"><span>0%</span><span>50%</span><span>100%</span></div>
            <div className="muted small">Grey = no prediction. Bands (&lt;30% / 30–60% / ≥60%) are for display only, not clinical cut-offs.</div>
          </div>

          <h3>Selected vessel</h3>
          {sel ? (
            <div className="card" style={{ borderColor: riskToColor(selRisk) }}>
              <div className="card-title">{sel.id} — {sel.label}</div>
              <div className="big" style={{ color: riskToColor(selRisk) }}>{formatPct(selRisk)}</div>
              <div className="muted">
                {isValidProb(selRisk)
                  ? riskSource === 'model'
                    ? `${riskBand(selRisk).label} model probability; educational estimate`
                    : `${riskBand(selRisk).label} manual demo value; not a model prediction`
                  : 'No vessel prediction available'}
              </div>
              <p>{sel.description}</p>
              <p className="muted small">Typically supplies: {sel.supplies}</p>
            </div>
          ) : (
            <div className="card muted">Click a vessel in the 3D view (or a row above) to inspect it.</div>
          )}

          <ModelNotes />

          {!embedded && (
            <details className="calib" onToggle={(e) => setCalibrate(e.currentTarget.open)}>
              <summary>Calibrate artery placement</summary>
              <p className="muted small">Shows centre-line points. Nudge the whole artery set if it looks off the surface.</p>
              {['x', 'y', 'z'].map((axis, i) => (
                <label key={axis} className="slider">
                  offset {axis}: {offset[i].toFixed(2)}
                  <input type="range" min="-1" max="1" step="0.05" value={offset[i]}
                    onChange={(e) => { const o = [...offset]; o[i] = Number(e.target.value); setOffset(o) }} />
                </label>
              ))}
              <label className="slider">
                scale: {scale.toFixed(2)}
                <input type="range" min="0.9" max="1.1" step="0.01" value={scale}
                  onChange={(e) => setScale(Number(e.target.value))} />
              </label>
              <div className="btn-row">
                <button onClick={() => { setOffset([0, 0, 0]); setScale(1) }}>Reset</button>
                <button onClick={() => navigator.clipboard?.writeText(JSON.stringify({ offset, scale }))}>Copy values</button>
              </div>
            </details>
          )}
        </aside>}
      </div>

      {!embedded && <Attribution />}
    </div>
  )
}
