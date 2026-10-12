# CardioScope — Project Report (Hinglish)

**Live demo:** <https://cardioscope-i8un.onrender.com/>  
**Source code:** <https://github.com/AtharSultan4184/Cardioscope>

> **Zaroori safety note:** CardioScope ek educational prototype hai. Yeh
> diagnosis, doctor ki advice, ya medical test ka replacement nahi hai. Iske
> model outputs clinically validated nahi hain. Is project ko real patient
> treatment decide karne ke liye use nahi karna chahiye.

## 1. Project ka short introduction

CardioScope ek web-based demonstration hai jo clinical features enter karne par
Coronary Artery Disease (CAD) ka estimated probability aur teen coronary
vessels—LAD, LCX, RCA—ke stenosis labels ki estimated probabilities dikhata
hai. Dashboard ke saath ek interactive 3D heart model bhi hai.

Project ka main purpose machine-learning pipeline ko samjhana aur ek
interactive visualization dena hai: input form se data lena, trained models se
probability nikalna, result ko dashboard mein dikhana, aur vessel estimates ko
schematic 3D heart par visualize karna. Yeh kisi individual ke liye reliable
clinical risk assessment dene ka claim nahi karta.

## 2. Is project mein kya-kya banaya gaya

- Clinical measurements ke liye grouped web form; fields optional hain.
- Overall CAD, LAD, LCX aur RCA ke liye chaar alag trained models.
- CAD probability, model class, vessel probabilities aur feature-contribution
  list dikhane wala results dashboard.
- Holdout test-set par model evaluation metrics.
- Mouse/touch se rotate aur zoom hone wala 3D heart; front, back, left, right,
  reset-view aur illustrative heartbeat controls.
- Patient input, API aur 3D viewer ko connect karne wali web application.
- Docker-based Render deployment aur GitHub repository mein source files.

## 3. Data aur model training

Training ke liye supplied `extention of Z-Alizadeh sani dataset.xlsx`
workbook ki `Sheet 1 - Table 1` sheet use hoti hai. Is sheet mein 303 rows
hain. Har row dataset ke ek record ko represent karti hai.

Models chaar alag target labels predict karte hain:

| Model target | Dataset label column | Dataset mein positive class |
|---|---|---|
| CAD | `Cath` | `CAD` |
| LAD | `LAD` | `Stenotic` |
| LCX | `LCX` | `Stenotic` |
| RCA | `RCA` | `Stenotic` |

In chaar target columns ko input features se alag rakha gaya hai. Isse model ko
answer/label ko input ke roop mein dekh kar artificially achha result lene se
rokne ki koshish hoti hai; is problem ko **target leakage** kehte hain.

### Training ke steps

1. Workbook se feature columns aur har target ke labels load kiye jaate hain.
2. Har target ko alag binary classification problem ke roop mein process kiya
   jaata hai.
3. Har model ke liye stratified 80/20 split banta hai. Is run mein
   `random_state=42` hai; stratification ka matlab split mein classes ka
   proportion lagbhag preserve karna.
4. Numeric values ke liye missing values median se fill hoti hain, phir
   `StandardScaler` se scale/standardize ki jaati hain.
5. Categorical values ke missing entries most-frequent value se fill hoti
   hain, phir `OneHotEncoder` unhein model-readable numeric columns mein badalta
   hai. Unknown categories encoding ke dauran error ke bajay ignore hoti hain.
6. `class_weight="balanced"` wala Logistic Regression train hota hai. Is
   setting se training mein class imbalance ko account karne ki koshish hoti
   hai.
7. Holdout set par metrics calculate karne ke baad final pipeline us target ke
   sabhi 303 available records par dobara fit hoti hai.

Training ka main code `train_model.py` mein hai. Yeh models, feature schema aur
metrics ko `models/` mein save karta hai.

## 4. Form ke fields aur abbreviations

Form mein **55 fields** paanch groups mein dikhte hain. Descriptions neeche
common medical usage ke mutabik hain; workbook mein har variable ka complete
codebook ya unit supplied nahi hai. Isliye jahan coding/unit confirm nahi hai,
use guess nahi karna chahiye. Demonstration ke liye blank fields allowed hain;
system unhein training data ke imputation rules se handle karta hai.

