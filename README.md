# AgileRisk AI — Predictive Risk Management in Agile IT Projects

**MSc IT with Project Management | University of the West of Scotland**
Student: Manfred Oppong | Banner ID: B01814357 | Supervisor: Durfashan Tariq | Year: 2026

---

## 1. Project Overview

AgileRisk AI is a complete research artefact developed as part of an MSc dissertation titled
*"The Role of Artificial Intelligence in Enhancing Predictive Risk Management in Agile IT Projects"*.
The system integrates 19 publicly available datasets — spanning NASA PROMISE software defect
data, open-source Agile Scrum project histories, a 4,000-record project risk dataset, and an
Agile project outcomes dataset — into a unified machine-learning pipeline. A feature engineering
module derives sprint-level risk proxy indicators (velocity variance, completion rate, punt rate,
schedule variance, story-point delta) that serve as inputs to four supervised classifiers:
Logistic Regression, Random Forest, Gradient Boosting, and Support Vector Machine. The best
model is persisted and served through a modern desktop GUI that enables project managers to
enter real-time sprint metrics and receive an instant risk label, probability score, and
actionable recommendation.

The artefact consists of five deliverable files: a Tkinter/ttkbootstrap desktop application
(`App.py`), a standalone feature-engineering and training pipeline (`pipeline.py`), a
one-click Windows EXE builder (`build_exe.py`), a fully annotated Jupyter/Colab analysis
notebook (`AgileProject.ipynb`), and this README. Together they demonstrate that AI can provide
meaningful early-warning signals for sprint failure risk, supporting the dissertation objective
of enhancing predictive risk management in Agile IT environments through machine learning.

---

## 2. File Structure

```
AgileRiskAI/
├── App.py                    — Tkinter GUI application (2,186 lines)
├── pipeline.py               — Feature engineering & ML pipeline (1,682 lines)
├── build_exe.py              — Windows EXE builder via PyInstaller (752 lines)
├── AgileProject.ipynb        — Jupyter notebook: full EDA → training → demo
├── README.md                 — This file
├── requirements.txt          — All Python dependencies (pinned versions)
│
├── best_model.pkl            — Saved best ML model   (generated on first run)
├── scaler.pkl                — Saved feature scaler  (generated on first run)
├── merged_train_data.csv     — Merged training dataset (generated on first run)
│
├── app_icon.ico              — Application icon (optional, place here for EXE)
│
└── datasets/                 — Place your 19 dataset files here (or in root)
    ├── cm1.csv
    ├── pc1.csv
    ├── jm1.csv
    ├── kc1.csv
    ├── kc2.csv
    ├── project_risk_raw_dataset.csv
    ├── Mesos Stories 176.csv
    ├── MESO Issue Summary 370.csv
    ├── MESO Sprint 96.csv
    ├── Spring XD Issues 1992.csv
    ├── Spring XD Issues Summary 2861.csv
    ├── Spring XD Sprints 67.csv
    ├── Aurora Issues 554.csv
    ├── Aurora Issues summery 568.csv
    ├── Aurora Sprints 41.csv
    ├── Usergrid Issues 824.csv
    ├── Usergrid Issues Summary 929.csv
    ├── Usergrid Sprints 36.csv
    └── Agile_Projects_Dataset.xlsx
```

---

## 3. System Requirements

| Requirement     | Minimum                         | Recommended                     |
|-----------------|---------------------------------|---------------------------------|
| Operating System| Windows 10 / macOS 12 / Ubuntu 22 | Windows 11 (for EXE build)     |
| Python Version  | **3.11.9 exactly**              | 3.11.9 (critical for PyInstaller) |
| RAM             | 4 GB                            | 8 GB or more                    |
| Disk Space      | 1 GB free                       | 2 GB free (EXE build needs more) |
| Display         | 1024 × 768                      | 1920 × 1080                     |
| Internet        | For Colab notebook only         | Broadband for initial pip install |

> **⚠ Python version note:** PyInstaller 6.x generates EXE files that are tightly coupled to
> the Python version used at build time. Using Python 3.11.9 ensures maximum compatibility.
> Mismatched versions (e.g. 3.12.x) may produce EXEs that fail to launch on end-user machines.

