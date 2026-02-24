#!/usr/bin/env python3
"""
format_html_files.py -- Format existing HTML files to be human-readable

Usage:
  python3 format_html_files.py [path/to/html/files]
  
If no path is provided, defaults to ../rules/unit/

This script will:
1. Format HTML with proper indentation
2. Add helpful HTML comments labeling each stat (M, WS, BS, S, T, W, I, A, Ld)
3. Make files easier to manually edit
"""

import sys
import os
import re
from pathlib import Path
from html.parser import HTMLParser


# Stat keys and their full names
STAT_KEYS = ["Name", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld"]
STAT_NAMES = {
    "Name": "Unit Name",
    "M": "Movement",
    "WS": "Weapon Skill",
    "BS": "Ballistic Skill",
    "S": "Strength",
    "T": "Toughness",
    "W": "Wounds",
    "I": "Initiative",
    "A": "Attacks",
    "Ld": "Leadership"
}


def add_stat_comments_to_table(html_content):
    """
    Add HTML comments to label each stat in the unit profile table.
    This makes it much easier to find and edit specific stats manually.
    """
    # Find the tbody section with unit stats
    tbody_pattern = r'(<tbody[^>]*data-test-id="cf-ui-table-body"[^>]*>)(.*?)(</tbody>)'
    tbody_match = re.search(tbody_pattern, html_content, re.DOTALL)
    
    if not tbody_match:
        return html_content
    
    tbody_start = tbody_match.group(1)
    tbody_content = tbody_match.group(2)
    tbody_end = tbody_match.group(3)
    
    # Find all table rows
    row_pattern = r'<tr[^>]*data-test-id="cf-ui-table-row"[^>]*>(.*?)</tr>'
    rows = re.finditer(row_pattern, tbody_content, re.DOTALL)
    
    new_rows = []
    for row_match in rows:
        row_content = row_match.group(1)
        
        # Extract all cells from this row
        cell_pattern = r'<td[^>]*data-test-id="cf-ui-table-cell"[^>]*>(.*?)</td>'
        cells = re.findall(cell_pattern, row_content, re.DOTALL)
        
        if len(cells) != len(STAT_KEYS):
            # Not a standard stat row, keep as is
            new_rows.append(row_match.group(0))
            continue
        
        # Get unit name (first cell)
        unit_name = re.sub(r'<[^>]+>', '', cells[0]).strip()
        
        # Build new row with comments
        new_row = f'\n            <!-- Stats for: {unit_name} -->'
        new_row += '\n            <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        
        for i, (key, cell_value) in enumerate(zip(STAT_KEYS, cells)):
            stat_name = STAT_NAMES.get(key, key)
            clean_value = re.sub(r'<[^>]+>', '', cell_value).strip()
            
            new_row += f'\n              <!-- {stat_name}: {clean_value} -->'
            new_row += f'\n              <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{cell_value}</td>'
        
        new_row += '\n            </tr>'
        new_rows.append(new_row)
    
    # Reconstruct tbody
    new_tbody = tbody_start + ''.join(new_rows) + '\n            ' + tbody_end
    
    # Replace in original HTML
    result = html_content[:tbody_match.start()] + new_tbody + html_content[tbody_match.end():]
    return result


def format_html_with_stats(html_content):
    """
    Format HTML content to match the clean_unit_html.py output style.
    Adds proper indentation and stat comments.
    """
    # First, add stat comments to the table
    html = add_stat_comments_to_table(html_content)
    
    # Define block-level tags that should be on their own line
    block_tags = {
        'html', 'head', 'body', 'div', 'main', 'header', 'footer', 'section', 'article',
        'nav', 'aside', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'form', 'fieldset', 'title'
    }
    
    result = []
    indent = 0
    indent_str = '  '
    
    # Add line breaks around block-level tags
    html = html.strip()
    
    # Insert newlines before opening block tags and after closing tags
    for tag in block_tags:
        html = re.sub(rf'<{tag}([\s>])', rf'\n<{tag}\1', html, flags=re.IGNORECASE)
        html = re.sub(rf'</{tag}>', rf'\n</{tag}>\n', html, flags=re.IGNORECASE)
    
    # Clean up multiple newlines
    html = re.sub(r'\n\s*\n+', '\n', html)
    
    lines = html.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Handle HTML comments - keep them at current indent
        if line.startswith('<!--'):
            result.append(indent_str * indent + line)
            continue
        
        # Count closing tags to adjust indent
        closing_tags = len(re.findall(r'</(\w+)>', line))
        opening_tags = len(re.findall(r'<(\w+)(?:\s|>)', line))
        self_closing_count = len(re.findall(r'<(\w+)[^>]*/>', line))
        
        # Check if line starts with closing tag
        if line.startswith('</'):
            indent = max(0, indent - 1)
        
        # Add the line with current indentation
        result.append(indent_str * indent + line)
        
        # Adjust indent for next line
        net_tags = opening_tags - closing_tags - self_closing_count
        indent = max(0, indent + net_tags)
    
    return '\n'.join(result) + '\n'


def format_html_file(filepath):
    """
    Read an HTML file, format it with stat comments, and write it back.
    """
    print(f"Formatting: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Check if this file already has stat comments
        has_comments = '<!-- Movement:' in content or '<!-- Toughness:' in content
        
        # Format the HTML with stat comments
        formatted = format_html_with_stats(content)
        
        formatted_size = len(formatted)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)
        
        comment_status = "(updated comments)" if has_comments else "(added comments)"
        print(f"  ✓ Formatted {comment_status}: {original_size:,} → {formatted_size:,} bytes")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    # Determine directory
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # Default to ../rules/unit/ relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        target_dir = os.path.join(script_dir, '..', 'rules', 'unit')
    
    target_path = Path(target_dir)
    
    if not target_path.exists():
        print(f"Error: Directory not found: {target_dir}")
        sys.exit(1)
    
    if not target_path.is_dir():
        print(f"Error: Not a directory: {target_dir}")
        sys.exit(1)
    
    # Find all HTML files
    html_files = list(target_path.glob('*.html'))
    
    if not html_files:
        print(f"No HTML files found in: {target_dir}")
        sys.exit(0)
    
    print(f"Found {len(html_files)} HTML file(s) in: {target_dir}\n")
    print("This will add helpful HTML comments to label each stat (M, WS, BS, S, T, W, I, A, Ld)")
    print("making them easier to find and edit manually.\n")
    
    success_count = 0
    for html_file in sorted(html_files):
        if format_html_file(html_file):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Completed: {success_count}/{len(html_files)} files formatted successfully")
    print(f"{'='*60}")
    print("\nYou can now easily search for stats using:")
    print("  - '<!-- Toughness:' to find all T values")
    print("  - '<!-- Movement:' to find all M values")
    print("  - '<!-- Stats for:' to find specific units")


if __name__ == '__main__':
    main()