### A. Demographics

| Field | Full form / simple meaning | Form mein type |
|---|---|---|
| Age | Vyakti ki age, years | Number |
| Weight | Body weight; workbook ki unit explicitly document nahi hai | Number |
| Length | Body length/height; workbook ki unit explicitly document nahi hai | Number |
| Sex | Dataset ka sex category; source mein `Male` aur `Fmale` spellings hain (`Fmale` source ki spelling hai) | Category |
| BMI | **Body Mass Index**; weight aur height se sambandhit index, aam taur par kg/m² | Number |

### B. History and examination

| Field | Full form / simple meaning | Form mein type |
|---|---|---|
| DM | **Diabetes Mellitus**; dataset mein 0/1 numeric field | Number |
| HTN | **Hypertension**; high blood pressure history, 0/1 numeric field | Number |
| Current Smoker | Current smoking status, 0/1 numeric field | Number |
| EX-Smoker | Ex-smoker/former smoking status, 0/1 numeric field | Number |
| FH | **Family History**; dataset mein 0/1 numeric field | Number |
| Obesity | Obesity status; `Y`/`N` category | Category |
| CRF | **Chronic Renal Failure**; chronic kidney-function condition, `Y`/`N` | Category |
| CVA | **Cerebrovascular Accident**; stroke history ke liye common medical term, `Y`/`N` | Category |
| Airway disease | Airway/lung disease status, `Y`/`N` | Category |
| Thyroid Disease | Thyroid condition status, `Y`/`N` | Category |
| CHF | **Congestive Heart Failure**, `Y`/`N` | Category |
| DLP | **Dyslipidemia**; blood lipids abnormal hone ki history, `Y`/`N` | Category |
| BP | **Blood Pressure**; dataset mein numeric reading, unit/codebook yahan specified nahi | Number |
| PR | **Pulse Rate**; dataset mein numeric reading, unit/codebook yahan specified nahi | Number |
| Edema | Body tissues mein fluid swelling ka recorded indicator; 0/1 | Number |
| Weak Peripheral Pulse | Haath/paon ki peripheral pulse weak hone ka recorded status, `Y`/`N` | Category |
| Lung rales | Lungs mein rales/crackles ki examination finding, `Y`/`N` | Category |
| Systolic Murmur | Heart examination mein systolic murmur, `Y`/`N` | Category |
| Diastolic Murmur | Heart examination mein diastolic murmur, `Y`/`N` | Category |
| Typical Chest Pain | Typical chest-pain feature; dataset mein 0/1 | Number |
| Dyspnea | Saans phoolna/breathlessness, `Y`/`N` | Category |
| Function Class | Functional-class code; dataset mein 0–3 values hain, exact class definition/codebook supplied nahi | Number |
| Atypical | Atypical chest-pain feature, `Y`/`N` | Category |
| Nonanginal | Non-anginal chest-pain feature, `Y`/`N` | Category |
| Exertional CP | **Exertional Chest Pain**; dataset mein sirf `N` value recorded hai | Category |
| LowTH Ang | **Low-Threshold Angina** ka abbreviated field-name; dataset mein `N`/`Y` | Category |

### C. ECG

**ECG** ka full form **Electrocardiogram** hai—heart ki electrical activity ka
record. Yeh ECG se sambandhit fields hain:

| Field | Full form / simple meaning | Form mein type |
|---|---|---|
| Q Wave | ECG par Q-wave finding; dataset mein 0/1 | Number |
| St Elevation | **ST-segment elevation** finding; dataset mein 0/1 | Number |
| St Depression | **ST-segment depression** finding; dataset mein 0/1 | Number |
| Tinversion | **T-wave inversion** finding; dataset mein 0/1 | Number |
| LVH | **Left Ventricular Hypertrophy**; `Y`/`N` | Category |
| Poor R Progression | ECG par poor R-wave progression finding, `Y`/`N` | Category |
| BBB | **Bundle Branch Block**; dataset options `LBBB`, `N`, `RBBB` | Category |

`LBBB` = Left Bundle Branch Block; `RBBB` = Right Bundle Branch Block; `N` =
dataset ka no/normal category label.

### D. Laboratory

