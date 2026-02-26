# Installation Manual (Conda (Optional) + Shell Integration (compulsory) )

This manual shows how to set up `py_hrlogger_v2` on macOS, Linux, and Windows.

For setup follow the instructions below ( `1.` is optional installation, `2.` is for setup, `3.` is for shell integration, `4.` is for log configuration, `5.` is for basic usage). Steps `2.` and `3.` are complementary for setup.  In step `3.`, you can choose either Method-I or Method-II for shell integration (Method-I is recommended for better separation of concerns).

## 0) File overview and structure

- `hrloginv2.py` is the active logger script.
- `hrlogin.py` is **obsolete** (kept only for backward compatibility).
- `hrlogin2md.py` converts raw logs to markdown/html/pdf.
- `hrlogin_style.css` is the shared style file used by both HTML and PDF outputs.
- `header.tex` is used for PDF exports via Pandoc for consistent styling.

## 1) **Optional Installation** Create the Conda environment

This step is important if you want to use the HTML/PDF export features. For simple logging, you can use any Python environment (see next session for Setup). 

** For macOS/Linux users**:

From the project root:

```bash
conda env create -f environment.yml
conda activate py-hrlogger
```

** For Windows users**:

For Windows PowerShell shell shortcuts, use [powershell_hrlogin.ps1](powershell_hrlogin.ps1) via `$PROFILE` (documented in the manual).

you need to use `py-hrlogger` environment for exporting to HTML/PDF, but you can log entries with any Python environment as long as it has access to the log file.

Install/verify converter dependencies in the active env:

```bash
pip install markdown2 pdfkit xhtml2pdf
```

Optional (better PDF fidelity): install `wkhtmltopdf` system binary.

## 2) **Setup**: install scripts into ~/.local/bin (macOS/Linux)

This gives stable command paths and lets shell functions call scripts from anywhere.

```bash
mkdir -p ~/.local/bin
cp hrloginv2.py ~/.local/bin/hrloginv2.py
cp hrlogin2md.py ~/.local/bin/hrlogin2md.py
cp hrlogin_style.css ~/.local/bin/hrlogin_style.css
cp header.tex ~/.local/bin/header.tex
chmod +x ~/.local/bin/hrloginv2.py ~/.local/bin/hrlogin2md.py
```

Ensure `~/.local/bin` is on PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add that (above) PATH line to `~/.bashrc` or `~/.zshrc` if needed.

## 3) **Setup**: Setup shell commands (bash/zsh)

use one of the methods below to integrate the helper functions into your shell environment. These functions provide convenient commands like `hrlogin`, `hrrecent`, `hrdate`, `hrrange`, and `hrsearch` for managing your logs directly from the terminal. **My suggested method is Method-I** for better separation, but Method-II works fine too if you prefer everything in one file.


### A- Method-I: Use seprate source file (bash_hrlogin or zsh_hrlogin)

copy the appropriate helper file to your home directory:

```bash
# bash
cp bash_hrlogin ~/.bash_hrlogin

or if you are using zsh:
# zsh
cp zsh_hrlogin ~/.zsh_hrlogin
```

Then source it in your shell :

```bash
# bash
source ~/.bash_hrlogin

# zsh
source ~/.zsh_hrlogin
```



### B- Method-II: Use defaults shell source files

Choose one which shell profile you use and append the helper functions to it:

Forexample:
- bash: `~/.bashrc`
- zsh: `~/.zshrc`

Append one of the helper files:

```bash
# bash
cat bash_hrlogin >> ~/.bashrc
source ~/.bashrc

# zsh
cat zsh_hrlogin >> ~/.zshrc
source ~/.zshrc
```

After this, commands like `hrlogin`, `hrrecent`, `hrdate`, `hrrange`, `hrsearch` are available in your shell.


## 4) Configure log location (optional)

Default file is `~/.hrloginfo`. To customize:

```bash
# macOS/Linux
export HRLOG_FILE="$HOME/.hrloginfo"
```

PowerShell (Windows):

```powershell
$env:HRLOG_FILE = "$HOME/.hrloginfo"
```

## 5) Basic usage

Log an item:

```bash
hrlogin "implemented feature X"
```

Or directly via Python:

