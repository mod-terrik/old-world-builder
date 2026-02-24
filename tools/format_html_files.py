#!/usr/bin/env python3
"""
format_html_files.py -- Format existing HTML files to be human-readable

Usage:
  python3 format_html_files.py [path/to/html/files]
  
If no path is provided, defaults to ../rules/unit/
"""

import sys
import os
import re
from pathlib import Path


def format_html(html_content):
    """
    Format a minified HTML string to be human-readable with proper indentation.
    """
    # Remove all existing whitespace between tags
    html = re.sub(r'>\s+<', '><', html_content.strip())
    
    result = []
    indent = 0
    indent_str = '  '  # 2 spaces per indent level
    
    # Split by tags
    parts = re.split(r'(<[^>]+>)', html)
    
    for part in parts:
        if not part:
            continue
            
        # Check if this is a tag
        if part.startswith('<'):
            # Closing tag - decrease indent before adding
            if part.startswith('</'):
                indent = max(0, indent - 1)
                result.append(indent_str * indent + part)
            # Self-closing tag or single-line tag
            elif part.endswith('/>') or part.startswith('<!DOCTYPE') or part.startswith('<?'):
                result.append(indent_str * indent + part)
            # Opening tag
            else:
                # Get tag name
                tag_match = re.match(r'<(\w+)', part)
                if tag_match:
                    tag_name = tag_match.group(1)
                    
                    result.append(indent_str * indent + part)
                    
                    # Increase indent for these tags
                    if tag_name not in ['br', 'hr', 'img', 'input', 'meta', 'link']:
                        indent += 1
        else:
            # Text content - only add if not empty
            text = part.strip()
            if text:
                result.append(indent_str * indent + text)
    
    return '\n'.join(result) + '\n'


def format_html_advanced(html_content):
    """
    More sophisticated HTML formatting that handles inline elements better.
    """
    # Tags that should typically be on their own line
    block_tags = {
        'html', 'head', 'body', 'div', 'main', 'header', 'footer', 'section', 'article',
        'nav', 'aside', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'form', 'fieldset', 'title'
    }
    
    # Self-closing tags
    self_closing = {'meta', 'link', 'br', 'hr', 'img', 'input'}
    
    result = []
    indent = 0
    indent_str = '  '
    
    # Add line breaks around block-level tags
    html = html_content.strip()
    
    # Insert newlines before opening block tags
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
    Read an HTML file, format it, and write it back.
    """
    print(f"Formatting: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        
        # Format the HTML
        formatted = format_html_advanced(content)
        
        formatted_size = len(formatted)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted)
        
        print(f"  ✓ Formatted: {original_size:,} → {formatted_size:,} bytes")
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
    
    success_count = 0
    for html_file in sorted(html_files):
        if format_html_file(html_file):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Completed: {success_count}/{len(html_files)} files formatted successfully")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
