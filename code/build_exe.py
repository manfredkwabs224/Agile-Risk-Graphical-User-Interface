# =============================================================================
# build_exe.py — AgileRisk AI: Windows EXE Builder via PyInstaller
# MSc IT with Project Management | University of the West of Scotland
# Student  : Manfred Oppong | Banner ID: B01814357
# Supervisor: Durfashan Tariq | Year: 2026
# Python   : 3.11.9
#
# USAGE:
#   python build_exe.py               # full build
#   python build_exe.py --clean       # remove build artefacts only
#   python build_exe.py --no-confirm  # skip clean confirmation prompt
# =============================================================================

# ── Standard library ──────────────────────────────────────────────────────────
import os
import sys
import time
import shutil
import pathlib
import platform
import argparse
import subprocess
import importlib.util

# =============================================================================
# CONSTANTS
# =============================================================================

APP_NAME       = "AgileRisk_AI"
SCRIPT_DIR     = pathlib.Path(__file__).parent.resolve()
MAIN_SCRIPT    = SCRIPT_DIR / "App.py"
PIPELINE_SCRIPT = SCRIPT_DIR / "pipeline.py"
SPEC_FILE      = SCRIPT_DIR / f"{APP_NAME}.spec"
DIST_DIR       = SCRIPT_DIR / "dist"
BUILD_DIR      = SCRIPT_DIR / "build"
EXE_PATH       = DIST_DIR / f"{APP_NAME}.exe"
ICON_PATH      = SCRIPT_DIR / "app_icon.ico"

# Minimum Python version required
MIN_PYTHON = (3, 11)

# Required packages with minimum version constraints
REQUIRED_PACKAGES = {
    "ttkbootstrap":    "ttkbootstrap>=1.10.1",
    "sklearn":         "scikit-learn>=1.3.0",
    "pandas":          "pandas>=2.0.0",
    "numpy":           "numpy>=1.24.0",
    "matplotlib":      "matplotlib>=3.7.0",
    "seaborn":         "seaborn>=0.12.0",
    "joblib":          "joblib>=1.3.0",
    "openpyxl":        "openpyxl>=3.1.0",
    "imblearn":        "imbalanced-learn>=0.11.0",
    "xgboost":         "xgboost>=2.0.0",
    "PIL":             "Pillow>=10.0.0",
    "scipy":           "scipy>=1.11.0",
    "PyInstaller":     "pyinstaller>=6.3.0",
}

# PyInstaller hidden imports required to bundle sklearn, ttkbootstrap, etc.
HIDDEN_IMPORTS = [
    # scikit-learn internals
    "sklearn",
    "sklearn.utils._cython_blas",
    "sklearn.neighbors.typedefs",
    "sklearn.neighbors._partition_nodes",
    "sklearn.utils._weight_vector",
    "sklearn.utils._bunch",
    "sklearn.tree._utils",
    "sklearn.ensemble._gb_losses",
    "sklearn.linear_model._logistic",
    "sklearn.svm._libsvm",
    "sklearn.svm._liblinear",
    "sklearn.preprocessing._encoders",
    "sklearn.preprocessing._label",
    "sklearn.impute._base",
    "sklearn.model_selection._split",
    "sklearn.metrics._classification",
    "sklearn.metrics._ranking",
    # ttkbootstrap
    "ttkbootstrap",
    "ttkbootstrap.constants",
    "ttkbootstrap.style",
    "ttkbootstrap.themes",
    "ttkbootstrap.scrolled",
    "ttkbootstrap.widgets",
    "ttkbootstrap.dialogs",
    # data / ML
    "pandas",
    "pandas.core.arrays.integer",
    "pandas.core.arrays.floating",
    "numpy",
    "numpy.core._multiarray_umath",
    "numpy.random",
    "joblib",
    "joblib.externals.loky",
    "joblib.externals.cloudpickle",
    # visualisation
    "matplotlib",
    "matplotlib.backends.backend_tkagg",
    "matplotlib.backends.backend_agg",
    "seaborn",
    # file formats
    "openpyxl",
    "openpyxl.styles",
    "openpyxl.utils",
    # image
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
    # misc
    "scipy",
    "scipy.sparse",
    "scipy.special",
    "scipy.linalg",
    "xgboost",
    "imblearn",
    "tkinter",
    "tkinter.ttk",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "tkinter.font",
]