| Field | Full form / simple meaning | Form mein type |
|---|---|---|
| FBS | **Fasting Blood Sugar** | Number |
| CR | Is dataset mein serum **creatinine** ke liye use hua field-name | Number |
| TG | **Triglycerides** | Number |
| LDL | **Low-Density Lipoprotein** cholesterol | Number |
| HDL | **High-Density Lipoprotein** cholesterol | Number |
| BUN | **Blood Urea Nitrogen** | Number |
| ESR | **Erythrocyte Sedimentation Rate** | Number |
| HB | **Hemoglobin** | Number |
| K | Potassium ka chemical symbol | Number |
| Na | Sodium ka chemical symbol | Number |
| WBC | **White Blood Cell** count | Number |
| Lymph | Lymphocyte count/measure ka dataset field-name | Number |
| Neut | Neutrophil count/measure ka dataset field-name | Number |
| PLT | Platelet count/measure ka dataset field-name | Number |

In lab fields ki units workbook ke available project codebook mein specify nahi
hain. Values ko kisi naye source se units verify kiye bina convert ya compare
nahi karna chahiye.

### E. Echocardiography

**TTE** = **Transthoracic Echocardiography**, chest ke through kiya jaane wala
heart ultrasound; **VHD** = **Valvular Heart Disease**.

| Field | Full form / simple meaning | Form mein type |
|---|---|---|
| EF-TTE | **Ejection Fraction – Transthoracic Echocardiography**; heart pumping function se sambandhit recorded value | Number |
| Region RWMA | **Regional Wall Motion Abnormality**; dataset mein 0–4 codes, exact code-to-region mapping supplied nahi | Number |
| VHD | **Valvular Heart Disease** category; options `N`, `mild`, `Moderate`, `Severe` | Category |

### Categorical aur numeric coding kaise samjhein

- Category dropdowns mein wahi options use karo jo form dikhata hai.
- `Y`/`N` dropdowns dataset ke categorical labels hain.
- Kai numeric fields jaise DM, HTN, smoking indicators aur ECG flags dataset
  mein 0/1 ke roop mein hain. In binary flags ka semantic coding aam taur par
  0/1 hota hai, lekin har field ki official definition source codebook se
  verify honi chahiye.
- **Number field ka matlab yeh nahi ki uski unit hum jaante hain.** Weight,
  Length, BP, PR aur lab measurements ke units ko source codebook ke bina
  certain nahi kehna chahiye.
- `Exertional CP` ki source data mein sirf `N` dekha gaya; UI usi available
  category ko dikhata hai.
- `Function Class` aur `Region RWMA` ke codes ke exact meanings supplied
  metadata mein defined nahi hain; un codes ki clinical interpretation claim
  nahi karni chahiye.

## 5. Website prediction kaise banati hai

Jab visitor form submit karta hai, app 55 feature values collect karti hai.
Blank values ko API model ke training-set medians (numeric) ya most-frequent
categories se fill karta hai. Backend `app.py` mein FastAPI application hai:

1. `GET /api/features` form ke feature names/types/options deta hai.
2. `GET /api/metrics` holdout evaluation values deta hai.
3. `POST /api/predict` input validate karta hai aur chaar model pipelines ko
   call karta hai.
4. API CAD result, LAD/LCX/RCA probabilities aur CAD feature-contribution list
   return karti hai.
5. Dashboard percentages, predicted class, metrics aur contribution list
   dikhata hai.
6. Vessel values iframe ke through 3D viewer ko bheje jaate hain. Viewer
   schematic arteries ko select/highlight karta hai aur probability ke mutabik
   grey/green/amber/red color dikhata hai.

Model ka displayed class `0.50` probability threshold par based hai. Isse
medical decision boundary ya clinically established cut-off nahi samajhna
chahiye. Contribution list model ke log-odds calculation se aati hai; yeh
causal explanation nahi hai aur SHAP explanation bhi nahi hai.

## 6. Tech stack