---

## 4. Step-by-Step Installation Guide (Python 3.11.9)

### Step 1 — Install Python 3.11.9

Download the **exact** installer for your OS:

- **Windows (64-bit):** https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
- **Windows (32-bit):** https://www.python.org/ftp/python/3.11.9/python-3.11.9.exe
- **macOS:**            https://www.python.org/ftp/python/3.11.9/python-3.11.9-macos11.pkg
- **All downloads:**    https://www.python.org/downloads/release/python-3119/

**Windows installation checklist** (in the installer wizard):

1. ☑ **Add Python 3.11 to PATH** — tick this checkbox on the first screen
2. Click **Customise Installation**
3. ☑ pip
4. ☑ tcl/tk and IDLE  ← **required for tkinter**
5. ☑ Python test suite
6. ☑ py launcher
7. Click **Next → Install**

Verify installation:

```bash
python --version
# Expected output: Python 3.11.9

python -c "import tkinter; print('tkinter OK')"
# Expected output: tkinter OK
```

---

### Step 2 — Create a Virtual Environment (Recommended)

Using a virtual environment isolates AgileRisk AI's dependencies from your system Python.

```bash
# Navigate to the project folder
cd path\to\AgileRiskAI

# Create the environment
python -m venv agilerisk_env

# Activate (Windows)
agilerisk_env\Scripts\activate

# Activate (macOS / Linux)
source agilerisk_env/bin/activate

# Confirm activation — prompt should show (agilerisk_env)
python --version
```

To deactivate later:

```bash
deactivate
```

---

### Step 3 — Upgrade pip

```bash
python -m pip install --upgrade pip
```

Expected output: `Successfully installed pip 24.x.x`

---

### Step 4 — Install All Required Libraries

The exact `requirements.txt` content is:

```text
ttkbootstrap==1.10.1
scikit-learn==1.3.2
pandas==2.0.3
numpy==1.24.4
matplotlib==3.7.3
seaborn==0.12.2
joblib==1.3.2
openpyxl==3.1.2
imbalanced-learn==0.11.0
xgboost==2.0.3
pyinstaller==6.3.0
scipy==1.11.4
Pillow==10.0.0
```

Create `requirements.txt` with the above content, then install:

```bash
pip install -r requirements.txt
```

Typical install time: 2–5 minutes depending on internet speed.

Verify key imports after installation:

```bash
python -c "import ttkbootstrap; import sklearn; import pandas; import joblib; print('All OK')"
```

---

### Step 5 — Known Compatibility Issues and Fixes for Python 3.11.9

The following issues are known to affect some Python 3.11.9 environments and are documented
here with their exact resolutions:

#### 5a. `ttkbootstrap` PIL / Pillow dependency error

**Symptom:** `ImportError: cannot import name 'ANTIALIAS' from 'PIL.Image'`

**Cause:** ttkbootstrap 1.10.x was written against Pillow < 10.0; Pillow 10.0 removed
`Image.ANTIALIAS`.

**Fix:**

```bash
pip install Pillow==10.0.0
```

If the error persists, patch ttkbootstrap manually:

```python
# In your Python environment, find ttkbootstrap's style.py and replace:
# Image.ANTIALIAS  →  Image.LANCZOS
```

---

#### 5b. `scikit-learn` Cython import error

**Symptom:** `ImportError: cannot import name '_weight_vector' from 'sklearn.utils'`

**Fix:**

```bash
pip install --upgrade scikit-learn==1.3.2
```

If the binary wheel is unavailable for your platform:

```bash
pip install scikit-learn==1.3.2 --no-binary scikit-learn
```

---

#### 5c. NumPy 2.x incompatibility

**Symptom:** `AttributeError: module 'numpy' has no attribute 'bool'` or similar.

**Cause:** NumPy 2.0 removed several deprecated aliases (`np.bool`, `np.int`, `np.float`)
that scikit-learn 1.3.x still references internally.

**Fix:** The `requirements.txt` already pins `numpy==1.24.4` (NumPy 1.x). If you have
NumPy 2.x installed from a different project, run:

```bash
pip install "numpy<2.0"
```

---

#### 5d. PyInstaller hook for scikit-learn

