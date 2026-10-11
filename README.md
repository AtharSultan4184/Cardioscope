# CardioScope

CardioScope is an educational prototype for estimating overall CAD and
patient-level LAD, LCX, and RCA stenosis labels from clinical features. The
single dashboard combines a FastAPI prediction service, a React Three Fiber
heart viewer, model evaluation results, and an interpretable CAD contribution
list.

## Clinical safety and scope

This is a decision-support/educational demonstration, not a diagnosis or
clinical risk assessment. Predictions are not clinically validated and must
not replace assessment by a qualified clinician or formal diagnostic imaging.
The 3D coronary paths are schematic overlays; color indicates a model score,
not a lesion location or severity map. The input measurements are clinical
features, not anatomical coordinates.

## Dataset and preprocessing

- The project uses the supplied `extention of Z-Alizadeh sani dataset.xlsx`,
  sheet `Sheet 1 - Table 1`: 303 patient rows, with `Cath` (216 CAD, 87 Normal)
  and vessel labels LAD (177 Stenotic), LCX (119 Stenotic), and RCA (114
  Stenotic). The workbook's second sheet has headings but no patient rows.
- `Cath`, `LAD`, `LCX`, and `RCA` are targets only and are excluded from every
  model's feature matrix to prevent target leakage.
- Numeric missing values use median imputation and standardization. Categorical
  missing values use most-frequent imputation and one-hot encoding.
- Four independent, class-weighted logistic-regression pipelines are
  evaluated using separate stratified 80/20 holdouts (seed 42), then refitted
  on all 303 rows. The CAD explanation lists signed input contributions on the
  model's log-odds scale; they are not causal effects or SHAP values.
- The extension workbook was supplied for this project. Its external
  provenance and redistribution terms have not been independently verified.
  The related [UCI Z-Alizadeh Sani base dataset](https://archive.ics.uci.edu/dataset/412/z+alizadeh+sani),
  DOI [10.24432/C5Q31T](https://doi.org/10.24432/C5Q31T), is listed by UCI
  under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), which
  requires attribution. The supplied workbook metadata names “alizadeh” as
  creator but does not identify the source or license for the added vessel
  labels. Do not publish the extension workbook or derived model artifacts
  until those additional terms are confirmed; the base UCI license alone does
  not establish rights for the extension.

### Current holdout results

| Target | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| CAD | 80.3% | 89.7% | 81.4% | 85.4% | 89.0% |
| LAD stenosis | 73.8% | 79.4% | 75.0% | 77.1% | 82.9% |
| LCX stenosis | 59.0% | 48.3% | 58.3% | 52.8% | 64.2% |
| RCA stenosis | 72.1% | 63.6% | 60.9% | 62.2% | 73.9% |

These are single small-holdout educational estimates. In particular, LCX
performance is weak; none of these figures demonstrates clinical validity or
reliable individual risk estimation.

## Run locally (Windows PowerShell)

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Push-Location .\heart3d
npm install
npm run test:lib
npm run build
Pop-Location
python train_model.py
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/>. The dashboard is the single entry point; the
3D viewer is served from the locally built `heart3d` module under `/heart3d/`.
The viewer can also run standalone for UI development with `npm run dev` from
`heart3d`; predictions are connected when it is embedded in the dashboard.

## Deploy with GitHub Pages and Render

GitHub Pages serves static files; it cannot run the FastAPI app or load the
trained models. Deploy the dashboard/viewer to Pages and the API to Render:

1. In Render, create a Blueprint from this repository and use `render.yaml`.
   Set `CORS_ORIGINS` to the Pages **origin** (scheme and host only), such as
   `https://your-user.github.io`. For a custom domain, use that domain's origin.
2. After Render deploys, copy the service URL, such as
   `https://cardioscope-api.onrender.com`.
3. In the GitHub repository, go to **Settings → Secrets and variables →
   Actions → Variables** and add the repository variable
   `CARDIOSCOPE_API_URL` with the Render service URL.
4. In **Settings → Pages**, select **GitHub Actions** as the deployment source.
   Push to the `main` branch (or run the Pages workflow manually). The workflow
   builds and tests the viewer, puts it beside the dashboard, and configures
   the API URL.

The Pages workflow intentionally fails if `CARDIOSCOPE_API_URL` is missing, so
the dashboard cannot deploy with its input fields disconnected. `CORS_ORIGINS`
must exactly match the Pages origin; do not include the project path or a
trailing slash. The frontend uses relative viewer paths, so both user-site and
project-site Pages URLs work. For local FastAPI use, `config.js` has an empty
API URL and the dashboard uses the same-origin API.

The Render service loads the model artifacts in `models/`; confirm that the
dataset and derived-artifact redistribution terms noted above permit your
deployment before making the model available publicly.

## Architecture and files

- `train_model.py`: validates target labels, excludes all four target columns,
  evaluates and trains the four pipelines, and writes artifacts under `models/`.
- `app.py`: serves the dashboard, schema, metrics, predictions, and built 3D
  viewer; patient entries are processed in memory and are not saved.
- `index.html`: patient form, CAD score, vessel estimates, holdout metrics, and
  per-patient CAD contribution dashboard.
- `heart3d/src/`: interactive Three.js heart model, schematic LAD/LCX/RCA
  overlays, probability color mapping, and vessel selection.
- `models/prediction_models.joblib`, `models/schema.json`, and
  `models/metrics.json`: generated artifacts; regenerate with `python train_model.py`.
e dataset or trained artifacts.

## Attribution

The bundled base heart model, “Human_heart_3d_model” by marxtrax, is from
[Sketchfab](https://skfb.ly/oDKZq) under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). It was converted to
a static mesh, its textures were resized, and schematic coronary overlays
were added, with editing and adaptation assistance from Claude (Anthropic).
The source's detailed animation is not included.

## AI assistance disclosure

AI assistance was used to inspect the workbook, develop the data-preprocessing
and model-training pipeline, implement the API and dashboard, integrate the
3D viewer, test the prototype, and draft project documentation. The student
should understand and independently explain the preprocessing, leakage
prevention, evaluation limits, model contributions, and schematic nature of
the visualization before presenting.
