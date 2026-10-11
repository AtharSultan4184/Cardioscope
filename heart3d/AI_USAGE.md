# AI-assisted parts (keep updated; use for the README disclosure)

Tool: Claude (Anthropic), used as a pair-programming assistant. The student remains responsible for understanding and explaining everything below.

| Part | What the AI did | What the student must be able to explain |
|---|---|---|
| Task analysis & architecture plan | Summarised the brief, proposed stack, risks | Why FastAPI + React Three Fiber; what leakage means |
| `tools/bake_heart.py` | Wrote the GLB baking script after inspecting the file (skin scale issue, deprecated extension) | What skinning is; why static mesh is safer; what the script outputs |
| `tools/place_arteries.py`, `artery_waypoints.json` | Wrote the placement tool; chose artery waypoints by eye using rendered overlays | The arteries are schematic; how "outermost-surface lookup" works |
| `src/**` (React/Three.js viewer) | Wrote all components and CSS | Component flow: risks → colour → tube; events; camera presets |
| `src/lib/risk.js` + test | Wrote and tested colour mapping | Colour ramp; display bands are not clinical thresholds |
| Docs | Drafted README/ATTRIBUTION | CC BY obligations |
| Local setup and review (Copilot SDK in VS Code) | Extracted and ran the module, initialized it with no predictions, added a mobile layout, upgraded Vite to a patched compatible release, and verified rendering/interactions | Why demo values are not model output; how the mesh and schematic artery overlays differ |
| Extended dataset and final integration (Copilot SDK in VS Code) | Inspected the supplied workbook's target columns, implemented four leakage-safe classifiers and metrics, connected FastAPI predictions to the embedded viewer, coordinated the dashboard dark theme/layout, and drafted the project report and video script | How each target is trained/evaluated; why probabilities and explanations are educational estimates; why vessel paths do not localize lesions |

## What was actually verified (and what was not)
Verified before handoff by running:
- Baked GLB is structurally valid (chunk sizes, buffer ranges, images decode, indices in range) - `tools/check_assets.py`.
- Artery centre-lines lie inside the heart's bounds and were inspected on rendered overlays from 4 sides (`docs/artery_placement_check.png`).
- Asset pipeline reproduces the committed files byte-for-byte.
- `npm run test:lib` passes and `npm run build` succeeds.
- The 3D view renders in Chromium with the bundled heart and all three artery overlays. Front/Back and Heartbeat controls, vessel selection and the no-prediction state were smoke-tested.
- `npm audit` reports no known dependency vulnerabilities after the Vite upgrade.

**Not fully verified:** the standalone `tools/check_syntax.cjs` helper requires a globally installed TypeScript package that is not declared by this module; the production Vite build successfully parses and bundles the source. Automated click-through and frame-rate benchmarking on a range of physical devices have not been done.

## Browser checklist (do this once, then tick it off)
- [x] `npm install`, `npm run test:lib`, and `npm run build` complete; browser dev server starts
- [x] Heart appears with red/blue texture, centred with visible coronary overlays
- [x] Three arteries are visible; their schematic placement is documented and rendered from four sides
- [x] Rotate/zoom are provided by OrbitControls; Front/Back/Left/Right/Reset and Heartbeat controls render
- [ ] Clicking each artery selects it (white outline + side card); clicking the background deselects
- [ ] Clicking the front of the heart does NOT select an artery hidden behind it
- [ ] Labels hide when their artery is behind the heart
- [ ] Confirm smooth interaction on a laptop without a dedicated GPU
