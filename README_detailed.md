# Research lohher (hrlogger_v2)

## Overview

This tool is **designed for researchers/programmers/software developers** to log their work in a structured way, allowing for easy export to Markdown, HTML, and PDF formats. Specially useful for those who want to **maintain a chronological record of their research activities**, thoughts, and progress.

If you are a researcher/programmer/software developer who values organized documentation and wants a simple way to keep track of your work, this tool can be a great asset. It is particularly beneficial for those who want to create a research diary or logbook that can be easily shared or published. **Specially if you are working on many proejects and you often switch between them and always forget where in which diroectory you are working on**, this tool can help you keep track of your work across different projects and directories. By logging your activities with timestamps, you can easily see what you have done and when, which can be very helpful for project management and reflection.

### Key Features

It can be used for daily diary, daily research logs, project updates, or any kind of note-taking that benefits from a timestamped format.
 
It is designed to be simple and flexible, allowing you to log entries with a single command and then export them in various formats for sharing or publication. The tool is cross-platform, working on macOS, Linux, and Windows, making it accessible to a wide range of researchers regardless of their operating system.

See also [MANUAL_hResearchLogger.md](MANUAL_hResearchLogger.md) for setup and usage instructions.

### Other Notes

- This file is for the update information of `hrlogger`. The original version is in the `py_hrlogger` branch, and this `hrlogger_v2` repo contains the new version with cross-platform support and improved features.

- If this repo contains the following directories, please ignore them: `sample_data/`, `run/`, `old_versions/`

- Cross-platform logging/export workflow for **macOS**, **Linux**, and **Windows** using Conda.

## SETUP & INSTALLATION

for details see [MANUAL_hrLogger.md](MANUAL_hrLogger.md).

- Optional but recommended: Create and activate the Conda environment for HTML/PDF export features.

- cp python files to your desired location and add to PATH or use shell shortcuts (documented in the manual).

- cop bash/zsh/powershell shortcuts to your shell profile for easy logging (documented in the manual).

## BASIC COMMANDS & USAGE

### List of available commands in shell (after setup):
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

### Viewing saved logs:

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



### Example usage in shell:

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

### Exporting reports (Markdown/HTML/PDF)

- for conversion to markdown/html/pdf, see the Python scripts and usage instructions in the manual.
- run `hrlog2md` without arguments to see usage instructions for conversion and export options.

```bash
hrlog2md
```

above cmd will print usage instructions like:

```
Usage: hrlog2md input_file [output_file] [--format md|html|pdf] [--css style.css] [--time-ranges range1,range2,...]

Some Examples are:
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


## MORE ON EXPORTING LOGS

### 1) Convert log to Markdown

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.md --format md
```

Convert directly to HTML (uses shared style file):

```bash
python hrlogin2md.py "$HOME/.hrloginfo" run/hrloginfo.html --format html --css hrlogin_style.css
```

### 2) Export PDF (cross-platform)

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
