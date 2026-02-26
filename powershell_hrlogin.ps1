function hrlogin {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Description
    )

    if (-not $Description -or $Description.Count -eq 0) {
        Write-Host "[hrlogin] Usage: hrlogin 'description'"
        return
    }

    python "$PSScriptRoot/hrloginv2.py" ($Description -join ' ')
}

function hrlog2md {
    param(
        [string]$InputFile = "$HOME/.hrloginfo",
        [string]$OutputFile = "$PSScriptRoot/run/hrloginfo.md"
    )

    python "$PSScriptRoot/hrlogin2md.py" $InputFile $OutputFile --format md
}

function hrlog2pdf {
    param(
        [string]$InputFile = "$HOME/.hrloginfo",
        [string]$RunDir = "$PSScriptRoot/run"
    )

    python "$PSScriptRoot/hrlogin2md.py" $InputFile "$RunDir/hrloginfo.md" --format md
    Push-Location $RunDir
    try {
        pandoc ./hrloginfo.md -o output.pdf --pdf-engine=tectonic -H ../header.tex --toc --toc-depth=3 --number-sections
    }
    finally {
        Pop-Location
    }
}

function hrlog2html {
    param(
        [string]$InputFile = "$HOME/.hrloginfo",
        [string]$OutputFile = "$PSScriptRoot/run/hrloginfo.html"
    )

    python "$PSScriptRoot/hrlogin2md.py" $InputFile $OutputFile --format html
}

function hrhelp {
    Write-Host "=== hrlogin PowerShell Commands ==="
    Write-Host "hrlogin <text>        - Log an entry"
    Write-Host "hrlog2md [in] [out]   - Convert log to markdown"
    Write-Host "hrlog2pdf [in] [dir]  - Convert log to markdown + PDF"
    Write-Host "hrlog2html [in] [out] - Convert log to HTML"
}
