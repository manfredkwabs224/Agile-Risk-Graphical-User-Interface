                                                                               
                                                                     
                                                                     
                                                  
                                          
                   
 
                               
                                
                                                                        
                                                                                 
                                                                            
                                                                                 
                                                                           
                                                                               

import os, sys, time, queue, logging, zipfile, pathlib
import threading, datetime, tempfile, traceback

sys.setrecursionlimit(5000)

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    TTKBOOTSTRAP = True
except ImportError:
    import tkinter.ttk as ttk
    TTKBOOTSTRAP = False

import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import numpy as np;   NUMPY_OK = True
except ImportError:       NUMPY_OK = False
try:
    import pandas as pd;  PANDAS_OK = True
except ImportError:       PANDAS_OK = False
try:
    import joblib;        JOBLIB_OK = True
except ImportError:       JOBLIB_OK = False
try:
    import matplotlib; matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except ImportError:       MATPLOTLIB_OK = False
try:
    import seaborn as sns; SEABORN_OK = True
except ImportError:        SEABORN_OK = False
try:
    from sklearn.linear_model  import LogisticRegression
    from sklearn.ensemble      import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.svm           import SVC
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                                  f1_score, roc_auc_score, confusion_matrix,
                                  classification_report)
    SKLEARN_OK = True
except ImportError:        SKLEARN_OK = False

                                                                               
           
                                                                               

APP_TITLE    = "AgileRisk AI — Predictive Risk Management System"
APP_MIN_W    = 1100
APP_MIN_H    = 680
SIDEBAR_W    = 210
DEFAULT_THEME = "cosmo"

C_SIDEBAR_BG     = "#1E3A5F"
C_SIDEBAR_TEXT   = "#FFFFFF"
C_SIDEBAR_ACTIVE = "#F0A500"
C_MAIN_BG        = "#F4F6F9"
C_CARD_BG        = "#FFFFFF"
C_CARD_BORDER    = "#E0E0E0"
C_BTN_GREEN      = "#2ECC71"
C_BTN_RED        = "#E74C3C"
C_BTN_BLUE       = "#3498DB"
C_TEXT_DARK      = "#2C3E50"
C_TEXT_MUTED     = "#7F8C8D"

RISK_COLOURS = {
    "Low":      "#2ECC71",
    "Medium":   "#F0A500",
    "High":     "#E67E22",
    "Critical": "#E74C3C",
    "At Risk":  "#E67E22",
    "Unknown":  C_TEXT_MUTED,
}

RISK_RECOMMENDATIONS = {
    "Low":      "Sprint is on track. Monitor velocity weekly.",
    "Medium":   "Caution: review backlog and re-estimate story points.",
    "High":     "Intervention needed: escalate to project manager and re-plan sprint.",
    "Critical": "Sprint in crisis: halt new work, conduct emergency retrospective.",
    "At Risk":  "Sprint showing risk signals: review completion rate and punt rate.",
    "Unknown":  "Train a model first before making predictions.",
}

BASE_DIR    = pathlib.Path(__file__).parent.resolve()
MODEL_PATH  = BASE_DIR / "best_model.pkl"
SCALER_PATH = BASE_DIR / "scaler.pkl"
MERGED_CSV  = BASE_DIR / "merged_train_data.csv"

AVAILABLE_THEMES = [
    "cosmo","flatly","litera","minty","pulse","sandstone",
    "united","yeti","darkly","superhero","solar","cyborg","vapor",
]

                                                                               
         
                                                                               

def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _card(parent, **kw):
    return tk.Frame(parent, bg=C_CARD_BG,
                    highlightbackground=C_CARD_BORDER,
                    highlightthickness=1, **kw)

def _lbl(parent, text, size=10, bold=False, color=C_TEXT_DARK,
         bg=C_CARD_BG, **kw):
    w = "bold" if bold else "normal"
    return tk.Label(parent, text=text, font=("Segoe UI", size, w),
                    fg=color, bg=bg, **kw)

def _btn(parent, text, cmd, color=C_BTN_BLUE, fg="#FFF", width=18, **kw):
    return tk.Button(parent, text=text, command=cmd,
                     bg=color, fg=fg, activebackground=color,
                     activeforeground=fg, font=("Segoe UI", 10, "bold"),
                     relief="flat", cursor="hand2",
                     padx=10, pady=6, width=width, **kw)


                                                                               
                
                                                                               

class SidebarButton(tk.Frame):
    def __init__(self, parent, text, icon, command, **kw):
        super().__init__(parent, bg=C_SIDEBAR_BG, cursor="hand2", **kw)
        self._cmd    = command
        self._active = False
        self._bar    = tk.Frame(self, bg=C_SIDEBAR_BG, width=4)
        self._bar.place(x=0, y=0, relheight=1, width=4)
        self._icon = tk.Label(self, text=icon, bg=C_SIDEBAR_BG,
                               fg=C_SIDEBAR_TEXT, font=("Segoe UI", 12))
        self._icon.pack(side="left", padx=(14, 5), pady=9)
        self._text = tk.Label(self, text=text, bg=C_SIDEBAR_BG,
                               fg=C_SIDEBAR_TEXT, font=("Segoe UI", 10),
                               anchor="w")
        self._text.pack(side="left", fill="x", expand=True)
        for w in (self, self._icon, self._text):
            w.bind("<Button-1>", lambda _e: self._cmd())
            w.bind("<Enter>",    self._hover_on)
            w.bind("<Leave>",    self._hover_off)

    def set_active(self, v):
        self._active = v
        bg  = "#254B77" if v else C_SIDEBAR_BG
        fgc = C_SIDEBAR_ACTIVE if v else C_SIDEBAR_TEXT
        fw  = "bold" if v else "normal"
        self._bar.config(bg=C_SIDEBAR_ACTIVE if v else C_SIDEBAR_BG)
        for w in (self, self._icon, self._text):
            w.config(bg=bg)
        self._text.config(fg=fgc, font=("Segoe UI", 10, fw))
        self._icon.config(fg=fgc)

    def _hover_on(self, _=None):
        if not self._active:
            for w in (self, self._icon, self._text):
                w.config(bg="#243F68")

    def _hover_off(self, _=None):
        if not self._active:
            for w in (self, self._icon, self._text):
                w.config(bg=C_SIDEBAR_BG)


                                                                               
             
                                                                               

class MetricCard(tk.Frame):
    def __init__(self, parent, title, value, subtitle="", accent=C_BTN_BLUE, **kw):
        super().__init__(parent, bg=C_CARD_BG,
                         highlightbackground=C_CARD_BORDER,
                         highlightthickness=1, **kw)
        tk.Frame(self, bg=accent, height=4).pack(fill="x")
        inner = tk.Frame(self, bg=C_CARD_BG, padx=14, pady=10)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=title.upper(), bg=C_CARD_BG, fg=C_TEXT_MUTED,
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill="x")
        self._vl = tk.Label(inner, text=value, bg=C_CARD_BG, fg=accent,
                             font=("Segoe UI", 26, "bold"), anchor="w")
        self._vl.pack(fill="x", pady=(3, 1))
        self._sl = tk.Label(inner, text=subtitle, bg=C_CARD_BG, fg=C_TEXT_MUTED,
                             font=("Segoe UI", 9), anchor="w")
        self._sl.pack(fill="x")

    def update(self, value, subtitle=""):
        self._vl.config(text=value)
        if subtitle:
            self._sl.config(text=subtitle)


                                                                               
            
                                                                               

class BasePanel(tk.Frame):
    def __init__(self, parent, title, subtitle="", **kw):
        super().__init__(parent, bg=C_MAIN_BG, **kw)
        hdr = tk.Frame(self, bg=C_MAIN_BG, padx=24, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg=C_MAIN_BG, fg=C_TEXT_DARK,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, bg=C_MAIN_BG, fg=C_TEXT_MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(1, 0))
        tk.Frame(self, bg=C_CARD_BORDER, height=1).pack(fill="x")

    def _scrollable_body(self):
        container = tk.Frame(self, bg=C_MAIN_BG)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=C_MAIN_BG, highlightthickness=0)
        vsb    = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C_MAIN_BG)
        wid   = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _cfg(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(wid, width=canvas.winfo_width())

        inner.bind("<Configure>", _cfg)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))

        def _mw(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _mw)
        return inner


                                                                               
                     
                                                                               

class DashboardPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Dashboard",
                         "Overview of your AgileRisk AI workspace", **kw)
        self._app   = app
        self._cards = {}
        self._build()

    def _build(self):
        body = self._scrollable_body()

        banner = tk.Frame(body, bg="#1E3A5F", padx=22, pady=18)
        banner.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(banner, text="🚀  Welcome to AgileRisk AI",
                 bg="#1E3A5F", fg="#FFFFFF",
                 font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(banner,
                 text="AI-Enhanced Predictive Risk Management for Agile IT Projects\n"
                      "Load datasets → engineer features → train models → predict sprint risk.",
                 bg="#1E3A5F", fg="#B0C4DE", font=("Segoe UI", 10),
                 justify="left").pack(anchor="w", pady=(5, 0))

        cf = tk.Frame(body, bg=C_MAIN_BG)
        cf.pack(fill="x", padx=20, pady=8)
        defs = [("datasets", "Datasets Loaded",    "0", "CSV / XLSX files",    C_BTN_BLUE),
                ("records",  "Total Records",       "0", "Across all datasets", C_BTN_GREEN),
                ("features", "Features Engineered", "0", "After pipeline run",  "#E67E22"),
                ("models",   "Models Trained",      "0", "Best saved to disk",  "#9B59B6")]
        for i, (k, t, v, s, a) in enumerate(defs):
            card = MetricCard(cf, title=t, value=v, subtitle=s, accent=a)
            card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
            cf.columnconfigure(i, weight=1)
            self._cards[k] = card

                     
        gc = _card(body); gc.pack(fill="x", padx=20, pady=8)
        _lbl(gc, "  Quick-Start Guide", 12, bold=True).pack(anchor="w", pady=(10, 4))
        steps = [
            ("1", "Load Data",           "Browse or scan your ZIP/CSV dataset files."),
            ("2", "Feature Engineering", "Run the sprint risk feature pipeline."),
            ("3", "Train Model",         "Select classifiers and train on merged data."),
            ("4", "Evaluation",          "Review metrics, confusion matrices, ROC curves."),
            ("5", "Risk Predictor",       "Enter sprint metrics for instant risk assessment."),
        ]
        for num, st, desc in steps:
            r = tk.Frame(gc, bg=C_CARD_BG, padx=18, pady=5); r.pack(fill="x")
            tk.Label(r, text=num, bg=C_BTN_BLUE, fg="white",
                     font=("Segoe UI", 9, "bold"), width=2).pack(side="left", padx=(0, 10))
            tk.Label(r, text=f"{st}: ", bg=C_CARD_BG, fg=C_TEXT_DARK,
                     font=("Segoe UI", 10, "bold")).pack(side="left")
            tk.Label(r, text=desc, bg=C_CARD_BG, fg=C_TEXT_MUTED,
                     font=("Segoe UI", 10)).pack(side="left")

                       
        sc = _card(body); sc.pack(fill="x", padx=20, pady=8)
        _lbl(sc, "  System Status", 11, bold=True, bg=C_CARD_BG).pack(
            anchor="w", pady=(10, 4))
        deps = [("pandas", PANDAS_OK), ("numpy", NUMPY_OK),
                ("scikit-learn", SKLEARN_OK), ("matplotlib", MATPLOTLIB_OK),
                ("seaborn", SEABORN_OK), ("joblib", JOBLIB_OK),
                ("ttkbootstrap", TTKBOOTSTRAP)]
        df2 = tk.Frame(sc, bg=C_CARD_BG, padx=14, pady=6)
        df2.pack(fill="x")
        for ci, (lib, ok) in enumerate(deps):
            tk.Label(df2, text=f"{'✅' if ok else '❌'} {lib}",
                     bg=C_CARD_BG, fg=C_BTN_GREEN if ok else C_BTN_RED,
                     font=("Segoe UI", 9)).grid(
                row=ci // 4, column=ci % 4, sticky="w", padx=10, pady=2)
        tk.Frame(sc, bg=C_CARD_BG, height=8).pack()

    def refresh(self, datasets_count, records, features, models):
        self._cards["datasets"].update(str(datasets_count))
        self._cards["records"].update(f"{records:,}")
        self._cards["features"].update(str(features))
        self._cards["models"].update(str(models))


                                                                               
                                                  
                                                                               

class LoadDataPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Load Data",
                         "Import CSV, XLSX, or ZIP files into the workspace", **kw)
        self._app        = app
        self._build()

    def _build(self):
        body = self._scrollable_body()

        bc = _card(body); bc.pack(fill="x", padx=20, pady=(18, 8))
        _lbl(bc, "  Import Files", 12, bold=True).pack(anchor="w", pady=(10, 4))

        br = tk.Frame(bc, bg=C_CARD_BG, padx=14, pady=8); br.pack(fill="x")

                                                                                
        _btn(br, "📂  Browse Files (multi-select)",
             self._browse_files, color=C_BTN_BLUE, width=24).pack(
            side="left", padx=(0, 10))
        _btn(br, "📁  Scan /content",
             self._scan_content, color="#9B59B6", width=16).pack(
            side="left", padx=(0, 10))
        _btn(br, "🔄  Scan Script Dir",
             self._scan_script, color=C_BTN_GREEN, width=16).pack(side="left")

        self._info_var = tk.StringVar(value="No files selected.")
        tk.Label(bc, textvariable=self._info_var, bg=C_CARD_BG, fg=C_TEXT_MUTED,
                 font=("Segoe UI", 9), padx=14).pack(anchor="w", pady=(0, 6))

             
        lc = _card(body); lc.pack(fill="x", padx=20, pady=8)
        _lbl(lc, "  Extraction / Scan Log", 11, bold=True).pack(anchor="w", pady=(10, 4))
        self._log_text = tk.Text(lc, height=6, state="disabled",
                                  bg="#F8F9FA", fg=C_TEXT_DARK,
                                  font=("Consolas", 9), relief="flat",
                                  padx=8, pady=6)
        self._log_text.pack(fill="x", padx=14, pady=(0, 10))

               
        tc = _card(body); tc.pack(fill="both", expand=True, padx=20, pady=8)
        _lbl(tc, "  Loaded Datasets", 12, bold=True).pack(anchor="w", pady=(10, 4))
        cols = ("Name", "Rows", "Columns", "Nulls", "Path")
        self._tree = ttk.Treeview(tc, columns=cols, show="headings", height=14)
        for col in cols:
            self._tree.heading(col, text=col)
            w = 80 if col in ("Rows", "Columns", "Nulls") else (300 if col == "Path" else 180)
            self._tree.column(col, width=w, minwidth=60)
        vsb = ttk.Scrollbar(tc, orient="vertical",   command=self._tree.yview)
        hsb = ttk.Scrollbar(tc, orient="horizontal",  command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True, padx=14, pady=(0, 10))

                                                                                

    def _log(self, msg):
        self._log_text.configure(state="normal")
        self._log_text.insert(tk.END, f"[{_now()}] {msg}\n")
        self._log_text.see(tk.END)
        self._log_text.configure(state="disabled")

                                                                                
    def _browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Select one or more dataset files",
            filetypes=[
                ("All supported", "*.csv *.xlsx *.zip"),
                ("CSV files",     "*.csv"),
                ("Excel files",   "*.xlsx"),
                ("ZIP archives",  "*.zip"),
            ],
        )
        if not paths:
            return
        self._log(f"Selected {len(paths)} file(s).")
        for path_str in paths:
            path = pathlib.Path(path_str)
            if path.suffix.lower() == ".zip":
                self._extract_zip(path)
            else:
                self._load_file(path)

    def _extract_zip(self, zip_path):
        self._log(f"Extracting ZIP: {zip_path.name}")
        try:
            extract_dir = pathlib.Path(tempfile.mkdtemp(prefix="agilerisk_"))
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)
            self._log(f"Extracted to: {extract_dir}")
            found = list(extract_dir.rglob("*.csv")) + list(extract_dir.rglob("*.xlsx"))
            self._log(f"Found {len(found)} data files inside ZIP.")
            for f in found:
                self._load_file(f, silent=True)
            self._log("✅ ZIP extraction complete.")
        except zipfile.BadZipFile:
            self._log(f"⚠  Not a valid ZIP file: {zip_path.name}")
        except Exception as e:
            self._log(f"❌ ZIP error: {e}")

    def _load_file(self, path, silent=False):
        if not PANDAS_OK:
            messagebox.showerror("Missing", "pandas required.")
            return
        try:
            df = (pd.read_excel(path) if path.suffix.lower() == ".xlsx"
                  else pd.read_csv(path, low_memory=False))
            name  = path.stem
            nulls = int(df.isnull().sum().sum())
            self._tree.insert("", "end",
                               values=(name, df.shape[0], df.shape[1], nulls, str(path)))
            if not silent:
                self._log(f"Loaded: {path.name}  {df.shape[0]:,}r × {df.shape[1]}c")
            self._info_var.set(
                f"Last loaded: {path.name} — {df.shape[0]:,} rows × {df.shape[1]} cols")
            self._app.register_dataset(name, df)
        except Exception as e:
            msg = f"❌ {path.name}: {e}"
            self._log(msg)
            if not silent:
                messagebox.showerror("Load Error", msg)

    def _scan_dir(self, directory):
        self._log(f"Scanning: {directory}")
        d = pathlib.Path(directory)
        if not d.exists():
            self._log(f"⚠  Not found: {directory}"); return
        files = []
        for root, dirs, fnames in os.walk(d):
            dirs[:] = [x for x in dirs if not x.startswith(".") and x != "__MACOSX"]
            for fn in fnames:
                if pathlib.Path(fn).suffix.lower() in (".csv", ".xlsx"):
                    files.append(pathlib.Path(root) / fn)
        self._log(f"Found {len(files)} files.")
        for f in files:
            self._load_file(f, silent=True)
        self._log("✅ Scan complete.")

    def _scan_content(self):  self._scan_dir("/content")
    def _scan_script(self):   self._scan_dir(BASE_DIR)


                                                                               
                        
                                                                               

class DataPreviewPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Data Preview",
                         "Inspect the first 20 rows of any loaded dataset", **kw)
        self._app = app
        self._build()

    def _build(self):
        ctrl = tk.Frame(self, bg=C_MAIN_BG, padx=20, pady=10)
        ctrl.pack(fill="x")
        tk.Label(ctrl, text="Dataset:", bg=C_MAIN_BG, fg=C_TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self._dsv = tk.StringVar(value="— none —")
        self._menu = ttk.Combobox(ctrl, textvariable=self._dsv,
                                   state="readonly", width=32)
        self._menu.pack(side="left", padx=(0, 10))
        self._menu.bind("<<ComboboxSelected>>", self._show)
        _btn(ctrl, "🔄 Refresh", self._refresh, color=C_BTN_BLUE, width=10).pack(side="left")

        self._stats = tk.StringVar(value="")
        tk.Label(self, textvariable=self._stats, bg=C_MAIN_BG, fg=C_TEXT_MUTED,
                 font=("Segoe UI", 9), padx=24).pack(anchor="w")

        tf = tk.Frame(self, bg=C_MAIN_BG, padx=20, pady=4)
        tf.pack(fill="both", expand=True)
        self._tv = ttk.Treeview(tf, show="headings", height=24)
        vs = ttk.Scrollbar(tf, orient="vertical",   command=self._tv.yview)
        hs = ttk.Scrollbar(tf, orient="horizontal",  command=self._tv.xview)
        self._tv.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        vs.pack(side="right", fill="y"); hs.pack(side="bottom", fill="x")
        self._tv.pack(fill="both", expand=True)

    def _refresh(self):
        names = list(self._app.datasets.keys())
        self._menu["values"] = names or ["— none —"]
        if names:
            self._dsv.set(names[0]); self._show()

    def _show(self, _=None):
        name = self._dsv.get()
        if name not in self._app.datasets: return
        df = self._app.datasets[name]
        if df is None: return
        self._tv["columns"] = []
        for i in self._tv.get_children(): self._tv.delete(i)
        cols = list(df.columns)
        self._tv["columns"] = cols
        for c in cols:
            self._tv.heading(c, text=c)
            self._tv.column(c, width=100, minwidth=60)
        for _, row in df.head(20).iterrows():
            self._tv.insert("", "end", values=[str(v)[:40] for v in row.values])
        self._stats.set(
            f"Dataset: {name}  |  {df.shape[0]:,} rows  |  {df.shape[1]} cols  "
            f"|  Nulls: {int(df.isnull().sum().sum()):,}  |  Showing first 20 rows")


                                                                               
                               
                                                                               

class FeatureEngineeringPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Feature Engineering",
                         "Run the sprint risk feature pipeline via pipeline.py", **kw)
        self._app = app
        self._build()

    def _build(self):
        body = self._scrollable_body()

        ic = _card(body); ic.pack(fill="x", padx=20, pady=(18, 8))
        _lbl(ic, "  Engineered Features", 12, bold=True).pack(anchor="w", pady=(10, 4))
        desc = (
            "velocity  •  velocity_variance  •  completion_rate  •  backlog_growth\n"
            "punt_rate  •  schedule_variance  •  defect_density  •  sprint_risk_label\n"
            "avg_story_points  •  story_point_delta  •  not_completed_ratio  •  assignee_diversity\n\n"
            "Output: merged_train_data.csv saved to the working directory."
        )
        tk.Label(ic, text=desc, bg=C_CARD_BG, fg=C_TEXT_MUTED,
                 font=("Consolas", 9), justify="left", padx=14).pack(
            anchor="w", pady=(0, 10))

        cc = _card(body); cc.pack(fill="x", padx=20, pady=8)
        cr = tk.Frame(cc, bg=C_CARD_BG, padx=14, pady=10); cr.pack(fill="x")
        _lbl(cr, "Base directory:", 10, bg=C_CARD_BG).pack(side="left", padx=(0, 8))
        self._dirv = tk.StringVar(value=str(BASE_DIR))
        tk.Entry(cr, textvariable=self._dirv, font=("Segoe UI", 9),
                 width=40).pack(side="left", padx=(0, 8))
        _btn(cr, "📁 Browse", self._browse, color="#9B59B6", width=10).pack(
            side="left", padx=(0, 10))
        _btn(cr, "⚙️  Run Pipeline", self._run, color=C_BTN_GREEN).pack(side="left")

        pf = tk.Frame(body, bg=C_MAIN_BG, padx=20, pady=4); pf.pack(fill="x")
        self._prog  = ttk.Progressbar(pf, mode="indeterminate", length=400)
        self._prog.pack(fill="x")
        self._plbl  = tk.Label(pf, text="", bg=C_MAIN_BG, fg=C_TEXT_MUTED,
                                font=("Segoe UI", 9))
        self._plbl.pack(anchor="w", pady=2)

        lc = _card(body); lc.pack(fill="both", expand=True, padx=20, pady=8)
        _lbl(lc, "  Pipeline Log", 11, bold=True).pack(anchor="w", pady=(10, 4))
        self._lt = tk.Text(lc, height=20, state="disabled", bg="#0D1117", fg="#C9D1D9",
                            font=("Consolas", 9), relief="flat", padx=8, pady=8)
        vs = ttk.Scrollbar(lc, orient="vertical", command=self._lt.yview)
        self._lt.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y", padx=(0, 10))
        self._lt.pack(fill="both", expand=True, padx=(14, 0), pady=(0, 10))

    def _browse(self):
        d = filedialog.askdirectory()
        if d: self._dirv.set(d)

    def _append(self, msg):
        self._lt.configure(state="normal")
        self._lt.insert(tk.END, f"[{_now()}] {msg}\n")
        self._lt.see(tk.END)
        self._lt.configure(state="disabled")

    def _clear(self):
        self._lt.configure(state="normal")
        self._lt.delete("1.0", tk.END)
        self._lt.configure(state="disabled")

    def _run(self):
        base = self._dirv.get()
        self._prog.start(10); self._plbl.config(text="Running pipeline…")
        self._clear()

        def worker():
            try:
                self._append("Pipeline started…")
                import importlib
                pipeline_path = str(BASE_DIR)
                if pipeline_path not in sys.path:
                    sys.path.insert(0, pipeline_path)
                try:
                    import pipeline; importlib.reload(pipeline)
                    self._append("pipeline.py imported.")
                    result = pipeline.run_full_pipeline(base_dir=base,
                                                         output_dir=str(BASE_DIR))
                    if result is not None:
                        X_tr, X_vl, X_te, y_tr, y_vl, y_te, feat, scl = result
                        self._append(f"Done. X_train={X_tr.shape}, features={len(feat)}")
                        self._app.feature_names   = feat
                        self._app.scaler          = scl
                        self._app.splits          = (X_tr, X_vl, X_te, y_tr, y_vl, y_te)
                        self._app.features_count  = len(feat)
                        self._app.update_dashboard()
                    else:
                        self._append("⚠  Pipeline returned None — check dataset files.")
                except ImportError as e:
                    self._append(f"❌ Cannot import pipeline.py: {e}")
                except Exception as e:
                    self._append(f"❌ Error: {e}")
                    self._append(traceback.format_exc())
            finally:
                self._prog.stop()
                self._plbl.config(text="Pipeline finished.")
                self._app.set_status("Feature engineering complete.")

        threading.Thread(target=worker, daemon=True).start()


                                                                               
                       
                                                                               

class TrainModelPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Train Model",
                         "Select algorithms and train on the merged dataset", **kw)
        self._app = app
        self._build()

    def _build(self):
        body = self._scrollable_body()
        ac = _card(body); ac.pack(fill="x", padx=20, pady=(18, 8))
        _lbl(ac, "  Select Algorithms", 12, bold=True).pack(anchor="w", pady=(10, 4))

        self._algos = {}
        for name, default, tip in [
            ("Logistic Regression", True,  "Linear baseline — fast, interpretable"),
            ("Random Forest",       True,  "200 trees, bagging ensemble"),
            ("Gradient Boosting",   True,  "200 estimators, sequential boosting"),
            ("SVC",                 False, "RBF kernel SVM (slow on large data)"),
        ]:
            var = tk.BooleanVar(value=default)
            self._algos[name] = var
            r = tk.Frame(ac, bg=C_CARD_BG, padx=14); r.pack(fill="x", pady=3)
            tk.Checkbutton(r, text=name, variable=var, bg=C_CARD_BG, fg=C_TEXT_DARK,
                            font=("Segoe UI", 10, "bold"),
                            activebackground=C_CARD_BG,
                            selectcolor=C_CARD_BG).pack(side="left")
            tk.Label(r, text=f"  — {tip}", bg=C_CARD_BG, fg=C_TEXT_MUTED,
                     font=("Segoe UI", 9)).pack(side="left")
        tk.Frame(ac, bg=C_CARD_BG, height=6).pack()

        cc = _card(body); cc.pack(fill="x", padx=20, pady=8)
        cr = tk.Frame(cc, bg=C_CARD_BG, padx=14, pady=10); cr.pack(fill="x")
        self._tbtn = _btn(cr, "🚀  Train Selected Models",
                           self._start, color=C_BTN_GREEN)
        self._tbtn.pack(side="left", padx=(0, 12))
        _btn(cr, "🗑  Clear Log", self._clear, color=C_BTN_RED, width=10).pack(side="left")

        pf = tk.Frame(body, bg=C_MAIN_BG, padx=20, pady=4); pf.pack(fill="x")
        self._prog = ttk.Progressbar(pf, mode="indeterminate", length=400)
        self._prog.pack(fill="x")
        self._plbl = tk.Label(pf, text="", bg=C_MAIN_BG, fg=C_TEXT_MUTED,
                               font=("Segoe UI", 9))
        self._plbl.pack(anchor="w", pady=2)

        lc = _card(body); lc.pack(fill="both", expand=True, padx=20, pady=8)
        _lbl(lc, "  Training Log", 11, bold=True).pack(anchor="w", pady=(10, 4))
        self._lt = tk.Text(lc, height=22, state="disabled", bg="#0D1117", fg="#C9D1D9",
                            font=("Consolas", 9), relief="flat", padx=8, pady=8)
        vs = ttk.Scrollbar(lc, orient="vertical", command=self._lt.yview)
        self._lt.configure(yscrollcommand=vs.set)
        vs.pack(side="right", fill="y", padx=(0, 10))
        self._lt.pack(fill="both", expand=True, padx=(14, 0), pady=(0, 10))

    def _append(self, msg):
        self._lt.configure(state="normal")
        self._lt.insert(tk.END, f"[{_now()}] {msg}\n")
        self._lt.see(tk.END)
        self._lt.configure(state="disabled")

    def _clear(self):
        self._lt.configure(state="normal")
        self._lt.delete("1.0", tk.END)
        self._lt.configure(state="disabled")

    def _start(self):
        selected = [n for n, v in self._algos.items() if v.get()]
        if not selected:
            messagebox.showwarning("None selected", "Tick at least one algorithm.")
            return
        self._tbtn.config(state="disabled")
        self._prog.start(10); self._plbl.config(text="Training…")
        self._clear(); self._append(f"Training: {', '.join(selected)}")

        def worker():
            try:
                self._train(selected)
            finally:
                self._prog.stop(); self._plbl.config(text="Training complete.")
                self._tbtn.config(state="normal")
                self._app.set_status("Model training complete.")

        threading.Thread(target=worker, daemon=True).start()

    def _train(self, selected):
        if not (PANDAS_OK and NUMPY_OK and SKLEARN_OK and JOBLIB_OK):
            self._append("❌ Missing: pandas / numpy / sklearn / joblib"); return

        import numpy as np, pandas as pd, joblib, time
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split, cross_val_score
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

        splits = self._app.splits
        if splits is not None:
            X_tr, X_vl, X_te, y_tr, y_vl, y_te = splits
            self._append(f"Using pre-split data: X_train={X_tr.shape}")
        else:
            candidates = [BASE_DIR / "merged_train_data.csv",
                           pathlib.Path("/content/merged_train_data.csv")]
            df = None
            for c in candidates:
                if c.exists():
                    df = pd.read_csv(c); self._append(f"Loaded: {c}"); break
            if df is None:
                self._append("❌ No training data. Run Feature Engineering first."); return
            TARGET = "sprint_risk_label"
            if TARGET not in df.columns:
                self._append(f"❌ Column '{TARGET}' not found."); return
            feat = [c for c in df.columns if c != TARGET]
            X = df[feat].fillna(0).values.astype(np.float64)
            y = df[TARGET].fillna(0).values.astype(int)
            X_temp, X_te, y_temp, y_te = train_test_split(
                X, y, test_size=0.15, stratify=y, random_state=42)
            X_tr, X_vl, y_tr, y_vl = train_test_split(
                X_temp, y_temp, test_size=0.15/0.85, stratify=y_temp, random_state=42)
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_tr)
            X_vl = scaler.transform(X_vl)
            X_te = scaler.transform(X_te)
            joblib.dump(scaler, SCALER_PATH)
            self._app.scaler = scaler
            self._app.feature_names = feat
            self._append(f"Split: train={X_tr.shape} val={X_vl.shape} test={X_te.shape}")

        blueprints = {
            "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
            "Random Forest":       RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
            "Gradient Boosting":   GradientBoostingClassifier(n_estimators=200, random_state=42),
            "SVC":                 SVC(kernel="rbf", probability=True, random_state=42),
        }

        results = {}
        best_f1, best_model, best_name = -1.0, None, ""

        for name in selected:
            self._append(f"\n── {name}")
            t0 = time.time()
            m  = blueprints[name]
            m.fit(X_tr, y_tr)
            elapsed = time.time() - t0
            yp  = m.predict(X_te)
            f1  = f1_score(y_te, yp, average="weighted", zero_division=0)
            acc = accuracy_score(y_te, yp)
            try:
                if hasattr(m, "predict_proba"):
                    pr = m.predict_proba(X_te)
                    roc = (roc_auc_score(y_te, pr[:, 1])
                           if pr.shape[1] == 2
                           else roc_auc_score(y_te, pr, multi_class="ovr",
                                               average="weighted"))
                else: roc = float("nan")
            except Exception: roc = float("nan")
            cv = cross_val_score(
                m, np.vstack([X_tr, X_vl]),
                np.concatenate([y_tr, y_vl]),
                cv=5, scoring="f1_weighted", n_jobs=-1).mean()

            self._append(f"  {elapsed:.1f}s | Acc={acc:.4f} F1={f1:.4f} "
                          f"ROC={roc:.4f} CV-F1={cv:.4f}")
            results[name] = {"model": m, "test_f1": f1, "val_acc": acc}
            if f1 > best_f1:
                best_f1, best_model, best_name = f1, m, name

        if best_model is not None:
            joblib.dump(best_model, MODEL_PATH)
            self._append(f"\n🏆 Best: {best_name} (F1={best_f1:.4f}) → {MODEL_PATH}")
            self._app.trained_models       = results
            self._app.best_model           = best_model
            self._app.best_model_name      = best_name
            self._app.models_trained_count = len(results)
            self._app.splits = (X_tr, X_vl, X_te, y_tr, y_vl, y_te)
            self._app.update_dashboard()
            self._app.evaluation_panel.refresh()


                                                                               
                                                                  
                                                                               

class EvaluationPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Evaluation",
                         "Confusion matrices, ROC curves, and metrics table", **kw)
        self._app    = app
        self._canvas_widget = None                                
        self._build()

    def _build(self):
                                                                                
        ctrl = tk.Frame(self, bg=C_MAIN_BG, padx=20, pady=8)
        ctrl.pack(fill="x")
        _btn(ctrl, "🔄  Refresh Results", self.refresh,    color=C_BTN_BLUE, width=18).pack(side="left", padx=(0, 10))
        _btn(ctrl, "💾  Save Plots",      self._save_plots, color=C_BTN_GREEN, width=12).pack(side="left")

                                                                                
        body = self._scrollable_body()

                            
        tc = _card(body); tc.pack(fill="x", padx=20, pady=8)
        _lbl(tc, "  Model Metrics Summary", 12, bold=True).pack(anchor="w", pady=(10, 4))
        cols = ("Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "CV-F1")
        self._tv = ttk.Treeview(tc, columns=cols, show="headings", height=7)
        for col in cols:
            self._tv.heading(col, text=col)
            w = 170 if col == "Model" else 90
            self._tv.column(col, width=w, minwidth=60, anchor="center")
        self._tv.pack(fill="x", padx=14, pady=(0, 10))

                                                                           
        self._plot_card = _card(body)
        self._plot_card.pack(fill="both", expand=True, padx=20, pady=8)
        _lbl(self._plot_card, "  Confusion Matrices & Feature Importance",
             12, bold=True).pack(anchor="w", pady=(10, 4))

        self._no_model_lbl = tk.Label(
            self._plot_card,
            text="No trained models yet.\nTrain models in the 'Train Model' tab first.",
            bg=C_CARD_BG, fg=C_TEXT_MUTED, font=("Segoe UI", 12))
        self._no_model_lbl.pack(expand=True, pady=40)

    def refresh(self):
        for i in self._tv.get_children():
            self._tv.delete(i)

        models = self._app.trained_models
        splits = self._app.splits
        if not models or splits is None:
            return

        X_tr, X_vl, X_te, y_tr, y_vl, y_te = splits

        import numpy as np
        from sklearn.metrics import (accuracy_score, precision_score,
                                      recall_score, f1_score, roc_auc_score)
        from sklearn.model_selection import cross_val_score

        rows = []
        for name, info in models.items():
            m      = info["model"]
            yp     = m.predict(X_te)
            acc    = accuracy_score(y_te, yp)
            prec   = precision_score(y_te, yp, average="weighted", zero_division=0)
            rec    = recall_score(y_te,    yp, average="weighted", zero_division=0)
            f1     = f1_score(y_te,         yp, average="weighted", zero_division=0)
            try:
                pr  = m.predict_proba(X_te) if hasattr(m, "predict_proba") else None
                roc = (roc_auc_score(y_te, pr[:, 1])
                       if pr is not None and pr.shape[1] == 2
                       else roc_auc_score(y_te, pr, multi_class="ovr",
                                           average="weighted")
                       if pr is not None else float("nan"))
            except Exception:
                roc = float("nan")
            cv = cross_val_score(
                m, np.vstack([X_tr, X_vl]),
                np.concatenate([y_tr, y_vl]),
                cv=5, scoring="f1_weighted", n_jobs=-1).mean()

            self._tv.insert("", "end",
                             values=(name,
                                     f"{acc:.4f}", f"{prec:.4f}", f"{rec:.4f}",
                                     f"{f1:.4f}",
                                     f"{roc:.4f}" if roc == roc else "N/A",
                                     f"{cv:.4f}"))
            rows.append((name, m, yp, info.get("test_f1", f1)))

        self._build_plots(models, X_te, y_te)

    def _build_plots(self, models, X_te, y_te):
        
        if not (MATPLOTLIB_OK and SEABORN_OK):
            return

        import numpy as np, matplotlib.pyplot as plt, seaborn as sns
        from sklearn.metrics import confusion_matrix, roc_curve, auc as sk_auc
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

                                      
        if self._canvas_widget is not None:
            self._canvas_widget.get_tk_widget().destroy()
            self._canvas_widget = None
        self._no_model_lbl.pack_forget()

        n       = len(models)
        ncols   = min(n, 2)
        nrows   = (n + ncols - 1) // ncols
        n_cls   = len(np.unique(y_te))
        labels  = ["No Risk", "At Risk"] if n_cls == 2 else None

                                                                               
                                                                   
        has_rf  = "Random Forest" in models and hasattr(
            models["Random Forest"]["model"], "feature_importances_")
        extra_rows = 1 if n_cls == 2 else 0            
        extra_rows += 1 if has_rf else 0               

        fig_h = nrows * 4.5 + extra_rows * 5
        fig   = plt.figure(figsize=(13, max(fig_h, 5)))

                                                                                
        import matplotlib.gridspec as gridspec
        total_rows = nrows + extra_rows
        gs = gridspec.GridSpec(total_rows, ncols, figure=fig,
                               hspace=0.55, wspace=0.4)

        axes_cm = []
        for r in range(nrows):
            for c in range(ncols):
                axes_cm.append(fig.add_subplot(gs[r, c]))

        for ax, (nm, info) in zip(axes_cm, models.items()):
            m  = info["model"]
            yp = m.predict(X_te)
            cm = confusion_matrix(y_te, yp)
            tl = labels if labels and cm.shape[0] == 2 else None
            sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                        xticklabels=tl, yticklabels=tl,
                        linewidths=1, linecolor="white",
                        annot_kws={"size": 13})
            ax.set_title(nm, fontsize=11, fontweight="bold", pad=8)
            ax.set_xlabel("Predicted", fontsize=9)
            ax.set_ylabel("Actual",    fontsize=9)

        for ax in axes_cm[n:]:
            ax.set_visible(False)

        extra_row_idx = nrows

                                                                                
        if n_cls == 2:
            ax_roc = fig.add_subplot(gs[extra_row_idx, :])
            colors = ["#3498DB", "#2ECC71", "#E74C3C", "#9B59B6"]
            for color, (nm, info) in zip(colors, models.items()):
                m = info["model"]
                try:
                    proba = m.predict_proba(X_te)[:, 1]
                    fpr, tpr, _ = roc_curve(y_te, proba)
                    ax_roc.plot(fpr, tpr, color=color, linewidth=2,
                                label=f"{nm} (AUC={sk_auc(fpr,tpr):.3f})")
                except Exception:
                    pass
            ax_roc.plot([0, 1], [0, 1], "k--", linewidth=1)
            ax_roc.set_title("ROC Curves — Test Set", fontsize=11, fontweight="bold")
            ax_roc.set_xlabel("False Positive Rate"); ax_roc.set_ylabel("True Positive Rate")
            ax_roc.legend(fontsize=9); ax_roc.grid(True, alpha=0.3)
            extra_row_idx += 1

                                                                                
        if has_rf:
            rf_m  = models["Random Forest"]["model"]
            fnames = self._app.feature_names or []
            imps   = rf_m.feature_importances_
            if len(fnames) == len(imps):
                ax_fi = fig.add_subplot(gs[extra_row_idx, :])
                fi = (sorted(zip(fnames, imps), key=lambda x: x[1], reverse=True))[:20]
                fi_names, fi_vals = zip(*fi)
                colors_fi = plt.cm.RdYlGn(
                    [v / max(fi_vals) for v in fi_vals])[::-1]
                ax_fi.barh(list(fi_names)[::-1], list(fi_vals)[::-1],
                            color=colors_fi, edgecolor="white")
                ax_fi.set_title("Random Forest — Top 20 Feature Importances",
                                 fontsize=11, fontweight="bold")
                ax_fi.set_xlabel("Gini Importance")

        fig.suptitle("Model Evaluation — Test Set",
                     fontsize=13, fontweight="bold", y=1.0)

                                                                                
        canvas = FigureCanvasTkAgg(fig, master=self._plot_card)
        canvas.draw()
        w = canvas.get_tk_widget()
        w.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._canvas_widget = canvas
        plt.close(fig)

    def _save_plots(self):
        if self._canvas_widget is None:
            messagebox.showinfo("Nothing to save", "Refresh results first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            title="Save evaluation plots…")
        if path:
            self._canvas_widget.figure.savefig(path, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Saved", f"Plots saved to:\n{path}")


                                                                               
                                                             
                                                                               

class RiskPredictorPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Risk Predictor",
                         "Enter sprint metrics for real-time risk assessment", **kw)
        self._app = app
        self._build()

    def _build(self):
        body = self._scrollable_body()

        two = tk.Frame(body, bg=C_MAIN_BG, padx=20, pady=10)
        two.pack(fill="both", expand=True)
        two.columnconfigure(0, weight=3)
        two.columnconfigure(1, weight=2)

                                                                                
        fc = _card(two); fc.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        _lbl(fc, "  Sprint Metrics Input", 12, bold=True).pack(anchor="w", pady=(10, 4))

        self._fields = {}

                                                                                   
        field_defs = [
            ("velocity",          "Sprint Velocity",          "45",   "completedIssues estimate sum"),
            ("completion_rate",   "Completion Rate (0–1)",    "0.92", "completedIssues / totalIssues"),
            ("backlog_growth",    "Backlog Growth",           "3",    "issues added mid-sprint"),
            ("punt_rate",         "Punt Rate (0–1)",          "0.05", "puntedIssues / totalIssues"),
            ("schedule_variance", "Schedule Variance (days)", "-1",   "negative = early, positive = late"),
            ("avg_story_points",  "Avg Story Points",         "5.2",  "mean currentStoryPoint per sprint"),
            ("story_point_delta", "Story Point Delta",        "0.1",  "mean (current − initial)"),
            ("defect_density",    "Defect Density",           "0.02", "branchCount / loc (NASA proxy)"),
        ]

        fi = tk.Frame(fc, bg=C_CARD_BG, padx=14, pady=6)
        fi.pack(fill="x")
                                                                               
        fi.columnconfigure(0, weight=1)
        fi.columnconfigure(1, weight=0)

        for row_idx, (key, label, default, tip) in enumerate(field_defs):

                                                                                
            lf = tk.Frame(fi, bg=C_CARD_BG)
            lf.grid(row=row_idx, column=0,
                    sticky="w", padx=(0, 12), pady=5)

            tk.Label(lf, text=label, bg=C_CARD_BG, fg=C_TEXT_DARK,
                     font=("Segoe UI", 9, "bold"),
                     anchor="w", justify="left",
                     wraplength=200).pack(anchor="w")
            tk.Label(lf, text=tip, bg=C_CARD_BG, fg=C_TEXT_MUTED,
                     font=("Segoe UI", 7),
                     anchor="w", justify="left",
                     wraplength=200).pack(anchor="w")

            var = tk.StringVar(value=default)
            self._fields[key] = var
            tk.Entry(fi, textvariable=var,
                     font=("Segoe UI", 10),
                     width=10, relief="solid",
                     highlightbackground=C_CARD_BORDER,
                     highlightthickness=1).grid(
                row=row_idx, column=1, sticky="w", pady=5)

        br = tk.Frame(fc, bg=C_CARD_BG, padx=14, pady=10)
        br.pack(fill="x")
        _btn(br, "🔮  Predict Risk", self._predict, color=C_BTN_GREEN).pack(
            side="left", padx=(0, 8))
        _btn(br, "↩  Reset", self._reset, color=C_BTN_RED, width=8).pack(side="left")

                                                                                
        rc = _card(two); rc.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        _lbl(rc, "  Prediction Result", 12, bold=True).pack(anchor="w", pady=(10, 4))

        inner = tk.Frame(rc, bg=C_CARD_BG, padx=16, pady=10)
        inner.pack(fill="both", expand=True)

        self._rlv = tk.StringVar(value="—")
        self._rlw = tk.Label(inner, textvariable=self._rlv,
                              bg=C_CARD_BG, fg=C_TEXT_MUTED,
                              font=("Segoe UI", 34, "bold"))
        self._rlw.pack(pady=(10, 4))

        tk.Label(inner, text="Risk Probability:", bg=C_CARD_BG,
                 fg=C_TEXT_MUTED, font=("Segoe UI", 10)).pack(anchor="w")
        self._pbar = tk.Canvas(inner, height=28, bg="#ECEFF1",
                                highlightthickness=1,
                                highlightbackground=C_CARD_BORDER)
        self._pbar.pack(fill="x", pady=(4, 8))
        self._ptxt = tk.StringVar(value="—")
        tk.Label(inner, textvariable=self._ptxt, bg=C_CARD_BG,
                 fg=C_TEXT_MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        tk.Label(inner, text="Recommendation:", bg=C_CARD_BG,
                 fg=C_TEXT_DARK, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(12, 2))
        self._recv = tk.StringVar(value="Run a prediction to see a recommendation.")
        tk.Label(inner, textvariable=self._recv, bg=C_CARD_BG,
                 fg=C_TEXT_MUTED, font=("Segoe UI", 10),
                 wraplength=300, justify="left").pack(anchor="w")

        self._miv = tk.StringVar(value="No model loaded.")
        tk.Label(inner, textvariable=self._miv, bg=C_CARD_BG,
                 fg=C_TEXT_MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(14, 0))

                                                                                
        dc = _card(body); dc.pack(fill="x", padx=20, pady=8)
        _lbl(dc, "  Load Demo Scenario", 11, bold=True).pack(anchor="w", pady=(10, 4))
        dr = tk.Frame(dc, bg=C_CARD_BG, padx=14, pady=8); dr.pack(fill="x")

        demos = [
            ("✅ Low Risk",    "#2ECC71",
             {"velocity":"45","completion_rate":"0.92","backlog_growth":"3",
              "punt_rate":"0.05","schedule_variance":"-1",
              "avg_story_points":"5.2","story_point_delta":"0.1","defect_density":"0.02"}),
            ("⚠️ Medium Risk","#F0A500",
             {"velocity":"28","completion_rate":"0.68","backlog_growth":"12",
              "punt_rate":"0.22","schedule_variance":"3",
              "avg_story_points":"8.1","story_point_delta":"1.4","defect_density":"0.07"}),
            ("🚨 High Risk",  "#E67E22",
             {"velocity":"15","completion_rate":"0.45","backlog_growth":"28",
              "punt_rate":"0.41","schedule_variance":"9",
              "avg_story_points":"11.3","story_point_delta":"3.8","defect_density":"0.18"}),
            ("🔴 Critical",   "#E74C3C",
             {"velocity":"6","completion_rate":"0.22","backlog_growth":"47",
              "punt_rate":"0.72","schedule_variance":"21",
              "avg_story_points":"18.9","story_point_delta":"7.2","defect_density":"0.41"}),
        ]
        for label, color, scenario in demos:
            _btn(dr, label, lambda s=scenario: self._load_demo(s),
                 color=color, width=12).pack(side="left", padx=(0, 8))

    def _load_demo(self, scenario):
        for k, v in scenario.items():
            if k in self._fields:
                self._fields[k].set(v)
        self._predict()

    def _reset(self):
        defaults = {"velocity":"45","completion_rate":"0.92","backlog_growth":"3",
                    "punt_rate":"0.05","schedule_variance":"-1","avg_story_points":"5.2",
                    "story_point_delta":"0.1","defect_density":"0.02"}
        for k, v in defaults.items():
            if k in self._fields:
                self._fields[k].set(v)

    def _predict(self):
        import numpy as np

        raw = {}
        for k, var in self._fields.items():
            try:
                raw[k] = float(var.get().replace("−", "-").strip())
            except ValueError:
                messagebox.showerror("Input error", f"Invalid value for '{k}'")
                return

        model  = self._app.best_model
        scaler = self._app.scaler
        feat   = self._app.feature_names

        if model is None and JOBLIB_OK:
            import joblib
            if MODEL_PATH.exists():
                try:   model = joblib.load(MODEL_PATH); self._app.best_model = model
                except Exception: pass
        if scaler is None and JOBLIB_OK:
            import joblib
            if SCALER_PATH.exists():
                try:   scaler = joblib.load(SCALER_PATH); self._app.scaler = scaler
                except Exception: pass

        if model is None:
            self._rlv.set("No Model")
            self._rlw.config(fg=C_TEXT_MUTED)
            self._recv.set("Train a model first or ensure best_model.pkl exists.")
            return

        if feat:
            vec = np.array([float(raw.get(f, 0.0)) for f in feat], dtype=np.float64)
        else:
            ordered = ["velocity","velocity_variance","completion_rate","backlog_growth",
                       "punt_rate","schedule_variance","avg_story_points","story_point_delta",
                       "not_completed_ratio","assignee_diversity",
                       "loc","v(g)","ev(g)","iv(g)","n","v","l","d","i","e","b","t",
                       "lOCode","lOComment","lOBlank","uniq_Op","uniq_Opnd",
                       "total_Op","total_Opnd","branchCount","defect_density"]
            vec = np.array([float(raw.get(k, 0.0)) for k in ordered], dtype=np.float64)

        vec = vec.reshape(1, -1)
        if scaler is not None:
            try: vec = scaler.transform(vec)
            except Exception: pass

        rc  = int(model.predict(vec)[0])
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(vec)[0]
            prob  = float(proba[rc]) if rc < len(proba) else float(proba[-1])
        else:
            prob = 0.75

        label = {0: "Low", 1: "At Risk"}.get(rc, "High" if rc >= 2 else "At Risk")
        color = RISK_COLOURS.get(label, C_TEXT_MUTED)
        rec   = RISK_RECOMMENDATIONS.get(label, "")

        self._rlv.set(label.upper())
        self._rlw.config(fg=color, bg=C_CARD_BG)
        self._ptxt.set(f"Probability: {prob*100:.1f}%")
        self._recv.set(rec)
        self._miv.set(
            f"Model: {self._app.best_model_name or 'disk'}  "
            f"| Class: {rc}  | Prob: {prob:.4f}")

        self._pbar.update_idletasks()
        w = max(self._pbar.winfo_width(), 1)
        fw = max(4, int(w * prob))
        self._pbar.delete("all")
        self._pbar.create_rectangle(0, 0, fw, 28, fill=color, outline="")
        self._pbar.create_rectangle(fw, 0, w, 28, fill="#ECEFF1", outline="")
        self._pbar.create_text(fw // 2, 14, text=f"{prob*100:.1f}%",
                                fill="white", font=("Segoe UI", 9, "bold"))
        self._app.set_status(f"Prediction: {label} ({prob*100:.1f}%)")


                                                                               
                 
                                                                               

class AboutPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "About",
                         "Project information and academic details", **kw)
        self._build()

    def _build(self):
        body = self._scrollable_body()

        ban = tk.Frame(body, bg="#1E3A5F", padx=26, pady=20)
        ban.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(ban, text="AgileRisk AI", bg="#1E3A5F", fg="#F0A500",
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(ban, text="Predictive Risk Management System for Agile IT Projects",
                 bg="#1E3A5F", fg="#FFFFFF", font=("Segoe UI", 11)).pack(anchor="w", pady=(2, 0))
        tk.Label(ban, text="Powered by Machine Learning  ·  Python 3.11.9",
                 bg="#1E3A5F", fg="#8BA0B8", font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        ac = _card(body); ac.pack(fill="x", padx=20, pady=8)
        _lbl(ac, "  Academic Details", 12, bold=True).pack(anchor="w", pady=(10, 4))
        details = [
            ("Project Title", "The Role of AI in Enhancing Predictive Risk Management in Agile IT Projects"),
            ("Student",       "Manfred Oppong"),
            ("Banner ID",     "B01814357"),
            ("Programme",     "MSc IT with Project Management"),
            ("University",    "University of the West of Scotland (UWS)"),
            ("Supervisor",    "Durfashan Tariq"),
            ("Year",          "2026"),
        ]
        for field, val in details:
            r = tk.Frame(ac, bg=C_CARD_BG, padx=14, pady=4); r.pack(fill="x")
            tk.Label(r, text=f"{field}:", bg=C_CARD_BG, fg=C_TEXT_MUTED,
                     font=("Segoe UI", 10), width=14, anchor="w").pack(side="left")
            tk.Label(r, text=val, bg=C_CARD_BG, fg=C_TEXT_DARK,
                     font=("Segoe UI", 10, "bold"), anchor="w",
                     wraplength=580, justify="left").pack(side="left")
        tk.Frame(ac, bg=C_CARD_BG, height=6).pack()

        ab = _card(body); ab.pack(fill="x", padx=20, pady=8)
        _lbl(ab, "  Project Abstract", 12, bold=True).pack(anchor="w", pady=(10, 4))
        tk.Label(ab,
                 text=(
                     "AgileRisk AI integrates five NASA PROMISE software defect datasets, "
                     "four open-source Agile Scrum project histories (Mesos, Spring XD, "
                     "Aurora, Usergrid), a 4,000-record project risk dataset, and an Agile "
                     "Projects outcome dataset. A feature engineering pipeline derives "
                     "sprint-level risk proxies. Four classifiers are trained (Logistic "
                     "Regression, Random Forest, Gradient Boosting, SVM) and the best "
                     "model is deployed in this desktop application for real-time sprint "
                     "risk assessment with actionable recommendations."
                 ),
                 bg=C_CARD_BG, fg=C_TEXT_DARK, font=("Segoe UI", 10),
                 wraplength=680, justify="left",
                 padx=14, pady=0).pack(anchor="w", pady=(0, 12))


                                                                               
                    
                                                                               

class SettingsPanel(BasePanel):
    def __init__(self, parent, app, **kw):
        super().__init__(parent, "Settings",
                         "Customise the application appearance", **kw)
        self._app = app
        self._build()

    def _build(self):
        body = self._scrollable_body()

        tc = _card(body); tc.pack(fill="x", padx=20, pady=(18, 8))
        _lbl(tc, "  Application Theme", 12, bold=True).pack(anchor="w", pady=(10, 4))
        tk.Label(tc, text="Requires ttkbootstrap. Changes apply immediately.",
                 bg=C_CARD_BG, fg=C_TEXT_MUTED, font=("Segoe UI", 9),
                 padx=14).pack(anchor="w")
        cr = tk.Frame(tc, bg=C_CARD_BG, padx=14, pady=10); cr.pack(fill="x")
        tk.Label(cr, text="Theme:", bg=C_CARD_BG, fg=C_TEXT_DARK,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        self._tv = tk.StringVar(value=DEFAULT_THEME)
        ttk.Combobox(cr, textvariable=self._tv, values=AVAILABLE_THEMES,
                     state="readonly", width=20).pack(side="left", padx=(0, 10))
        _btn(cr, "Apply Theme", self._apply, color=C_BTN_BLUE, width=12).pack(side="left")
        tk.Frame(tc, bg=C_CARD_BG, height=6).pack()

        fc = _card(body); fc.pack(fill="x", padx=20, pady=8)
        _lbl(fc, "  File Paths", 12, bold=True).pack(anchor="w", pady=(10, 4))
        for name, path in [("best_model.pkl", MODEL_PATH),
                             ("scaler.pkl",    SCALER_PATH),
                             ("merged_train_data.csv", MERGED_CSV)]:
            r = tk.Frame(fc, bg=C_CARD_BG, padx=14, pady=4); r.pack(fill="x")
            e = path.exists()
            tk.Label(r, text=f"{'✅' if e else '❌'}  {name}",
                     bg=C_CARD_BG, fg=C_BTN_GREEN if e else C_BTN_RED,
                     font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
            tk.Label(r, text=str(path), bg=C_CARD_BG, fg=C_TEXT_MUTED,
                     font=("Consolas", 8)).pack(side="left")
        tk.Frame(fc, bg=C_CARD_BG, height=6).pack()

    def _apply(self):
        if not TTKBOOTSTRAP:
            messagebox.showwarning("ttkbootstrap required",
                                   "Install ttkbootstrap to use themes.")
            return
        try:
            self._app.style.theme_use(self._tv.get())
            self._app.set_status(f"Theme: {self._tv.get()}")
        except Exception as e:
            messagebox.showerror("Theme error", str(e))


                                                                               
                  
                                                                               

class AgileRiskApp:
    def __init__(self):
        if TTKBOOTSTRAP:
            self.root  = ttk.Window(themename=DEFAULT_THEME)
            self.style = self.root.style
        else:
            self.root = tk.Tk()

        self.root.title(APP_TITLE)
        self.root.minsize(APP_MIN_W, APP_MIN_H)
        self.root.geometry(f"{APP_MIN_W}x{APP_MIN_H + 80}")
        self.root.configure(bg=C_MAIN_BG)

        icon = BASE_DIR / "app_icon.ico"
        if icon.exists():
            try: self.root.iconbitmap(str(icon))
            except Exception: pass

                   
        self.datasets:             dict  = {}
        self.trained_models:       dict  = {}
        self.best_model                  = None
        self.best_model_name:      str   = ""
        self.scaler                      = None
        self.feature_names:        list  = []
        self.splits                      = None
        self.features_count:       int   = 0
        self.models_trained_count: int   = 0

        self._build_layout()
        self._build_sidebar()
        self._build_panels()
        self._build_statusbar()
        self._try_load_saved_model()
        self._navigate("dashboard")

                                                                               

    def _build_layout(self):
        self._outer = tk.Frame(self.root, bg=C_SIDEBAR_BG)
        self._outer.pack(fill="both", expand=True)
        self._sidebar = tk.Frame(self._outer, bg=C_SIDEBAR_BG, width=SIDEBAR_W)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)
        self._content = tk.Frame(self._outer, bg=C_MAIN_BG)
        self._content.pack(side="left", fill="both", expand=True)

    def _build_sidebar(self):
        brand = tk.Frame(self._sidebar, bg="#152B4A", padx=12, pady=14)
        brand.pack(fill="x")
        tk.Label(brand, text="🛡 AgileRisk AI", bg="#152B4A", fg="#F0A500",
                 font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
        tk.Label(brand, text="Risk Management System", bg="#152B4A", fg="#8BA0B8",
                 font=("Segoe UI", 8), anchor="w").pack(fill="x")
        tk.Frame(self._sidebar, bg="#2C4E75", height=1).pack(fill="x")

        self._nav_btns: dict[str, SidebarButton] = {}
        nav = [
            ("dashboard",    "📊", "Dashboard"),
            ("load_data",    "📂", "Load Data"),
            ("data_preview", "👁",  "Data Preview"),
            ("feat_eng",     "⚙️",  "Feature Engineering"),
            ("train",        "🚀", "Train Model"),
            ("evaluation",   "📈", "Evaluation"),
            ("predictor",    "🔮", "Risk Predictor"),
            ("settings",     "⚙",  "Settings"),
            ("about",        "ℹ",  "About"),
        ]
        nf = tk.Frame(self._sidebar, bg=C_SIDEBAR_BG)
        nf.pack(fill="x", pady=(6, 0))
        for key, icon, label in nav:
            btn = SidebarButton(nf, text=label, icon=icon,
                                 command=lambda k=key: self._navigate(k))
            btn.pack(fill="x")
            self._nav_btns[key] = btn

        tk.Frame(self._sidebar, bg="#2C4E75", height=1).pack(
            fill="x", side="bottom")
        tk.Label(self._sidebar, text="v1.0.0  ·  Python 3.11.9",
                 bg=C_SIDEBAR_BG, fg="#4A6E8A",
                 font=("Segoe UI", 7)).pack(side="bottom", pady=5)

    def _build_panels(self):
        self.dashboard_panel    = DashboardPanel(self._content,    app=self)
        self.load_data_panel    = LoadDataPanel(self._content,     app=self)
        self.data_preview_panel = DataPreviewPanel(self._content,  app=self)
        self.feat_eng_panel     = FeatureEngineeringPanel(self._content, app=self)
        self.train_panel        = TrainModelPanel(self._content,   app=self)
        self.evaluation_panel   = EvaluationPanel(self._content,   app=self)
        self.predictor_panel    = RiskPredictorPanel(self._content, app=self)
        self.settings_panel     = SettingsPanel(self._content,     app=self)
        self.about_panel        = AboutPanel(self._content,        app=self)

        self._panels = {
            "dashboard":    self.dashboard_panel,
            "load_data":    self.load_data_panel,
            "data_preview": self.data_preview_panel,
            "feat_eng":     self.feat_eng_panel,
            "train":        self.train_panel,
            "evaluation":   self.evaluation_panel,
            "predictor":    self.predictor_panel,
            "settings":     self.settings_panel,
            "about":        self.about_panel,
        }
        for p in self._panels.values():
            p.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _build_statusbar(self):
        sb = tk.Frame(self.root, bg="#1E3A5F", height=24)
        sb.pack(fill="x", side="bottom"); sb.pack_propagate(False)
        self._status_var = tk.StringVar(value=f"Ready  ·  {_now()}")
        tk.Label(sb, textvariable=self._status_var, bg="#1E3A5F", fg="#8BA0B8",
                 font=("Segoe UI", 8), padx=12).pack(side="left", anchor="w")
        self._model_var = tk.StringVar(value="No model loaded")
        tk.Label(sb, textvariable=self._model_var, bg="#1E3A5F", fg="#8BA0B8",
                 font=("Segoe UI", 8), padx=12).pack(side="right", anchor="e")

                                                                                

    def _navigate(self, key):
        if key not in self._panels: return
        for p in self._panels.values(): p.lower()
        self._panels[key].lift()
        for k, btn in self._nav_btns.items():
            btn.set_active(k == key)
        if key == "data_preview":
            self.data_preview_panel._refresh()
        self.set_status(f"Navigated to: {key}")

                                                                                

    def register_dataset(self, name, df):
        self.datasets[name] = df
        self.update_dashboard()

    def set_status(self, msg):
        self._status_var.set(f"{msg}  ·  {_now()}")

    def update_dashboard(self):
        total = 0
        if PANDAS_OK:
            for df in self.datasets.values():
                if df is not None and hasattr(df, "__len__"):
                    total += len(df)
        name = self.best_model_name or ("Loaded" if self.best_model else "None")
        self._model_var.set(
            f"Best model: {name}" if self.best_model else "No model loaded")
        self.dashboard_panel.refresh(
            datasets_count=len(self.datasets),
            records=total,
            features=self.features_count,
            models=self.models_trained_count,
        )

    def _try_load_saved_model(self):
        if not JOBLIB_OK: return
        import joblib
        if MODEL_PATH.exists():
            try:
                self.best_model      = joblib.load(MODEL_PATH)
                self.best_model_name = "Loaded from disk"
                self._model_var.set("Model: loaded from best_model.pkl")
            except Exception: pass
        if SCALER_PATH.exists():
            try: self.scaler = joblib.load(SCALER_PATH)
            except Exception: pass
        if MERGED_CSV.exists() and PANDAS_OK:
            try:
                df = pd.read_csv(MERGED_CSV, nrows=1)
                self.feature_names  = [c for c in df.columns
                                        if c != "sprint_risk_label"]
                self.features_count = len(self.feature_names)
            except Exception: pass

                                                                                

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        if messagebox.askyesno("Exit", "Exit AgileRisk AI?"):
            self.root.destroy()


                                                                               
             
                                                                               

if __name__ == "__main__":
    AgileRiskApp().run()