**Symptom:** EXE launches but crashes with `ModuleNotFoundError: sklearn.*` at runtime.

**Cause:** PyInstaller cannot automatically detect all sklearn Cython extension modules.

**Fix:**

```bash
pip install pyinstaller-hooks-contrib
```

Then rebuild:

```bash
python build_exe.py --clean
python build_exe.py
```

---

#### 5e. `tkinter` missing on Linux / macOS

**Symptom:** `ModuleNotFoundError: No module named '_tkinter'`

**Cause:** Linux/macOS Python installations often omit tkinter from the default package.

**Fix (Ubuntu/Debian):**

```bash
sudo apt-get update
sudo apt-get install python3-tk python3.11-tk
```

**Fix (Fedora/RHEL):**

```bash
sudo dnf install python3-tkinter
```

**Fix (macOS with Homebrew):**

```bash
brew install python-tk@3.11
```

**Fix (macOS — reinstall Python):**
Download the official Python 3.11.9 installer from python.org (not Homebrew); it bundles
the correct Tcl/Tk 8.6 version.

---

#### 5f. `openpyxl` required for Excel files

**Symptom:** `ValueError: Missing optional dependency 'openpyxl'. Use pip or conda to install openpyxl.`

**Cause:** pandas requires `openpyxl` to read `.xlsx` files but does not install it automatically.

**Fix:** Already included in `requirements.txt`. If missing:

```bash
pip install openpyxl==3.1.2
```

---

#### 5g. PyInstaller `RecursionError` during EXE build

**Symptom:** `RecursionError: maximum recursion depth exceeded` during PyInstaller analysis.

**Fix:** `App.py` already contains `sys.setrecursionlimit(5000)` at the top of the file.
If the error persists, increase the limit in `App.py`:

```python
import sys
sys.setrecursionlimit(8000)
```

---

#### 5h. `matplotlib` TkAgg backend error in App.py

**Symptom:** `ImportError: cannot import name 'FigureCanvasTkAgg'`

**Cause:** matplotlib backend not set before import.

**Fix:** `pipeline.py` already calls `matplotlib.use("Agg")` before any other matplotlib
import. In `App.py`, `matplotlib.use("TkAgg")` is called before pyplot is imported.
Ensure no other module calls `import matplotlib.pyplot` before these lines execute.

---

### Step 6 — Running the Jupyter Notebook (Google Colab)

The Jupyter notebook `AgileProject.ipynb` is designed for **Google Colab** with Python 3.11.9.

```
1. Open a browser and go to: https://colab.research.google.com
2. Click File → Upload notebook
3. Select AgileProject.ipynb from your local machine
4. Upload your dataset files:
   a. Click the 📁 Files icon in the left sidebar
   b. Click the upload button (↑ icon)
   c. Upload all 19 dataset CSV/XLSX files to /content/
   d. Alternatively, upload a single ZIP of all files — Cell 2 auto-extracts ZIPs
5. Run all cells: Runtime → Run all  (or Ctrl+F9)
```

> **Python version note for Colab:** Google Colab currently uses Python 3.10.x by default.
> The notebook is compatible with Python 3.10+ but was developed and tested on 3.11.9.
> To check the Colab version: add `!python --version` in any cell.
> All `!pip install` commands in Cell 1 will upgrade packages to compatible versions.

**Estimated runtime:** 10–20 minutes for all 15 cells (depends on Colab instance type).
GPU runtime is not required — all models are CPU-based.

---

### Step 7 — Running the Desktop Application

```bash
# Make sure the virtual environment is active
agilerisk_env\Scripts\activate     # Windows
source agilerisk_env/bin/activate  # macOS/Linux

# Navigate to the project folder
cd path\to\AgileRiskAI

# Launch the GUI
python App.py
```

**First-time use workflow:**

1. **Load Data** — click "Scan Script Directory" to auto-load all CSVs in the project folder
2. **Feature Engineering** — click "Run Pipeline" to engineer sprint features and build `merged_train_data.csv`
3. **Train Model** — select algorithms and click "Train Selected Models"
4. **Evaluation** — click "Refresh Results" to view metrics, confusion matrices
5. **Risk Predictor** — enter sprint metrics or click a demo scenario button

