# Research Logger (`hrlogger_v2`)

A structured, cross-platform research logging system for researchers,
programmers, and developers.

------------------------------------------------------------------------

## Overview

**Research Logger (`hrlogger_v2`)** is designed for researchers,
programmers, and software developers who want to maintain a structured,
chronological record of their work.

It allows you to log activities in a consistent format and export them
to **Markdown, HTML, or PDF**, making it suitable for documentation,
reporting, publication, or archival purposes.

This tool is especially useful if you:

-   Work on multiple projects simultaneously\
-   Frequently switch between directories\
-   Want to maintain a professional research diary\
-   Need timestamped records for reports or publications\
-   Value organized and reproducible documentation

Each entry is logged with a timestamp, allowing you to clearly see
**what was done and when**.

------------------------------------------------------------------------

## Key Features

-   Timestamped logging with a single command\
-   Chronological record of research and development activities\
-   Multi-project friendly (works naturally across directories)\
-   Search and filter by date, time, or keyword\
-   Export logs to **Markdown, HTML, and PDF**\
-   Cross-platform support (macOS, Linux, Windows)\
-   Backup and restore functionality\
-   Statistical summaries of activity

------------------------------------------------------------------------

## Repository Notes

-   This repository contains the updated version (`hrlogger_v2`) with
    improved cross-platform support and enhanced export capabilities.
-   The original implementation is available in the `py_hrlogger`
    branch.
-   If present, the following directories are for development or
    examples and can be ignored:
    -   `sample_data/`
    -   `run/`
    -   `old_versions/`

------------------------------------------------------------------------

# SETUP & INSTALLATION

For detailed instructions, see:

`MANUAL_hrLogger.md`

### Basic Installation Notes

-   Optionally (recommended): Create and activate a Conda environment
    for HTML/PDF export features.
-   Copy Python files to your desired location and add them to your
    `PATH`, or use shell shortcuts.
-   Copy bash/zsh/powershell shortcuts to your shell profile for
    convenient command usage.

------------------------------------------------------------------------

# BASIC COMMANDS & USAGE

## Logging

-   `hrlogin "message"`: Log a new entry with the given message.

------------------------------------------------------------------------

## Viewing Saved Logs

-   `hrview`
-   `hrlist [asc|desc]`
-   `hrrecent [N]`
-   `hrtoday`
-   `hrdate YYYY-MM-DD`
-   `hrdate YYYY-MM-DD.HHMM`
-   `hrrange YYYY-MM-DD YYYY-MM-DD`
-   `hrhour YYYY-MM-DD HH [HH]`
-   `hrweek`
-   `hrmonth`
-   `hrsearch "keyword"`
-   `hrcontext "keyword"`
-   `hrstats`
-   `hrhelp`
-   `hrbackup`
-   `hrrestore "backup_file"`

------------------------------------------------------------------------

## Example Usage

``` bash
# Log a new entry
hrlogin "fixed MPI bug in boundary conditions"

# View entire log
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

# Pro usage
hrlist | grep 'MPI'
hrrecent 50 | grep '20251210'
hrtoday | wc -l
hrdate 20251211 | grep -E '\.(09|10|11)[0-9]{2}:'
```

------------------------------------------------------------------------

# Exporting Reports (Markdown / HTML / PDF)

Run:

``` bash
hrlog2md
```

Follow the printed usage instructions for conversion and export options.

------------------------------------------------------------------------

## Notes

-   Uses cross-platform file locking (`portalocker`).
-   HTML/PDF Python dependencies: `markdown2`, `pdfkit`, `xhtml2pdf`.
-   Optional system dependency: `wkhtmltopdf` for high-quality PDF
    rendering.
-   TeX-based PDF export via `pandoc` is supported.
-   Compatible with Conda environments.
