#!/usr/bin/env python3
"""
hrlogin - Hierarchical directory logging tool
Logs work notes organized by directory hierarchy
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import time


def get_output_file():
    """Get output file path from environment or use default"""
    return os.environ.get('HRLOG_FILE', os.path.expanduser('~/.hrloginfo'))


def acquire_lock(lockfile, timeout=5):
    """Acquire file lock with timeout"""
    try:
        import portalocker
    except ImportError as exc:
        raise RuntimeError("Missing dependency: portalocker. Install with `pip install portalocker`.") from exc

    lock_fd = open(lockfile, 'a+', encoding='utf-8')
    try:
        try:
            portalocker.lock(lock_fd, portalocker.LOCK_EX, timeout=timeout)
            return lock_fd
        except TypeError:
            lock_nb = getattr(portalocker, 'LOCK_NB', 0)
            start_time = time.time()
            while True:
                try:
                    portalocker.lock(lock_fd, portalocker.LOCK_EX | lock_nb)
                    return lock_fd
                except portalocker.exceptions.LockException:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Could not acquire lock")
                    time.sleep(0.1)
    except portalocker.exceptions.LockException as exc:
        lock_fd.close()
        raise TimeoutError("Could not acquire lock") from exc
    except TimeoutError:
        lock_fd.close()
        raise


def release_lock(lock_fd):
    """Release file lock"""
    if lock_fd:
        import portalocker
        portalocker.unlock(lock_fd)
        lock_fd.close()


def get_relative_path(current_path, home):
    """Get path relative to HOME, or from root if outside HOME"""
    current = Path(current_path).resolve()
    home_path = Path(home).resolve()
    
    if current == home_path:
        return None, None  # Cannot log at HOME
    
    try:
        # Try to get path relative to HOME
        rel = current.relative_to(home_path)
        return rel, True  # Inside HOME
    except ValueError:
        # Outside HOME - keep absolute path (cross-platform)
        return current, False


def build_section_hierarchy(rel_path, home, inside_home):
    """Build list of section headers and paths from path components"""
    sections = []

    if inside_home:
        parts = rel_path.parts
    else:
        abs_path = str(rel_path)
        drive, tail = os.path.splitdrive(abs_path)
        normalized_tail = tail.replace('\\', '/')
        tail_parts = [p for p in normalized_tail.split('/') if p]
        if drive:
            parts = (f"{drive.rstrip(':')}:", *tail_parts)
        else:
            parts = tuple(tail_parts)

    for depth, part in enumerate(parts, start=1):
        hashes = '#' * depth

        # Build full path for this section
        partial_path = Path(*parts[:depth])
        if inside_home:
            display_path = f"~/{partial_path}"
        else:
            first_part = parts[0]
            if first_part.endswith(':'):
                if depth == 1:
                    display_path = first_part + '\\'
                else:
                    display_path = first_part + '\\' + '\\'.join(parts[1:depth])
            else:
                display_path = '/' + '/'.join(parts[:depth])

        sections.append({
            'header': f"{hashes} {part}",
            'path_line': f"> {display_path}",
            'depth': depth
        })
    
    return sections


def parse_existing_file(filepath):
    """Parse existing file into structured data"""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    return [line.rstrip('\n') for line in lines]


def find_section_line(lines, section_header):
    """Find line number where section header exists"""
    for i, line in enumerate(lines):
        if line == section_header:
            return i
    return None


def find_last_existing_section(lines, sections):
    """Find the last section in hierarchy that exists in file"""
    last_idx = -1
    last_line = -1
    
    for idx, section in enumerate(sections):
        line_num = find_section_line(lines, section['header'])
        if line_num is not None:
            last_idx = idx
            last_line = line_num
        else:
            break
    
    return last_idx, last_line


def insert_bullet_in_section(lines, section_line, bullet):
    """Insert bullet right after section header and path line"""
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        # Insert after path line (which is right after header)
        if i == section_line + 1:
            new_lines.append(bullet)
    return new_lines


def find_next_separator_after(lines, start_line):
    """Find next separator line after given line"""
    for i in range(start_line + 1, len(lines)):
        if lines[i] == '------------------------':
            return i
    return None


def insert_sections_after_parent(lines, parent_line, new_sections, bullet, target_header):
    """Insert new sections after parent section"""
    # Find where to insert (before next separator or at end)
    next_sep = find_next_separator_after(lines, parent_line)
    
    if next_sep is None:
        # Parent is last section - append at end
        insert_at = len(lines)
    else:
        # Insert before next separator (skip back over blank line if present)
        insert_at = next_sep
        # Check if there's a blank line before separator
        if insert_at > 0 and lines[insert_at - 1] == '':
            insert_at = insert_at - 1
    
    # Build insertion content
    insertion = []
    for section in new_sections:
        insertion.append('')  # Blank line before separator
        insertion.append('------------------------')
        insertion.append(section['header'])
        insertion.append(section['path_line'])
        if section['header'] == target_header:
            insertion.append(bullet)
    
    # Reconstruct lines
    new_lines = lines[:insert_at] + insertion + lines[insert_at:]
    return new_lines


def append_new_hierarchy(lines, sections, bullet, target_header):
    """Append completely new hierarchy at end of file"""
    new_lines = lines.copy()
    
    # Remove trailing blank lines from existing content
    while new_lines and new_lines[-1] == '':
        new_lines.pop()
    
    for section in sections:
        new_lines.append('')  # Blank line before separator
        new_lines.append('------------------------')
        new_lines.append(section['header'])
        new_lines.append(section['path_line'])
        if section['header'] == target_header:
            new_lines.append(bullet)
    
    return new_lines


def normalize_blank_lines(lines):
    """Remove consecutive blank lines and trailing blanks"""
    normalized = []
    prev_blank = False
    
    for line in lines:
        is_blank = line == ''
        
        # Skip if this is a blank and previous was also blank
        if is_blank and prev_blank:
            continue
        
        normalized.append(line)
        prev_blank = is_blank
    
    # Remove trailing blank lines
    while normalized and normalized[-1] == '':
        normalized.pop()
    
    return normalized


def hrlogin_main(description):
    """Main logic for hrlogin"""
    if not description:
        print("[hrlogin] No description provided - skipping")
        return 0
    
    # Get paths
    outfile = get_output_file()
    lockfile = outfile + '.lock'
    current_dir = os.getcwd()
    home = os.path.expanduser('~')
    
    # Get relative path
    try:
        rel_path, inside_home = get_relative_path(current_dir, home)
    except Exception as e:
        print(f"[hrlogin] Error getting relative path: {e}")
        return 1
    
    if rel_path is None:
        print("[hrlogin] Cannot log at HOME or root directory")
        return 1
    
    # Build section hierarchy with paths
    sections = build_section_hierarchy(rel_path, home, inside_home)
    if not sections:
        print("[hrlogin] Invalid path")
        return 1
    
    target_section = sections[-1]['header']
    # Changed from YYYYMMDD to YYYYMMDD.HHMM
    date_stamp = datetime.now().strftime('%Y%m%d.%H%M')
    bullet = f"- {date_stamp}: {description}"
    
    # Acquire lock
    lock_fd = None
    try:
        lock_fd = acquire_lock(lockfile)
        
        # Parse existing file
        lines = parse_existing_file(outfile)
        
        # Check if target section exists
        target_line = find_section_line(lines, target_section)
        
        if target_line is not None:
            # Target exists - just insert bullet
            new_lines = insert_bullet_in_section(lines, target_line, bullet)
        else:
            # Need to create sections
            section_headers = [s['header'] for s in sections]
            last_existing_idx, last_existing_line = find_last_existing_section(lines, sections)
            
            if last_existing_idx == -1:
                # No parents exist - append all at end
                new_lines = append_new_hierarchy(lines, sections, bullet, target_section)
            else:
                # Insert missing sections after last existing parent
                new_sections = sections[last_existing_idx + 1:]
                new_lines = insert_sections_after_parent(
                    lines, last_existing_line, new_sections, bullet, target_section
                )
        
        # Normalize blank lines (remove consecutive blanks and trailing)
        new_lines = normalize_blank_lines(new_lines)
        
        # Write back to file
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
            # Add final newline
            f.write('\n')
        
        # Success message
        path_display = sections[-1]['path_line'][2:]
        print(f"[hrlogin] ✓ Logged: {path_display}")
        
        return 0
        
    except Exception as e:
        print(f"[hrlogin] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if lock_fd:
            release_lock(lock_fd)
        # Clean up lock file
        try:
            if os.path.exists(lockfile):
                os.remove(lockfile)
        except:
            pass


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("[hrlogin] Usage: hrlogin 'description'")
        return 0
    
    description = ' '.join(sys.argv[1:])
    return hrlogin_main(description)


if __name__ == '__main__':
    sys.exit(main())