If `best_model.pkl` and `scaler.pkl` already exist in the project folder (from a previous
training run or the Colab notebook), the app loads them automatically on startup and you
can use the Risk Predictor immediately.

---

### Step 8 — Running the Pipeline Standalone

```bash
# Default: scans /content (Colab) or falls back to script directory
python pipeline.py

# Custom directories
python pipeline.py --base-dir C:\Data\AgileRiskAI --output-dir C:\Data\AgileRiskAI\outputs

# Train only specific models (skip slow SVC)
python pipeline.py --skip-svc

# Train only selected models
python pipeline.py --models "Logistic Regression" "Random Forest"
```

**Expected outputs in the output directory:**

| File                      | Description                                      |
|---------------------------|--------------------------------------------------|
| `merged_train_data.csv`   | Merged feature matrix (all groups combined)      |
| `best_model.pkl`          | Best classifier (highest weighted F1 on test set)|
| `scaler.pkl`              | StandardScaler fitted on training set            |
| `confusion_matrices.png`  | Seaborn heatmap grid for all trained models      |
| `roc_curves.png`          | Overlaid ROC curves (binary classification)      |
| `feature_importance_rf.png`| Random Forest top-20 feature importances        |
| `learning_curves.png`     | LR + GB training vs validation log-loss curves   |

---

### Step 9 — Building the Windows EXE

Ensure you are on a Windows machine with Python 3.11.9 and all dependencies installed.

```bash
# Full build
python build_exe.py

# Check environment only (no build)
python build_exe.py --check-only

# Clean previous build artefacts
python build_exe.py --clean

# Clean without confirmation prompt
python build_exe.py --clean --no-confirm
```

**Expected output:** `dist\AgileRisk_AI.exe`

**Build time:** Approximately 3–8 minutes depending on hardware.

**Post-build — copy required files to dist/ before distributing:**

```batch
xcopy best_model.pkl   dist\  /Y
xcopy scaler.pkl       dist\  /Y
```

> **Antivirus false positive warning:** Windows Defender and other antivirus tools sometimes
> flag PyInstaller EXEs as suspicious because they self-extract a Python runtime into a
> temporary folder at launch (a common technique used by legitimate and malicious software
> alike). If you see a Defender SmartScreen warning:
>
> 1. Click **More info**
> 2. Click **Run anyway**
>
> To permanently whitelist: Windows Security → Virus & Threat Protection →
> Manage Settings → Exclusions → Add an exclusion → File → select `AgileRisk_AI.exe`.

---

### Step 10 — Running the EXE on a Target Machine

1. Copy the entire `dist\` folder to the target machine
2. Ensure `best_model.pkl` and `scaler.pkl` are in the same folder as the EXE
3. Double-click `AgileRisk_AI.exe`
4. No Python installation is required on the target machine

**Minimum target machine requirements:**

- Windows 10 version 1903 or later (64-bit)
- 200 MB free disk space (for temp files at runtime)
- 2 GB RAM
- Display resolution: 1024 × 768 minimum

---

## 5. Dataset Sources

All datasets used in this project are publicly available from academic repositories.

| Variable Name                  | File                               | Records | Source / URL                                                                 |
|--------------------------------|------------------------------------|---------|------------------------------------------------------------------------------|
| `cm1`                          | cm1.csv                            | 498     | NASA PROMISE Repository — https://promise.site.uottawa.ca/SERepository/        |
| `pc1`                          | pc1.csv                            | 1,109   | NASA PROMISE Repository — https://promise.site.uottawa.ca/SERepository/        |
| `jm1`                          | jm1.csv                            | 13,204  | NASA PROMISE Repository — https://promise.site.uottawa.ca/SERepository/        |
| `kc1`                          | kc1.csv                            | 2,109   | NASA PROMISE Repository — https://promise.site.uottawa.ca/SERepository/        |
| `kc2`                          | kc2.csv                            | 522     | NASA PROMISE Repository — https://promise.site.uottawa.ca/SERepository/        |
| `project_risk_raw_dataset`     | project_risk_raw_dataset.csv       | 4,000   | Kaggle — https://www.kaggle.com/datasets/                                       |
| `Mesos_Stories_176`            | Mesos Stories 176.csv              | 176     | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `MESO_Issue_Summary_370`       | MESO Issue Summary 370.csv         | 374     | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `MESO_Sprint_96`               | MESO Sprint 96.csv                 | 96      | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Spring_XD_Issues_1992`        | Spring XD Issues 1992.csv          | 1,992   | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Spring_XD_Issues_Summary_2861`| Spring XD Issues Summary 2861.csv  | 2,861   | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Spring_XD_Sprints_67`         | Spring XD Sprints 67.csv           | 66      | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Aurora_Issues_554`            | Aurora Issues 554.csv              | 554     | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Aurora_Issues_summery_568`    | Aurora Issues summery 568.csv      | 568     | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Aurora_Sprints_41`            | Aurora Sprints 41.csv              | 40      | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Usergrid_Issues_824`          | Usergrid Issues 824.csv            | 824     | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Usergrid_Issues_Summary_929`  | Usergrid Issues Summary 929.csv    | 929     | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Usergrid_Sprints_36`          | Usergrid Sprints 36.csv            | 38      | Tawosi et al. (2022) — https://doi.org/10.5281/zenodo.6369121                  |
| `Agile_Projects_Dataset`       | Agile_Projects_Dataset.xlsx        | 200     | Kaggle — https://www.kaggle.com/datasets/                                       |