| Technology | Project mein role |
|---|---|
| Python | Model artifacts load karna, input processing aur API |
| pandas / NumPy | Table data aur numeric computations |
| scikit-learn | Imputation, scaling, one-hot encoding, Logistic Regression aur metrics |
| FastAPI / Uvicorn | Prediction API aur dashboard-serving backend |
| HTML / CSS / JavaScript | Patient form aur results dashboard |
| React | Interactive viewer interface |
| Three.js / React Three Fiber | Browser mein 3D heart render aur controls |
| Vite | Viewer assets ka production build |
| Docker | Viewer build aur Python app ko container mein package karna |
| Render | Public demo ke liye hosted web service |

## 7. Interactive heart visualization

`heart3d/public/models/human_heart.glb` 3D heart asset hai. LAD, LCX, RCA
paths separate interactive tube overlays ke roop mein draw kiye gaye hain.
User drag karke rotate, scroll/pinch se zoom, view buttons se camera preset
change, aur vessel click karke region select kar sakta hai. Optional heartbeat
effect poore heart aur artery group ko halka scale-pulse karta hai; yeh original
heart animation ya biological simulation nahi hai.

**Visualization ki limits:** coronary paths schematic, hand-placed aur
illustrative hain—patient-specific nahi. Color vessel model probability
dikhata hai, lesion ka anatomical location/severity nahi. Source mesh ka front
cut-open hai; artery tube thickness visibility/clickability ke liye exaggerated
hai.

## 8. Evaluation results

Har target ke liye alag stratified holdout set mein 61 records the. Reported
values ek chhote, single 80/20 split ke estimates hain; multiple external
datasets par validation ya clinical trial nahi.

| Target | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| CAD | 80.3% | 89.7% | 81.4% | 85.4% | 89.0% |
| LAD stenosis | 73.8% | 79.4% | 75.0% | 77.1% | 82.9% |
| LCX stenosis | 59.0% | 48.3% | 58.3% | 52.8% | 64.2% |
| RCA stenosis | 72.1% | 63.6% | 60.9% | 62.2% | 73.9% |

**Important:** LCX ka performance khaas taur par weak hai. Accuracy ya
probability ko individual patient ke liye certainty ya diagnosis nahi samajhna
chahiye.

## 9. Live demo aur deployment

Current public demo: <https://cardioscope-i8un.onrender.com/>. Render par
Docker container viewer build aur FastAPI service ko saath run karta hai.
Service free tier par sleep ho sakti hai; inactivity ke baad pehla request
wake-up ke kaaran dheema ho sakta hai.

GitHub Pages par frontend publish karne ki workflow bhi repository mein hai,
lekin Pages-only deployment backend API ko khud nahi chalata. Isliye current
working full application ka shareable link Render demo hi hai.

## 10. 45-second presentation script

> “Hamare project ka naam CardioScope hai. Yeh ek educational prototype hai jo
> clinical features ko input lekar CAD aur teen coronary vessels—LAD, LCX aur
> RCA—ke estimated model probabilities dikhata hai. Humne supplied
> Z-Alizadeh Sani extension dataset ke 303 records use kiye. Target leakage se
> bachne ke liye CAD, LAD, LCX aur RCA labels ko input features se hata kar
> chaar separate class-weighted Logistic Regression models train kiye.
> Missing numeric values median se impute, numeric features standardize, aur
> categorical features most-frequent imputation plus one-hot encoding se
> process hote hain. FastAPI prediction serve karta hai, React Three Fiber
> schematic 3D heart dikhata hai. Yeh research/learning demo hai, diagnosis
> nahi; holdout results chhote dataset par hain aur clinical validation nahi
> hui.”

## 11. Project files ka map

| File/folder | Kaam |
|---|---|
| `train_model.py` | Workbook validation, preprocessing pipeline, evaluation aur model training |
| `app.py` | FastAPI routes, artifact loading aur prediction |
| `index.html` | Main dashboard, form, metrics/results aur viewer iframe |
| `heart3d/src/` | React 3D viewer, vessel paths aur probability display |
| `heart3d/public/models/human_heart.glb` | 3D heart asset |
| `models/prediction_models.joblib` | Trained CAD, LAD, LCX, RCA pipelines |
| `models/schema.json` | Input feature names, types aur category options |
| `models/metrics.json` | Holdout metrics aur evaluation note |
| `Dockerfile`, `render.yaml` | Optional hosted container deployment configuration |