# =============================================================================
# COLOUR HELPERS  (ANSI for terminal output)
# =============================================================================

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
GREY   = "\033[90m"

def _c(text: str, colour: str) -> str:
    """Wrap text in ANSI colour codes (Windows 10+ supports ANSI in cmd)."""
    return f"{colour}{text}{RESET}"


def _print_header(title: str):
    print()
    print(_c("=" * 65, CYAN))
    print(_c(f"  {title}", BOLD))
    print(_c("=" * 65, CYAN))


def _print_step(msg: str):
    print(f"\n{_c('▶', CYAN)} {msg}")


def _ok(msg: str):
    print(f"  {_c('✅', GREEN)} {msg}")


def _warn(msg: str):
    print(f"  {_c('⚠ ', YELLOW)} {msg}")


def _err(msg: str):
    print(f"  {_c('❌', RED)} {msg}")


def _info(msg: str):
    print(f"  {_c('ℹ', CYAN)} {msg}")


# =============================================================================
# SECTION 1 — ENVIRONMENT CHECKS
# =============================================================================

def check_python_version() -> bool:
    """
    Verify that Python 3.11.x is active.  Warn (but continue) on other versions.
    """
    _print_step("Checking Python version…")
    ver = sys.version_info
    ver_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    print(f"  Python version: {ver_str}")

    if ver.major != 3:
        _err(f"Python 3 is required — found Python {ver.major}.")
        return False

    if (ver.major, ver.minor) < MIN_PYTHON:
        _err(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required — "
             f"found {ver_str}.")
        _info("Download Python 3.11.9: "
              "https://www.python.org/downloads/release/python-3119/")
        return False

    if ver.minor != 11:
        _warn(f"Python 3.11.9 is recommended for PyInstaller compatibility. "
              f"Found {ver_str}.")
        _warn("PyInstaller EXE may not run correctly on Python != 3.11.")
    else:
        _ok(f"Python {ver_str} — compatible.")

    return True


def check_operating_system():
    """Report OS and warn if not Windows (EXE only targets Windows)."""
    _print_step("Checking operating system…")
    os_name = platform.system()
    os_ver  = platform.version()
    arch    = platform.machine()

    print(f"  OS      : {os_name} {os_ver}")
    print(f"  Arch    : {arch}")

    if os_name != "Windows":
        _warn(f"Running on {os_name}. PyInstaller can build on this OS "
              "but the output EXE only runs on Windows.")
        _info("For cross-platform build, install Wine + PyInstaller on Linux, "
              "or use a Windows VM.")
    else:
        _ok("Windows detected — native EXE build supported.")


def check_source_files() -> bool:
    """Verify that App.py and pipeline.py exist in the script directory."""
    _print_step("Checking source files…")
    all_ok = True

    for path, label in [(MAIN_SCRIPT, "App.py"), (PIPELINE_SCRIPT, "pipeline.py")]:
        if path.exists():
            size_kb = path.stat().st_size / 1024
            _ok(f"{label} found  ({size_kb:.1f} KB)")
        else:
            _err(f"{label} NOT FOUND at {path}")
            all_ok = False

    return all_ok


# =============================================================================
# SECTION 2 — PACKAGE INSTALLATION
# =============================================================================

def _is_importable(module_name: str) -> bool:
    """Return True if *module_name* can be imported in the current environment."""
    return importlib.util.find_spec(module_name) is not None


