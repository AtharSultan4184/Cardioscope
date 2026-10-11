// Required by the task: clear, always-visible clinical safety disclaimer.
export function DisclaimerBanner() {
  return (
    <div className="disclaimer" role="alert">
      <b>⚠ Decision-support / educational prototype only.</b> Predictions are not a diagnosis and are{' '}
      <b>not a substitute for formal diagnostic imaging</b> (e.g. coronary angiography or CT angiography)
      or for assessment by a qualified clinician.
    </div>
  )
}

export function ModelNotes() {
  return (
    <div className="notes">
      <p>
        <b>Schematic anatomy:</b> the LAD, LCX and RCA paths are drawn by hand along typical coronary
        courses. They are <b>not</b> patient-specific and do not show where a lesion is inside a vessel.
      </p>
      <p>
        The source heart model is <b>cut open at the front</b>, so the LAD is drawn on the cut face. Use the
        <i> Back</i> view to see the LCX and RCA on the intact surface.
      </p>
    </div>
  )
}

// CC BY 4.0 requires attribution + indication of changes.
export function Attribution() {
  return (
    <footer className="attrib">
      Base 3D model “Human_heart_3d_model” by <b>marxtrax</b> (
      <a href="https://skfb.ly/oDKZq" target="_blank" rel="noreferrer">Sketchfab</a>), licensed{' '}
      <a href="http://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">CC BY 4.0</a>.
      Edited with assistance from Claude (Anthropic): converted to a static mesh, textures resized,
      coronary arteries added.
    </footer>
  )
}