```bash
python hrloginv2.py "implemented feature X"
```

Convert to markdown:

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.md --format md
```

Convert to HTML (shared CSS):

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.html --format html --css hrlogin_style.css
```

Convert to PDF (shared CSS):

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.pdf --format pdf --css hrlogin_style.css
```

PDF engine behavior:

- Uses `wkhtmltopdf` via `pdfkit` when available.
- Automatically falls back to `xhtml2pdf` when `wkhtmltopdf` is not installed.
- For strict env usage: `conda run -n <env_name> python hrlogin2md.py ...`

Export PDF (portable):

```bash
cd run
pandoc ./hrloginfo.md -o output.pdf --pdf-engine=tectonic -H ../header.tex --toc --toc-depth=3 --number-sections
```

## 6) Windows notes

- `~/.local/bin` and `bash_hrlogin`/`zsh_hrlogin` are Unix-shell oriented.
- On Windows, prefer direct Python commands in PowerShell, or use Git Bash/WSL for shell-function workflows.
- or use the provided `powershell_hrlogin.ps1` for PowerShell integration (documented in the manual).
- Cross-platform runtime is handled by Conda + Python scripts.

### Setup PowerShell profile commands

Run in PowerShell:

```powershell
if (!(Test-Path $PROFILE)) { New-Item -Type File -Path $PROFILE -Force }
Add-Content -Path $PROFILE -Value ". '$PWD/powershell_hrlogin.ps1'"
. $PROFILE
```

After that, use commands:

- `hrlogin "message"`
- `hrlog2md`
- `hrlog2pdf`
- `hrlog2html`
- `hrhelp`

## 7) Publishing checklist

- Keep in repo: `environment.yml`, `README.md`, `MANUAL_hResearchLogger.md`, Python scripts, `hrlogin_style.css`, `header.tex`, `powershell_hrlogin.ps1`.
- Keep out of repo: generated outputs (`run/*.pdf`, `run/*.html`, etc.) via `.gitignore`.
- Mention in release notes: `hrlogin.py` is obsolete; use `hrloginv2.py`.



# Usage manual

## List of available commands in shell (after setup):
<!--
Logging:
  hrlogin 'description'     - Log an entry in current directory

Viewing:
  hrview                    - View entire log file
  hrlist [asc|desc]         - List all entries sorted by datetime (default: desc)
  hrrecent [N]              - Show last N entries (default: 10)
  
Search:
  hrsearch <keyword>        - Search for keyword (with context)
  hrcontext <keyword>       - Search with full section hierarchy
  
Date-based:
  hrtoday                   - Show today's entries
  hrdate YYYYMMDD           - Show entries from specific date
  hrdate YYYYMMDD.HHMM      - Show entries from specific datetime
  hrrange START END         - Show entries in date/datetime range
  hrweek                    - Show this week's entries
  hrmonth                   - Show this month's entries
  hrhour YYYYMMDD HH [HH]   - Show entries for specific hour(s)
  
Analysis:
  hrstats                   - Show statistics summary
  hrhelp                    - Show this help

Environment:
  HRLOG_FILE               - Set custom log file path (default: ~/.hrloginfo)

Installation:
  copy hrloginv2.py ~/.local/bin/
  chmod +x ~/.local/bin/hrloginv2.py
-->

### Logging:
- `hrlogin "message"`: Log a new entry with the given message.

### Viewing:
- `hrview`: View the entire log file.
- `hrlist [asc|desc]`: List all entries sorted by datetime (default:
- `hrrecent [N]`: Show the most recent N log entries (default 10).
- `hrtoday`: Show all entries from today.
- `hrdate YYYY-MM-DD`: Show all entries from the specified date.
- `hrdate YYYY-MM-DD.HHMM`: Show the entry from the specific datetime (if it exists).
- `hrrange YYYY-MM-DD YYYY-MM-DD`: Show entries within the date range.
- `hrhour YYYY-MM-DD HH [HH]`: Show entries for a specific hour or range of hours.
- `hrweek`: Show entries from the past 7 days.
- `hrmonth`: Show entries from the past 30 days.
- `hrsearch "keyword"`: Search for entries containing the keyword (with context).
- `hrcontext "keyword"`: Search for entries with full section hierarchy context.
- `hrstats`: Show statistics like total entries, entries per day, etc.
- `hrhelp`: Show the help message with available commands and usage instructions.
  
- `hrbackup`: Create a timestamped backup of the log file.
- `hrrestore "backup_file"`: Restore log file from a specified backup.
- `hrlog2md`: Convert the log file to markdown format (calls `hrlogin2md.py`).
- `hrlog2pdf`: Convert the log file to PDF format (calls `hrlogin2md.py` + `pandoc`).
- `hrlog2html`: Convert the log file to HTML format (calls `hrlogin2md.py`).
- `hrlog2md --format md|pdf|html`: Specify output format for conversion.
- `hrlog2pdf --pdf-engine tectonic|lualatex`: Specify PDF engine for PDF export.



## Example usage in shell:

<!--

Environment:
  HRLOG_FILE               - Set custom log file path (default: ~/.hrloginfo)

Installation:
  copy hrloginv2.py ~/.local/bin/
  chmod +x ~/.local/bin/hrloginv2.py

Examples:
  hrlogin 'fixed MPI bug in boundary conditions'
  hrrecent 20
  hrsearch 'equilibrium'
  hrdate 20251211                    # All entries on Dec 11
  hrdate 20251211.1430               # Specific entry at 2:30pm
  hrrange 20251201 20251210          # Date range
  hrrange 20251211.0900 20251211.1700  # Time range (9am-5pm)
  hrhour 20251211 14                 # All entries in 2pm hour
  hrhour 20251211 09 17              # Entries between 9am-5pm

ProUsage - Combine with other tools:
  hrlist | grep 'MPI'              # Search in sorted list
  hrrecent 50 | grep '20251210'    # Recent entries from specific date
  hrtoday | wc -l                  # Count today's entries
  hrdate 20251211 | grep -E '\.(09|10|11)[0-9]{2}:'  # Morning entries only

-->


```bash
# Example usage in shell:
# Log a new entry
hrlogin "fixed MPI bug in boundary conditions"
# vierw entire log
hrview
# View 50 recent entries
hrrecent 50
# Search for keyword
hrsearch "equilibrium"
# Show entries from specific date
hrdate 20251211
# Show entry from specific datetime
hrdate 20251211.1430
# Show entries in date range
hrrange 20251201 20251210
# Show entries in time range
hrrange 20251211.0900 20251211.1700
# Show entries in specific hour
hrhour 20251211 14
# Show entries between 9am-5pm
hrhour 20251211 09 17

# Pro usage - Combine with other tools:
# Combine with other tools
hrlist | grep 'MPI'              # Search in sorted list
hrrecent 50 | grep '20251210'    # Recent entries from specific date
hrtoday | wc -l                  # Count today's entries    
hrdate 20251211 | grep -E '\.(09|10|11)[0-9]{2}:'  # Morning entries only

```

# for conversion to markdown/html/pdf, see the Python scripts and usage instructions in the manual.
# run hrlog2md without arguments to see usage instructions for conversion and export options.
```bash
hrlog2md
```
it will print usage instructions like:
```Usage: hrlog2md input_file [output_file] [--format md|html|pdf] [--css style.css] [--time-ranges range1,range2,...]
Examples:
  python hrlogin2md.py notes.txt output.md --format md
  python hrlogin2md.py notes.txt output.html --format html
  python hrlogin2md.py notes.txt output.pdf --format pdf
  python hrlogin2md.py notes.txt output.html --format html --css hrlogin_style.css
  python hrlogin2md.py notes.txt output.pdf --format pdf --css hrlogin_style.css
  python hrlogin2md.py notes.md output.html --format html --css hrlogin_style.css
  python hrlogin2md.py notes.md output.pdf --format pdf --css hrlogin_style.css
  python hrlogin2md.py notes.md --format pdf  # auto-names output 
  ---------------------------------------------------
  markdown-pdf input.md
  pandoc input.md -o output.html --standalone
  pandoc input.md -o output.pdf --pdf-engine=tectonic -H header.tex --toc --toc-depth=3 --number-sections
  pandoc hrloginfo.md -o hrloginfo.pdf --pdf-engine=xelatex -H ~/.local/bin/header.tex --toc --toc-depth=3 --number-sections
```

