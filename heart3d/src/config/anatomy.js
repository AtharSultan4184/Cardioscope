// Everything the viewer needs to know about the anatomy, in ONE place.
// To add a vessel/structure later: add its centre-line to arteryPaths.json (tools/place_arteries.py
// generates it) and add an entry below. No viewer code changes needed.
import paths from './arteryPaths.json'

export const MODEL_URL = `${import.meta.env.BASE_URL}models/human_heart.glb`

// Must match the ids used by the ML backend (targets LAD, LCX, RCA).
export const ARTERY_IDS = ['LAD', 'LCX', 'RCA']

// labelT = where along the vessel (0..1) the on-model label is attached.
const EXTRA = {
  LAD: { supplies: 'Front of the heart', labelT: 0.6 },
  LCX: { supplies: 'Side and back of the heart', labelT: 0.3 },
  RCA: { supplies: 'Right side and bottom of the heart', labelT: 0.18 },
}

export const ARTERIES = Object.fromEntries(
  ARTERY_IDS.map((id) => [id, { id, ...paths.arteries[id], ...EXTRA[id] }]),
)

// Tube radius in model units (1 unit ~ 1 cm). Real arteries are thinner; this is exaggerated so it is clickable.
export const ARTERY_RADIUS = 0.2

// Camera presets (camera position; the camera always looks at the origin).
// +z = front of the heart, +x = patient's left.
export const VIEW_PRESETS = {
  default: [9, 3, 25],
  front: [0, 0, 27],
  back: [0, 0, -27],
  left: [27, 0, 0],
  right: [-27, 0, 0],
}
