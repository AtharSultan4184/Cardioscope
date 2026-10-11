# 3D Coronary Viewer

Interactive 3D heart with the **LAD, LCX and RCA** drawn as separate, clickable vessels whose colour follows a
predicted stenosis probability (green → amber → red; grey = no prediction).

> ⚠ Decision-support / educational prototype only. Not a diagnosis; not a substitute for formal diagnostic imaging.

## Use it

The integrated application is served from the project root:

```powershell
python -m uvicorn app:app --reload
```

Open <http://localhost:8000/>. The dashboard sends each real prediction to this
viewer; vessel rows and 3D colors update together. Manual demo controls and
calibration sliders are hidden in the integrated view.

For standalone viewer development only:

```bash
npm install
npm run dev          # open http://localhost:5173/heart3d/
```

Build the viewer for the integrated dashboard with `npm run build`. FastAPI
serves the generated `dist` directory under `/heart3d/`.

Controls: drag = rotate, scroll/pinch = zoom, click a vessel (or its row) = inspect. Buttons: Front/Back/Left/Right,
Reset view, Heartbeat. When opened standalone, sliders and demo values are
illustrative manual inputs, not model predictions. The viewer starts with no
prediction.

## Viewer component API
`<HeartViewer risks={{ LAD: 0.82, LCX: 0.31, RCA: 0.12 }} selected={id} onSelect={setId} />`
Probabilities are 0–1. Keys must equal the model target names (`LAD`, `LCX`, `RCA`). `null`/missing → grey.

## What is in the repo
| Path | Purpose |
|---|---|
| `public/models/human_heart.glb` | Static, 1.6 MB heart (baked from the original 17 MB skinned file) |
| `src/config/arteryPaths.json` | Centre-lines of the 3 arteries (generated; schematic) |
| `src/config/anatomy.js` | One place that defines vessels, labels, camera presets (extensibility) |
| `src/components/HeartViewer.jsx`, `Artery.jsx` | The reusable 3D component |
| `src/lib/risk.js` | Probability → colour/band (unit-tested: `npm run test:lib`) |
| `tools/bake_heart.py` | Original GLB → static GLB (pose baked, textures resized) |
| `tools/place_arteries.py` + `artery_waypoints.json` | Designs and checks artery paths on the mesh |
| `tools/check_assets.py`, `check_syntax.cjs` | Validate the GLB/JSON; syntax-check the web source |
| `docs/artery_placement_check.png` | Overlay used to verify artery placement (dashed = hidden behind the heart) |

## Rebuild the assets (optional, needs the original download)
```bash
pip install -r tools/requirements.txt
python tools/bake_heart.py <source.glb> <textures_dir> public/models/human_heart.glb
python tools/place_arteries.py heart_baked.npz tools/artery_waypoints.json src/config/arteryPaths.json docs/artery_placement_check.png
python tools/check_assets.py
```
Re-running these reproduces the committed files byte-for-byte.

## Why the model was re-baked
The original GLB is a *skinned* mesh under a node scaled 0.01 and uses the deprecated
`KHR_materials_pbrSpecularGlossiness` extension; Three.js may render it at the wrong size/without textures, and
attached artery geometry could not be aligned reliably. A static mesh also keeps interaction smooth without a GPU.
The 24-clip "beating" animation of the original (valve/atrium joints) is therefore **not** included; the optional
Heartbeat button is a simple whole-organ scale pulse, applied to heart and arteries together.

## Known limitations (state these honestly in the report/video)
- Artery paths are **schematic**, hand-placed along typical courses; **not** patient-specific, and no lesion location inside a vessel is shown (the dataset has no such information).
- The source model is **cut open at the front**; the LAD is therefore drawn on the cut face. Rotate to Back to see LCX/RCA on intact surface.
- The RCA path continues into the posterior descending branch for visual continuity.
- Tube radius is exaggerated (0.2 cm) so vessels are visible and clickable.
- Artery paths are illustrative overlays, not segmentation from the mesh or diagnostic findings.
- Browser rendering and controls have been smoke-tested in Chromium; see `AI_USAGE.md` for the verified scope.
