# py_hrlogger_v2

This file is for the update information of py_hrlogger. The original version is in the `py_hrlogger` branch, and this `py_hrlogger_v2` branch contains the new version with cross-platform support and improved features.

See [MANUAL_hResearchLogger.md](MANUAL_hResearchLogger.md) for setup and usage instructions.

If this die contains following directories, Ignore them: sample_data/, run/, old_versions/

Cross-platform logging/export workflow for macOS, Linux, and Windows using Conda.

For Windows PowerShell shell shortcuts, use [powershell_hrlogin.ps1](powershell_hrlogin.ps1) via `$PROFILE` (documented in the manual).

## 1) Create environment

```bash
conda env create -f environment.yml
conda activate py-hrlogger
```

## 2) Log an entry

```bash
python hrloginv2.py "implemented feature X"
```

You can set a custom log file:

```bash
# macOS/Linux
export HRLOG_FILE="$HOME/.hrloginfo"

# Windows PowerShell
$env:HRLOG_FILE = "$HOME/.hrloginfo"
```

## 3) Convert log to Markdown

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.md --format md
```

Convert directly to HTML (uses shared style file):

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.html --format html --css hrlogin_style.css
```

## 4) Export PDF (cross-platform)

Use the built-in converter:

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.pdf --format pdf --css hrlogin_style.css
```

PDF backend behavior:

- Primary: `pdfkit` + `wkhtmltopdf` binary (best rendering)
- Fallback: `xhtml2pdf` if `wkhtmltopdf` is not installed

Alternative (`pandoc` + TeX) is still available:

```bash
cd run
pandoc ./hrloginfo.md -o output.pdf --pdf-engine=tectonic -H ../header.tex --toc --toc-depth=3 --number-sections
```

## Notes

- `hrlogin.py` and `hrloginv2.py` now use cross-platform file locking (`portalocker`).
- `hrlogin2md.py` reads shared style from `hrlogin_style.css` for both HTML and PDF.
- If running in a specific conda env, prefer: `conda run -n <env> python ...`
- HTML/PDF Python deps: `markdown2`, `pdfkit`, `xhtml2pdf` (install in your active env).
- Optional system dependency: `wkhtmltopdf` binary for higher-fidelity PDF rendering.
- If you prefer `lualatex`, install a TeX distribution separately on each OS and switch `--pdf-engine`.
- `bash_hrlogin` and `zsh_hrlogin` are shell-specific helpers; the Python commands above are cross-platform.

## Publish checklist

- Include `environment.yml`
- Include this `README.md`
- Include `hrlogin_style.css`
- Exclude runtime output files (`run/*.pdf`, `run/*.html`) if you want a clean repository
