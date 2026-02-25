#!/usr/bin/env python3
"""
Bulk update script to add minimal mode support to all remaining HTML files
Run this from the root of your old-world-builder repository
"""

import os
import glob

MINIMAL_MODE_CODE = """    <style>
      /* Minimal mode styling - matches tow.whfb.app minimal header */
      body.minimal-mode .minimal-source {
        font-size: 14px;
        margin: 10px 0;
        padding: 0;
      }
      
      body.minimal-mode .minimal-source span {
        display: none;
      }
      
      body.minimal-mode .minimal-source::before {
        content: 'Back';
        color: #0066cc;
        text-decoration: none;
        margin-right: 20px;
        cursor: pointer;
      }
      
      body.minimal-mode .minimal-source::after {
        content: 'Source: ';
        margin-left: 0;
      }
      
      body.minimal-mode .minimal-source a {
        color: #0066cc;
        text-decoration: none;
        font-weight: normal;
      }
      
      body.minimal-mode .minimal-source a:hover {
        text-decoration: underline;
      }
      
      /* Hide the full header elements in minimal mode */
      body.minimal-mode .css-1kvywv3 {
        padding: 10px;
      }
    </style>
    <script>
      // Check for minimal=true parameter and apply minimal mode
      (function() {
        const urlParams = new URLSearchParams(window.location.search);
        const isMinimal = urlParams.get('minimal') === 'true';
        
        if (isMinimal) {
          document.body.classList.add('minimal-mode');
          
          // Add back button functionality
          const minimalSource = document.querySelector('.minimal-source');
          if (minimalSource) {
            minimalSource.style.cursor = 'pointer';
            minimalSource.addEventListener('click', function(e) {
              if (e.target === this || e.offsetX < 60) {
                window.history.back();
              }
            });
          }
          
          // Add minimal=true to all tow.whfb.app links for consistent navigation
          document.querySelectorAll('a[href^="https://tow.whfb.app"]').forEach(function(link) {
            const href = link.getAttribute('href');
            
            // Skip if already has minimal parameter
            if (href.includes('minimal=')) return;
            
            // Skip asset files (images, icons, css, etc)
            const skipExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js', '.woff', '.woff2', '.ttf', '.webmanifest', '.json'];
            if (skipExtensions.some(ext => href.toLowerCase().endsWith(ext))) return;
            if (href.includes('/icons/') || href.includes('/static/') || href.includes('/_next/')) return;
            
            // Add minimal=true parameter
            const separator = href.includes('?') ? '&' : '?';
            link.setAttribute('href', href + separator + 'minimal=true');
          });
        }
      })();
    </script>
"""

def update_html_file(filepath):
    """Update a single HTML file with minimal mode support"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has minimal mode code
        if 'body.minimal-mode' in content:
            return 'skipped'
        
        # Add the code before </body>
        if '</body>' in content:
            updated_content = content.replace('  </body>\n</html>', MINIMAL_MODE_CODE + '  </body>\n</html>')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return 'updated'
        else:
            return 'error'
    except Exception as e:
        return f'error: {str(e)}'

def main():
    # Find all HTML files in rules directory
    html_files = []
    html_files.extend(glob.glob('rules/unit/*.html'))
    html_files.extend(glob.glob('rules/weapons-of-war/*.html'))
    html_files.extend(glob.glob('rules/magic-items/*.html'))
    
    print(f"Found {len(html_files)} HTML files to process\n")
    
    updated = 0
    skipped = 0
    errors = 0
    
    for filepath in sorted(html_files):
        result = update_html_file(filepath)
        
        if result == 'updated':
            print(f"✓ Updated: {filepath}")
            updated += 1
        elif result == 'skipped':
            print(f"- Skipped (already updated): {filepath}")
            skipped += 1
        else:
            print(f"✗ Error: {filepath} - {result}")
            errors += 1
    
    print()
    print("=" * 60)
    print(f"Summary:")
    print(f"  ✓ Updated: {updated} files")
    print(f"  - Skipped: {skipped} files")
    print(f"  ✗ Errors: {errors} files")
    print(f"  Total: {len(html_files)} files")
    print("=" * 60)
    
    if updated > 0:
        print()
        print("✓ Update complete! You can now commit and push your changes:")
        print("  git add rules/")
        print("  git commit -m 'Add minimal mode support to all HTML rule files'")
        print("  git push origin main")

if __name__ == '__main__':
    main()
