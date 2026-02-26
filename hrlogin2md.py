#!/usr/bin/env python3
"""
Convert text file to clean markdown format and optionally to HTML/PDF.
Usage: python hrlogin2md.py input_file [output_file] [--format md|html|pdf]
"""

import sys
import os
import re
import shutil
from datetime import datetime

DEFAULT_RECENCY_RANGES = (1440, 2880, 10080, 20160, 30240)
DEFAULT_CSS_FILE = os.path.join(os.path.dirname(__file__), 'hrlogin_style.css')

def wrap_windows_paths(text):
    """Wrap Windows-style paths (e.g., C:\\Users\\name) in markdown inline code."""
    windows_path_pattern = re.compile(r'(?<!`)([A-Za-z]:\\[^\s`]+)(?!`)')
    return windows_path_pattern.sub(r'`\1`', text)


def parse_time_tag(time_tag):
    """Parse YYYYMMDD.HHMM: timestamp into datetime, returning None if invalid."""
    try:
        return datetime.strptime(time_tag.rstrip(':'), '%Y%m%d.%H%M')
    except ValueError:
        return None


def recency_class(timestamp, newest_timestamp, ranges):
    """Map a timestamp to a recency bucket based on newest timestamp and minute ranges."""
    delta_minutes = max(0, int((newest_timestamp - timestamp).total_seconds() // 60))
    if delta_minutes <= ranges[0]:
        return 'recency-now'
    if delta_minutes <= ranges[1]:
        return 'recency-recent'
    if delta_minutes <= ranges[2]:
        return 'recency-day'
    if delta_minutes <= ranges[3]:
        return 'recency-week'
    return 'recency-old'


def period_label(timestamp, reference_time):
    """Classify timestamp into TODAY/YESTER/WEEK*/MONTH* buckets from current time."""
    delta_minutes = max(0, int((reference_time - timestamp).total_seconds() // 60))
    delta_days = delta_minutes / 1440.0

    if delta_days <= 1:
        return 'TODAY'
    if delta_days <= 2:
        return 'YESTER'
    if delta_days <= 7:
        return 'WEEK'
    if delta_days <= 14:
        return 'WEEK2'
    if delta_days <= 21:
        return 'WEEK3'
    if delta_days <= 28:
        return 'WEEK4'
    if delta_days <= 60:
        return 'MONTH1'
    if delta_days <= 90:
        return 'MONTH2'

    month_index = int((delta_days - 90 - 1e-9) // 30) + 3
    return f'MONTH{month_index}'


def jet_color_hex(normalized_age):
    """Return a Jet-like color hex for a normalized age value in [0, 1]."""
    x = max(0.0, min(1.0, float(normalized_age)))

    def channel(v):
        value = 1.5 - abs(4.0 * x - v)
        return int(max(0.0, min(1.0, value)) * 255)

    r = channel(3.0)
    g = channel(2.0)
    b = channel(1.0)
    return f"#{r:02x}{g:02x}{b:02x}"


def parse_time_ranges(range_text):
    """
    Parse --time-ranges text into 5 ascending minute thresholds.
    Expected format: m1,m2,m3,m4,m5 (e.g. 1440,2880,10080,20160,30240)
    """
    parts = [part.strip() for part in range_text.split(',') if part.strip()]
    if len(parts) != 5:
        raise ValueError("--time-ranges must contain exactly 5 comma-separated values")

    try:
        values = tuple(int(part) for part in parts)
    except ValueError as exc:
        raise ValueError("--time-ranges values must be integers (minutes)") from exc

    if any(value <= 0 for value in values):
        raise ValueError("--time-ranges values must be positive")

    if not (values[0] < values[1] < values[2] < values[3] < values[4]):
        raise ValueError("--time-ranges must be strictly increasing")

    return values


def add_timeline_recency_classes(html_content, ranges):
    """
    Add recency tags to <li> entries containing <em>YYYYMMDD.HHMM:</em> tags.
    Keeps original item order and text unchanged.
    """
    li_block_pattern = re.compile(r'<li>(.*?)</li>', re.DOTALL)
    time_tag_pattern = re.compile(r'<em>(\d{8}\.\d{4}:)</em>')

    matches = list(li_block_pattern.finditer(html_content))
    if not matches:
        return html_content

    parsed_timestamps = []
    for match in matches:
        li_content = match.group(1)
        tag_match = time_tag_pattern.search(li_content)
        if tag_match:
            parsed = parse_time_tag(tag_match.group(1))
            if parsed is not None:
                parsed_timestamps.append(parsed)

    if not parsed_timestamps:
        return html_content

    newest_timestamp = max(parsed_timestamps)
    oldest_timestamp = min(parsed_timestamps)
    total_span_seconds = max(1.0, (newest_timestamp - oldest_timestamp).total_seconds())
    reference_time = datetime.now()

    def replacer(match):
        li_content = match.group(1)
        tag_match = time_tag_pattern.search(li_content)
        if not tag_match:
            return match.group(0)

        time_tag = tag_match.group(1)
        parsed = parse_time_tag(time_tag)
        period_text = 'MONTHX'
        if parsed is not None:
            period_text = period_label(parsed, reference_time)

        if parsed is None:
            tag_color = '#64748b'
        else:
            age_seconds = (newest_timestamp - parsed).total_seconds()
            normalized_age = age_seconds / total_span_seconds
            tag_color = jet_color_hex(normalized_age)

        tag_html = (
            f'<span class="recency-tag" data-time-tag="{time_tag}" '
            f'style="color:{tag_color}; border-color:{tag_color};">{period_text}</span> '
        )
        if li_content.lstrip().startswith('<p>'):
            tagged_content = re.sub(r'^(\s*<p>)', rf'\1{tag_html}', li_content, count=1)
        else:
            tagged_content = tag_html + li_content

        return f'<li>{tagged_content}</li>'

    return li_block_pattern.sub(replacer, html_content)


def load_css(css_file=None):
    """Load shared CSS used by both HTML and PDF templates."""
    css_path = css_file or DEFAULT_CSS_FILE
    try:
        with open(css_path, 'r', encoding='utf-8') as css_handle:
            return css_handle.read()
    except FileNotFoundError:
        print(f"Error: CSS file '{css_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSS file '{css_path}': {e}", file=sys.stderr)
        sys.exit(1)


def preserve_heading_underscores(markdown_content):
    """Escape underscores in heading text so markdown doesn't treat them as emphasis."""
    heading_pattern = re.compile(r'^(\s*#{1,6}\s+)(.*)$', re.MULTILINE)

    def replacer(match):
        prefix = match.group(1)
        heading_text = match.group(2)
        return prefix + heading_text.replace('_', r'\_')

    return heading_pattern.sub(replacer, markdown_content)


def add_heading_numbers(html_content):
    """Prefix heading tags (h1-h6) with hierarchical numbering."""
    heading_pattern = re.compile(r'<h([1-6])>(.*?)</h\1>', re.DOTALL)
    counters = [0] * 6

    def replacer(match):
        level = int(match.group(1))
        content = match.group(2)

        counters[level - 1] += 1
        for idx in range(level, 6):
            counters[idx] = 0

        number = '.'.join(str(counters[idx]) for idx in range(level) if counters[idx] > 0)
        return f'<h{level}><span class="heading-number">{number} </span>{content}</h{level}>'

    return heading_pattern.sub(replacer, html_content)


def pdf_compact_overrides():
    """Return compact CSS overrides for PDF engines (wkhtmltopdf/xhtml2pdf)."""
    return """
body { line-height: 0.9 !important; }
p { margin: 0 0 2pt 0 !important; }
h1, h2, h3, h4, h5, h6 {
    margin-top: 1pt !important;
    margin-bottom: 1pt !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin-left: 0 !important;
    padding-left: 0 !important;
    text-indent: 0 !important;
    border: none !important;
    line-height: 1.0 !important;
}
h1 { font-size: 19pt !important; }
h2 { font-size: 17pt !important; }
h3 { font-size: 15pt !important; }
h4 { font-size: 13pt !important; }
h5 { font-size: 11pt !important; }
h6 { font-size: 9pt !important; }
ul, ol {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 1.2em !important;
}
p + ul, p + ol, ul + p, ol + p {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
li {
    margin: 0 !important;
    padding: 0 !important;
    line-height: 0.95 !important;
}
li > p {
    margin: 0 !important;
    padding: 0 !important;
    display: inline !important;
    line-height: 0.95 !important;
}
li p + p { display: inline !important; }
blockquote {
    margin: 0.5pt 0 !important;
    padding: 0 0 0 6pt !important;
    border-left-width: 2px !important;
    line-height: 0.95 !important;
}
blockquote p { margin: 0 !important; line-height: 0.95 !important; }
blockquote * { margin-top: 0 !important; margin-bottom: 0 !important; }
.recency-tag { line-height: 1 !important; }
.heading-number { font-weight: 700 !important; }
"""

def hrlogin2md(input_file, output_file=None, output_format='md', recency_ranges=DEFAULT_RECENCY_RANGES, css_file=None):
    """
    Convert text file to clean markdown by:
    - Removing separator lines (---)
    - Adding blank lines after each line
    - Converting dates in format YYYYMMDD.HHMM to italic
    - Wrapping Windows-style paths in backticks
    - Optionally converting to HTML or PDF
    """
    # If no output file specified, use input filename with appropriate extension
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.{output_format}"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        processed_lines = []
        
        # Regex pattern to match date format: YYYYMMDD.HHMM:
        date_pattern = re.compile(r'^(\s*-\s+)(\d{8}\.\d{4}:)')
        
        for line in lines:
            # Strip whitespace for checking
            stripped_line = line.strip()
            
            # Skip separator lines (lines with only dashes)
            if stripped_line and all(c == '-' for c in stripped_line):
                continue
            
            # Skip empty lines (we'll add them back strategically)
            if not stripped_line:
                continue
            
            # Check if line has a date in bullet point
            match = date_pattern.match(line)
            if match:
                # Extract parts: bullet point and date
                bullet_part = match.group(1)  # "- " or "-  "
                date_part = match.group(2)    # "20260218.0131:"
                rest_of_line = wrap_windows_paths(line[match.end():].rstrip())
                
                # Format with italic date
                processed_line = f"{bullet_part}*{date_part}*{rest_of_line}\n"
                processed_lines.append(processed_line)
            else:
                # Add the line as-is
                processed_lines.append(wrap_windows_paths(line.rstrip()) + '\n')
            
            # Add blank line after each line
            processed_lines.append('\n')
        
        markdown_content = ''.join(processed_lines)
        
        # Handle different output formats
        if output_format == 'md':
            # Write markdown file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✓ Markdown conversion complete!")
            print(f"  Input:  {input_file}")
            print(f"  Output: {output_file}")
            
        elif output_format == 'html':
            # Convert to HTML
            try:
                import markdown2
            except ImportError:
                print("Error: markdown2 not installed. Run: pip install markdown2")
                sys.exit(1)
            
            css_content = load_css(css_file)
            render_markdown = preserve_heading_underscores(markdown_content)
            html_content = markdown2.markdown(render_markdown, extras=['fenced-code-blocks', 'tables'])
            html_content = add_timeline_recency_classes(html_content, recency_ranges)
            
            # Wrap in basic HTML template
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{os.path.basename(input_file)}</title>
    <style>
{css_content}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            print(f"✓ HTML conversion complete!")
            print(f"  Input:  {input_file}")
            print(f"  Output: {output_file}")
            
        elif output_format == 'pdf':
            # Convert to PDF via HTML
            try:
                import markdown2
                import pdfkit
            except ImportError:
                print(f"Error: Required package not installed.")
                print("Run: pip install markdown2 pdfkit xhtml2pdf")
                print("Optional for better rendering: install wkhtmltopdf binary")
                sys.exit(1)
            
            css_content = load_css(css_file)
            compact_pdf_css = pdf_compact_overrides()
            render_markdown = preserve_heading_underscores(markdown_content)
            html_content = markdown2.markdown(render_markdown, extras=['fenced-code-blocks', 'tables'])
            html_content = add_heading_numbers(html_content)
            html_content = add_timeline_recency_classes(html_content, recency_ranges)
            
            # HTML template for PDF
            pdf_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(input_file)}</title>
    <style>
{css_content}
{compact_pdf_css}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            wkhtmltopdf_path = shutil.which('wkhtmltopdf')

            if wkhtmltopdf_path:
                options = {
                    'page-size': 'A4',
                    'margin-top': '20mm',
                    'margin-right': '20mm',
                    'margin-bottom': '20mm',
                    'margin-left': '20mm',
                    'encoding': 'UTF-8',
                    'enable-local-file-access': None
                }
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                pdfkit.from_string(pdf_html, output_file, options=options, configuration=config)
            else:
                try:
                    from xhtml2pdf import pisa
                except ImportError:
                    print("Error: wkhtmltopdf not found and xhtml2pdf is not installed.")
                    print("Install either wkhtmltopdf binary or run: pip install xhtml2pdf")
                    sys.exit(1)

                with open(output_file, 'wb') as out_pdf:
                    result = pisa.CreatePDF(pdf_html, dest=out_pdf)
                if result.err:
                    print("Error: xhtml2pdf conversion failed.")
                    sys.exit(1)

            print(f"✓ PDF conversion complete!")
            print(f"  Input:  {input_file}")
            print(f"  Output: {output_file}")
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python hrlogin2md.py input_file [output_file] [--format md|html|pdf]")
        print("       python hrlogin2md.py input_file [output_file] [--format md|html|pdf] [--time-ranges m1,m2,m3,m4,m5] [--css path/to/style.css]")
        print("\nExamples:")
        print("  python hrlogin2md.py notes.txt")
        print("  python hrlogin2md.py notes.txt output.md")
        print("  python hrlogin2md.py notes.txt output.html --format html")
        print("  python hrlogin2md.py notes.txt output.pdf --format pdf")
        print("  python hrlogin2md.py notes.txt output.html --format html --time-ranges 1440,2880,10080,20160,30240")
        print("  python hrlogin2md.py notes.txt output.pdf --format pdf --time-ranges 1440,2880,10080,20160,30240")
        print("  python hrlogin2md.py notes.md output.html --format html") # auto-using default time ranges
        print("  python hrlogin2md.py notes.md output.pdf --format pdf") # auto-using default time ranges
        print("  python hrlogin2md.py notes.md output.html --format html --css hrlogin_style.css") # auto-using default time ranges
        print("  python hrlogin2md.py notes.md output.pdf --format pdf --css hrlogin_style.css") # auto-using default time ranges
        print("  python hrlogin2md.py notes.md --format pdf  # auto-names output") # auto-using default time ranges
        print("  ---------------------------------------------------")
        # or using markdown-pdf input.md
        print("  markdown-pdf input.md")
        print("  pandoc input.md -o output.html --standalone")
        print("  pandoc input.md -o output.pdf") # Using pandoc with LaTeX
        print("  pandoc input.md -o output.pdf --pdf-engine=wkhtmltopdf")
        # pandoc hrlogin_data.md -o out.pdf --pdf-engine=xelatex -H header.tex
        print("  pandoc input.md -o output.pdf --pdf-engine=xelatex -H header.tex")
        # pandoc hrlogin_data.md -o out.pdf --pdf-engine=lualatex -H header.tex
        print("  pandoc input.md -o output.pdf --pdf-engine=lualatex -H header.tex")
        # pandoc hrlogin_data.md -o out.pdf --pdf-engine=xelatex -H header.tex --toc --toc-depth=3 --number-sections
        print("  pandoc hrlogin_data.md -o output.pdf --pdf-engine=xelatex -H header.tex --toc --toc-depth=3 --number-sections")
        print("  pandoc hrloginfo.md -o hrloginfo.pdf --pdf-engine=xelatex -H ~/.local/bin/header.tex --toc --toc-depth=3 --number-sections")

        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = None
    output_format = 'md'
    recency_ranges = DEFAULT_RECENCY_RANGES
    css_file = None
    
    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--format':
            if i + 1 < len(sys.argv):
                output_format = sys.argv[i + 1].lower()
                if output_format not in ['md', 'html', 'pdf']:
                    print(f"Error: Invalid format '{output_format}'. Use: md, html, or pdf")
                    sys.exit(1)
                i += 2
            else:
                print("Error: --format requires an argument (md, html, or pdf)")
                sys.exit(1)
        elif sys.argv[i] == '--time-ranges':
            if i + 1 < len(sys.argv):
                try:
                    recency_ranges = parse_time_ranges(sys.argv[i + 1])
                except ValueError as e:
                    print(f"Error: {e}")
                    print("Example: --time-ranges 1440,2880,10080,20160,30240")
                    sys.exit(1)
                i += 2
            else:
                print("Error: --time-ranges requires an argument like 1440,2880,10080,20160,30240")
                sys.exit(1)
        elif sys.argv[i] == '--css':
            if i + 1 < len(sys.argv):
                css_file = sys.argv[i + 1]
                i += 2
            else:
                print("Error: --css requires a file path argument")
                sys.exit(1)
        else:
            output_file = sys.argv[i]
            i += 1
    
    hrlogin2md(input_file, output_file, output_format, recency_ranges, css_file)

if __name__ == "__main__":
    main()