def _pip_install(pip_spec: str) -> bool:
    """
    Run `pip install <pip_spec>` as a subprocess.
    Returns True on success.
    """
    cmd = [sys.executable, "-m", "pip", "install", pip_spec, "--quiet"]
    print(f"    Installing: {pip_spec}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        _err(f"pip install failed for '{pip_spec}':")
        print(result.stderr[-800:] if result.stderr else "(no stderr)")
        return False
    return True


def check_and_install_packages() -> bool:
    """
    Verify every required package is importable; auto-install any that are missing.
    Prints a ✅/❌ checklist.
    Returns True only if all packages end up available.
    """
    _print_step("Checking required packages…")
    print()

    all_ok     = True
    col_width  = max(len(k) for k in REQUIRED_PACKAGES) + 2

    for module_name, pip_spec in REQUIRED_PACKAGES.items():
        available = _is_importable(module_name)

        if available:
            _ok(f"{module_name:{col_width}s} already installed")
        else:
            _warn(f"{module_name:{col_width}s} NOT FOUND — installing…")
            success = _pip_install(pip_spec)
            # Re-check after install
            available = _is_importable(module_name)
            if available:
                _ok(f"{module_name:{col_width}s} installed successfully")
            else:
                _err(f"{module_name:{col_width}s} install FAILED — "
                     f"check your environment and try manually: pip install {pip_spec}")
                all_ok = False

    if all_ok:
        print()
        _ok("All required packages are available.")
    else:
        print()
        _err("One or more packages could not be installed. "
             "Resolve manually before building.")

    return all_ok


# =============================================================================
# SECTION 3 — SPEC FILE GENERATION
# =============================================================================

def _collect_datas() -> list[tuple[str, str]]:
    """
    Build the list of (source_path, dest_folder) tuples for PyInstaller's
    'datas' parameter.  Only includes files that actually exist.
    """
    datas = []

    # pipeline.py (required at runtime — imported by App.py)
    if PIPELINE_SCRIPT.exists():
        datas.append((str(PIPELINE_SCRIPT), "."))

    # Saved model and scaler (if already trained)
    for fname in ("best_model.pkl", "scaler.pkl", "merged_train_data.csv"):
        fpath = SCRIPT_DIR / fname
        if fpath.exists():
            datas.append((str(fpath), "."))

    # Any PNG images in the script directory
    for png in SCRIPT_DIR.glob("*.png"):
        datas.append((str(png), "."))

    # App icon
    if ICON_PATH.exists():
        datas.append((str(ICON_PATH), "."))

    return datas


def generate_spec_file() -> pathlib.Path:
    """
    Dynamically write AgileRisk_AI.spec to the script directory.
    Returns the path to the written spec file.

    FIX: All Windows paths are converted to forward slashes before
    embedding in the .spec file, preventing SyntaxError from backslash
    escape sequences such as backslash-U or backslash-A in path strings.
    """
    _print_step("Generating PyInstaller spec file…")

    datas = _collect_datas()

    # ── Convert every path to forward slashes (Windows fix) ──────────────
    def _fwd(p) -> str:
        return str(p).replace("\\", "/")

    main_script_fwd = _fwd(MAIN_SCRIPT)
    script_dir_fwd  = _fwd(SCRIPT_DIR)
    icon_clause     = f'"{_fwd(ICON_PATH)}"' if ICON_PATH.exists() else "None"

    hidden_str = ",\n    ".join(f'"{h}"' for h in HIDDEN_IMPORTS)
    datas_str  = ",\n    ".join(
        f'("{_fwd(src_p)}", "{dst}")' for src_p, dst in datas
    )

    spec_content = (
        '# ' + '='*77 + '\n'
        '# ' + APP_NAME + '.spec — PyInstaller build specification\n'
        '# Auto-generated by build_exe.py — do NOT edit manually\n'
        '# ' + '='*77 + '\n'
        'import sys\n'
        'from PyInstaller.utils.hooks import collect_submodules, collect_data_files\n'
        '\n'
        'block_cipher = None\n'
        '\n'
        'sklearn_hidden = collect_submodules("sklearn")\n'
        'ttk_hidden     = collect_submodules("ttkbootstrap")\n'
        'mpl_hidden     = collect_submodules("matplotlib")\n'
        '\n'
        'all_hidden = sklearn_hidden + ttk_hidden + mpl_hidden + [\n'
        f'    {hidden_str},\n'
        ']\n'
        '\n'
        'a = Analysis(\n'
        f'    ["{main_script_fwd}"],\n'
        f'    pathex=["{script_dir_fwd}"],\n'
        '    binaries=[],\n'
        '    datas=[\n'
        f'    {datas_str},\n'
        '    ],\n'
        '    hiddenimports=all_hidden,\n'
        '    hookspath=[],\n'
        '    hooksconfig={},\n'
        '    runtime_hooks=[],\n'
        '    excludes=["PyQt5","PyQt6","PySide2","PySide6","wx","gtk","gi","test","unittest"],\n'
        '    win_no_prefer_redirects=False,\n'
        '    win_private_assemblies=False,\n'
        '    cipher=block_cipher,\n'
        '    noarchive=False,\n'
        ')\n'
        '\n'
        'pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)\n'
        '\n'
        'exe = EXE(\n'
        '    pyz,\n'
        '    a.scripts,\n'
        '    a.binaries,\n'
        '    a.zipfiles,\n'
        '    a.datas,\n'
        '    [],\n'
        f'    name="{APP_NAME}",\n'
        '    debug=False,\n'
        '    bootloader_ignore_signals=False,\n'
        '    strip=False,\n'
        '    upx=True,\n'
        '    upx_exclude=[],\n'
        '    runtime_tmpdir=None,\n'
        '    console=False,\n'
        '    disable_windowed_traceback=False,\n'
        '    argv_emulation=False,\n'
        '    target_arch=None,\n'
        '    codesign_identity=None,\n'
        '    entitlements_file=None,\n'
        f'    icon={icon_clause},\n'
        '    onefile=True,\n'
        ')\n'
    )

    SPEC_FILE.write_text(spec_content, encoding="utf-8")
    _ok(f"Spec file written \u2192 {SPEC_FILE}")
    _info("  Paths use forward slashes (Windows backslash escape fix)")
    _info(f"  datas bundled: {len(datas)} file(s)")

    if not ICON_PATH.exists():
        _warn("app_icon.ico not found \u2014 building without custom icon.")

    return SPEC_FILE


# =============================================================================
# SECTION 4 — BUILD EXECUTION
# =============================================================================

def run_pyinstaller(spec_path: pathlib.Path) -> bool:
    """
    Execute PyInstaller with the generated spec file.
    Streams stdout/stderr to the terminal in real time.

    Returns True if the EXE was created successfully.
    """
    _print_step("Running PyInstaller…")
    print(f"  Spec : {spec_path}")
    print(f"  This may take 2–5 minutes depending on your hardware.\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--noconfirm",
        "--log-level", "WARN",
    ]

    print(_c("  ── PyInstaller output ──────────────────────────────────", GREY))
    t_start = time.time()

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # Stream output line by line
    assert proc.stdout is not None
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            # Colour-code PyInstaller WARNING and ERROR lines
            if "ERROR" in line or "error" in line.lower():
                print(_c(f"  {line}", RED))
            elif "WARNING" in line or "warn" in line.lower():
                print(_c(f"  {line}", YELLOW))
            else:
                print(_c(f"  {line}", GREY))

    proc.wait()
    elapsed = time.time() - t_start
    print(_c("  ── end of PyInstaller output ───────────────────────────", GREY))
    print()

    if proc.returncode != 0:
        _err(f"PyInstaller exited with code {proc.returncode} after {elapsed:.1f}s.")
        return False

    _ok(f"PyInstaller finished in {elapsed:.1f}s.")
    return True


def verify_exe() -> bool:
    """
    Check that the EXE was actually created and report its size.
    Returns True if EXE exists.
    """
    _print_step("Verifying output EXE…")

    if EXE_PATH.exists():
        size_bytes = EXE_PATH.stat().st_size
        size_mb    = size_bytes / (1024 * 1024)
        _ok(f"EXE found: {EXE_PATH}")
        _ok(f"File size: {size_mb:.1f} MB  ({size_bytes:,} bytes)")
        return True
    else:
        _err(f"EXE NOT found at expected path: {EXE_PATH}")
        _info("Check build/ and dist/ directories for error details.")
        _info("Re-run with --log-level DEBUG for verbose PyInstaller output.")
        return False


# =============================================================================
# SECTION 5 — POST-BUILD CHECKLIST
# =============================================================================

def post_build_checklist():
    """
    Print a checklist of files that must be distributed alongside the EXE,
    and check which of them already exist in the dist directory.
    """
    _print_header("POST-BUILD DISTRIBUTION CHECKLIST")

    dist_dir = DIST_DIR
    print(f"\n  EXE location: {EXE_PATH}\n")

    required_alongside = [
        ("best_model.pkl",          "Trained ML model (generate by running pipeline.py first)"),
        ("scaler.pkl",              "Feature scaler (generated with best_model.pkl)"),
        ("merged_train_data.csv",   "Merged training data (optional — for retraining)"),
        ("app_icon.ico",            "Application icon (optional — cosmetic only)"),
    ]

    print("  Files that MUST be copied to the same folder as the EXE:")
    print("  " + "─" * 60)

    for filename, description in required_alongside:
        src_path  = SCRIPT_DIR / filename
        dist_path = dist_dir   / filename
        src_exists  = src_path.exists()
        dist_exists = dist_path.exists()

        if dist_exists:
            status = _c("✅ already in dist/", GREEN)
        elif src_exists:
            status = _c("⚠  copy from project root to dist/", YELLOW)
        else:
            status = _c("❌ NOT YET GENERATED — create before distributing", RED)

        print(f"  {filename:30s} {status}")
        print(f"  {'':30s} → {description}")

    print()
    print(_c("  HOW TO COPY REQUIRED FILES:", BOLD))
    print(f"  xcopy best_model.pkl   \"{dist_dir}\\\" /Y")
    print(f"  xcopy scaler.pkl       \"{dist_dir}\\\" /Y")
    print()
    print(_c("  ANTIVIRUS NOTE:", YELLOW))
    print("  PyInstaller EXEs may trigger Windows Defender false positives.")
    print("  To whitelist: Windows Security → Virus & Threat Protection")
    print("  → Manage Settings → Exclusions → Add an exclusion → File")
    print(f"  → Select: {EXE_PATH}")
    print()
    print(_c("  DISTRIBUTION:", CYAN))
    print(f"  Share the entire '{DIST_DIR.name}/' folder.")
    print("  The target machine does NOT need Python installed.")


# =============================================================================
# SECTION 6 — CLEAN BUILD
# =============================================================================

def clean_build(no_confirm: bool = False):
    """
    Remove build/, dist/, __pycache__/ directories and *.spec files.
    Prompts for confirmation unless no_confirm=True.
    """
    _print_header("CLEAN BUILD ARTEFACTS")

    targets = []
    if BUILD_DIR.exists():
        targets.append(BUILD_DIR)
    if DIST_DIR.exists():
        targets.append(DIST_DIR)
    if SPEC_FILE.exists():
        targets.append(SPEC_FILE)

    # __pycache__ directories anywhere under SCRIPT_DIR
    pycache_dirs = list(SCRIPT_DIR.rglob("__pycache__"))
    targets.extend(pycache_dirs)

    # Any stray .pyc files
    pyc_files = list(SCRIPT_DIR.rglob("*.pyc"))
    targets.extend(pyc_files)

    if not targets:
        _info("Nothing to clean — working directory is already tidy.")
        return

    print(f"\n  The following will be DELETED:")
    for t in targets:
        rel = t.relative_to(SCRIPT_DIR)
        print(f"    {'📁' if t.is_dir() else '📄'}  {rel}")

    if not no_confirm:
        print()
        answer = input(_c("  Proceed with deletion? [y/N]: ", YELLOW)).strip().lower()
        if answer not in ("y", "yes"):
            _info("Clean cancelled.")
            return

    print()
    deleted_count = 0
    for t in targets:
        try:
            if t.is_dir():
                shutil.rmtree(t)
            else:
                t.unlink()
            deleted_count += 1
        except Exception as exc:
            _warn(f"Could not delete {t}: {exc}")

    _ok(f"Cleaned {deleted_count} item(s).")


# =============================================================================
# SECTION 7 — FULL BUILD ORCHESTRATION
# =============================================================================

def full_build(no_confirm: bool = False) -> bool:
    """
    Run the complete build sequence:
      1. Check Python version
      2. Check OS
      3. Check source files
      4. Check/install packages
      5. Generate spec file
      6. Run PyInstaller
      7. Verify EXE
      8. Post-build checklist

    Returns True if the build succeeded.
    """
    t_total = time.time()

    _print_header(f"AgileRisk AI — Windows EXE Builder  [{APP_NAME}]")
    print(f"  Script dir : {SCRIPT_DIR}")
    print(f"  Output EXE : {EXE_PATH}")
    print(f"  Timestamp  : {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # ── Step 1: Python version ────────────────────────────────────────────────
    if not check_python_version():
        _err("Build aborted: unsupported Python version.")
        return False

    # ── Step 2: OS ────────────────────────────────────────────────────────────
    check_operating_system()

    # ── Step 3: Source files ──────────────────────────────────────────────────
    if not check_source_files():
        _err("Build aborted: source files missing.")
        return False

    # ── Step 4: Packages ──────────────────────────────────────────────────────
    if not check_and_install_packages():
        _err("Build aborted: package installation failed.")
        return False

    # ── Step 5: Generate spec ─────────────────────────────────────────────────
    spec_path = generate_spec_file()

    # ── Step 6: Run PyInstaller ───────────────────────────────────────────────
    build_ok = run_pyinstaller(spec_path)
    if not build_ok:
        _err("PyInstaller build failed.")
        _info("Common fixes:")
        _info("  1. Run:  pip install pyinstaller-hooks-contrib")
        _info("  2. Add 'import sys; sys.setrecursionlimit(5000)' to App.py top")
        _info("  3. Ensure no syntax errors: python App.py")
        _info("  4. Try:  python build_exe.py --clean  then rebuild")
        return False

    # ── Step 7: Verify EXE ────────────────────────────────────────────────────
    exe_ok = verify_exe()

    # ── Step 8: Post-build checklist ──────────────────────────────────────────
    if exe_ok:
        post_build_checklist()

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed_total = time.time() - t_total
    print()
    _print_header("BUILD SUMMARY")
    if exe_ok:
        print()
        _ok(f"BUILD SUCCEEDED in {elapsed_total:.1f}s")
        _ok(f"EXE path: {EXE_PATH}")
        _info("Next steps:")
        _info(f"  1. Copy best_model.pkl and scaler.pkl to {DIST_DIR}")
        _info(f"  2. Double-click {EXE_PATH.name} to launch AgileRisk AI")
        _info("  3. No Python installation needed on target machine")
    else:
        _err(f"BUILD FAILED after {elapsed_total:.1f}s")
        _info("Review the PyInstaller output above for specific errors.")

    return exe_ok


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="build_exe.py",
        description=(
            "AgileRisk AI — Build Script\n"
            "Packages App.py + pipeline.py into a standalone Windows EXE "
            "using PyInstaller 6.x.\n\n"
            "Examples:\n"
            "  python build_exe.py               # full build\n"
            "  python build_exe.py --clean       # remove build artefacts\n"
            "  python build_exe.py --no-confirm  # clean without prompting\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete build/, dist/, __pycache__/, and *.spec files then exit.",
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        dest="no_confirm",
        help="Skip the deletion confirmation prompt when used with --clean.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        dest="check_only",
        help="Run environment checks and package audit only — do not build.",
    )

    args = parser.parse_args()

    if args.clean:
        clean_build(no_confirm=args.no_confirm)
        sys.exit(0)

    if args.check_only:
        _print_header("AgileRisk AI — Environment Check")
        check_python_version()
        check_operating_system()
        check_source_files()
        check_and_install_packages()
        sys.exit(0)

    # Default: full build
    success = full_build(no_confirm=args.no_confirm)
    sys.exit(0 if success else 1)