> The four Agile Scrum datasets (Mesos, Spring XD, Aurora, Usergrid) originate from the
> **Tawosi et al. (2022)** Zenodo archive of open-source Jira project histories. The exact DOI
> is: https://doi.org/10.5281/zenodo.6369121

---

## 6. Troubleshooting

### General

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: ttkbootstrap` | Package not installed | `pip install ttkbootstrap==1.10.1` |
| `No module named _tkinter` | Python installed without Tcl/Tk | Reinstall Python 3.11.9 with **tcl/tk** option ticked; on Linux: `sudo apt-get install python3-tk` |
| `FileNotFoundError: best_model.pkl` | Pipeline not yet run | Run `python pipeline.py` or train from the App's **Train Model** tab |
| `FileNotFoundError: scaler.pkl` | Scaler not saved | Run the pipeline; scaler is saved alongside best_model.pkl |
| `KeyError` on column name in notebook | Dataset not loaded / wrong CSV | Re-run Cell 2 to reload all datasets |
| `ValueError: could not convert string to float` | Non-numeric data in feature column | Ensure kc2.csv target is encoded (run Cell 8 which calls `prepare_nasa_datasets`) |
| `MemoryError` during jm1 load | jm1 has 13,204 rows; 4 GB RAM may be tight | Close other applications; use `pd.read_csv(..., chunksize=5000)` if needed |

### PyInstaller / EXE Build

| Error | Cause | Fix |
|---|---|---|
| `RecursionError` during build | PyInstaller analysis recursion limit | `App.py` already sets `sys.setrecursionlimit(5000)`; increase to 8000 if needed |
| EXE crashes on launch | Missing hidden imports | Run `pip install pyinstaller-hooks-contrib` then rebuild |
| EXE shows blank window | ttkbootstrap theme not bundled | Ensure `collect_submodules('ttkbootstrap')` is in the spec (already included) |
| `ModuleNotFoundError: sklearn.*` at EXE runtime | sklearn Cython modules not bundled | `pip install pyinstaller-hooks-contrib` and rebuild |
| Antivirus blocks EXE | False positive (self-extractor pattern) | Whitelist the EXE file in Windows Security settings |
| EXE file > 200 MB | Normal for bundled Python + ML libraries | Use UPX compression: already enabled in spec (`upx=True`) |
| `OSError: [WinError 193]` | 32-bit Python used for 64-bit dependencies | Rebuild using 64-bit Python 3.11.9 |

### Colab Notebook

| Error | Cause | Fix |
|---|---|---|
| `FileNotFoundError: cm1.csv` | Dataset not uploaded to /content | Upload all CSV files via the Files panel in Colab sidebar |
| `KeyError: 'defects'` | kc2.csv target column is 'problems' | Normal — Cell 8 handles this. Re-run Cell 8 if the error persists |
| `ImportError: No module named openpyxl` | openpyxl not installed in Colab session | Add `!pip install openpyxl` before the load cell |
| Session disconnects during training | Colab free tier has 12-hour session limit | Use Colab Pro or save intermediate results with `joblib.dump()` |
| Plots not showing | matplotlib backend issue | Add `%matplotlib inline` in a cell before the plot cells |
| `KeyboardInterrupt` during SVC training | SVC is slow on large datasets | Skip SVC or reduce dataset size; SVC checkbox is unticked by default in App.py |

### App.py (Desktop GUI)

| Error | Cause | Fix |
|---|---|---|
| GUI window too small / clipped | Display scaling > 100% | Set Windows display scaling to 100–125% |
| Sidebar text invisible | Dark theme + system colour override | Switch theme in the Settings panel |
| Pipeline log shows nothing | Thread not started | Click the "Run Pipeline" button (not just browse) |
| Risk Predictor always shows "No Model" | best_model.pkl not in script dir | Copy best_model.pkl from outputs/ to the same folder as App.py |
| Confusion matrix blank | Models not yet evaluated | Click "Refresh Results" after training completes |
| App freezes during training | Training running in main thread | Re-install App.py from the repository — the threaded version should be used |

---

## 7. Academic References

All references use Harvard citation format as per UWS academic guidelines.

1. Ahmadi, S. and Osman, A. (2022) 'A review of machine learning applications for software
   defect prediction', *Journal of Software: Evolution and Process*, 34(5), e2448.
   doi:10.1002/smr.2448

2. Campanelli, A. and Parrella, F. (2015) 'A systematic review of success factors and barriers
   for scaling agile', *Journal of Systems and Software*, 107, pp. 106–127.
   doi:10.1016/j.jss.2015.05.019

3. Crispin, L. and Gregory, J. (2009) *Agile Testing: A Practical Guide for Testers and Agile
   Teams*. Boston: Addison-Wesley.

4. Elish, M.O. and Elish, H.O. (2008) 'Predicting defect-prone software modules using support
   vector machines', *Journal of Systems and Software*, 81(5), pp. 649–660.
   doi:10.1016/j.jss.2007.07.040

5. Garg, S. and Gupta, S. (2022) 'Risk identification and mitigation in agile projects using
   machine learning', *International Journal of Advanced Computer Science and Applications*,
   13(4), pp. 312–321. doi:10.14569/IJACSA.2022.0130437

6. Madachy, R.J. (2008) *Software Process Dynamics*. Hoboken, NJ: Wiley-IEEE Press.

7. Menzies, T., Greenwald, J. and Frank, A. (2007) 'Data mining static code attributes to
   learn defect predictors', *IEEE Transactions on Software Engineering*, 33(1), pp. 2–13.
   doi:10.1109/TSE.2007.256941

8. Pedregosa, F., Varoquaux, G., Gramfort, A. et al. (2011) 'Scikit-learn: machine learning
   in Python', *Journal of Machine Learning Research*, 12, pp. 2825–2830.
   Available at: https://jmlr.org/papers/v12/pedregosa11a.html [Accessed 10 Jan 2026]

9. Schwaber, K. and Sutherland, J. (2020) *The Scrum Guide: The Definitive Guide to Scrum:
   The Rules of the Game*. Available at: https://scrumguides.org/scrum-guide.html
   [Accessed 5 Jan 2026]

10. Tawosi, V., Al-Subaihin, A., Sarro, F. and Harman, M. (2022) 'A replication study on the
    relationship between agile velocity and story points', in *Proceedings of the 16th
    ACM/IEEE International Symposium on Empirical Software Engineering and Measurement
    (ESEM 2022)*. New York: ACM, pp. 1–12. doi:10.5281/zenodo.6369121

---

## 8. Licence

```
MIT Licence

Copyright (c) 2026 Manfred Oppong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> **Academic use:** This artefact was produced as a dissertation submission for the
> MSc IT with Project Management programme at the University of the West of Scotland (2026).
> It is made available for academic reference and peer review. Commercial deployment without
> the express written consent of the author is not permitted under the terms of this licence.

---

*Generated by AgileRisk AI build system — Python 3.11.9 | UWS 2026*
