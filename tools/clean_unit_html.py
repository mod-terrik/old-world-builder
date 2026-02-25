#!/usr/bin/env python3
"""
clean_unit_html.py -- Generate static HTML pages mirroring tow.whfb.app

Usage:
  python3 clean_unit_html.py --fetch <slug> [--type unit|weapons-of-war|magic-item|special-rule] [--out <dir>]

  --type   defaults to 'unit' for backward compatibility.
           Use 'magic-item' (singular) to match the live site URL.
  --out    defaults to ../rules/<type>/ relative to this script.
  --build  optional: override the Next.js BUILD_ID (auto-detected when omitted).
  --debug  dump all raw field keys and types from the JSON response, then exit.
           Use this to diagnose missing content.

Examples:
  python3 clean_unit_html.py --fetch halberd --type weapons-of-war
  python3 clean_unit_html.py --fetch the-fellblade --type magic-item
  python3 clean_unit_html.py --fetch the-fellblade --type magic-item --debug
  python3 clean_unit_html.py --fetch fly --type special-rule
  python3 clean_unit_html.py --fetch grave-guard
"""

import sys, os, re, json, urllib.request

BASE_URL = "https://tow.whfb.app"
CSS_BASE = "/owb/rules"

# Maps the --type flag value to the exact Next.js page-route segment
# used in /_next/data/<BUILD_ID>/<FETCH_ROUTE>/<slug>.json
# These MUST match the live site's URL paths exactly.
FETCH_ROUTES = {
    "unit":           "unit",
    "weapons-of-war": "weapons-of-war",
    "magic-item":     "magic-item",    # singular -- matches tow.whfb.app/magic-item/<slug>
    "special-rule":   "special-rules",  # fetch route uses plural
}

# Default local output dirs relative to this script
DEFAULT_OUT_DIRS = {
    "unit":           "../rules/unit",
    "weapons-of-war": "../rules/weapons-of-war",
    "magic-item":     "../rules/magic-items",   # stored locally under magic-items (plural)
    "magic-items":    "../rules/magic-items",
    "special-rule":   "../rules/special-rules",
}

# rules-map fullUrl subdirectory names (what the hosted app expects)
RULES_MAP_SUBDIRS = {
    "unit":           "unit",
    "weapons-of-war": "weapons-of-war",
    "magic-item":     "magic-items",
    "magic-items":    "magic-items",
    "special-rule":   "special-rules",
}

# Base URL for rules-map fullUrl entries
OWB_RULES_BASE = "https://owapps.grra.me/owb/rules"

# Path to rules-map.js, relative to this script's location
RULES_MAP_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "src", "components", "rules-index", "rules-map.js"
)

CONTENT_TYPE_PATHS = {
    "specialRule":  "/special-rules",
    "weaponOfWar":  "/weapons-of-war",
    "troopType":    "/troop-types-in-detail",
    "unitCategory": "/troop-types-in-detail",
    "magicItem":    "/magic-item",
    "spell":        "/spells",
}

# Known ruleType IDs from Contentful that distinguish different kinds of "rule" entries
# These are discovered by examining the JSON structure of linked entries
RULE_TYPE_IDS = {
    "1cxV0Jnvb1D701DgF8Y7Op": "/troop-types-in-detail",  # Troop Type (Infantry, Cavalry, etc.)
}

STAT_KEYS      = ["Name", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld"]
STAT_NAMES     = {
    "Name": "Unit Name",
    "M":    "Movement",
    "WS":   "Weapon Skill",
    "BS":   "Ballistic Skill",
    "S":    "Strength",
    "T":    "Toughness",
    "W":    "Wounds",
    "I":    "Initiative",
    "A":    "Attacks",
    "Ld":   "Leadership",
}
EDITABLE_STATS = ["M", "WS", "BS", "S", "T", "W", "I", "A", "Ld"]

# Weapon profile columns: (contentful_field_key, display_header)
# Header labels match the live site exactly.
WEAPON_PROFILE_FIELDS = [
    ("range",          "Range"),
    ("strength",       "Strength"),
    ("armourPiercing", "Armour Piercing"),   # full label, not "AP"
]

# Ordered candidates for the flavour / intro description text
# (shown as italic paragraph above the profile table on the live site)
DESCRIPTION_FIELD_CANDIDATES = [
    "description",
    "flavourText",
    "flavour",
    "intro",
    "summary",
]

# Ordered candidates for the rules / notes body
# (shown as bullet list below the profile table on the live site)
# For magic items, the entire body (including embedded table nodes) is in 'body'.
NOTES_FIELD_CANDIDATES = [
    "body",     # magic items store table + notes here as rich-text
    "notes",
    "rules",
    "text",
    "content",
]


def _normalise_type(content_type):
    """Normalise legacy 'magic-items' alias to canonical 'magic-item'."""
    return "magic-item" if content_type == "magic-items" else content_type


def _is_present(val):
    """Return True if val is non-None and non-empty-string."""
    if val is None:
        return False
    if isinstance(val, str) and val.strip() == "":
        return False
    return True


# -- BUILD_ID detection -------------------------------------------------------

def detect_build_id():
    """
    Fetch the tow.whfb.app home page and extract the current Next.js
    BUILD_ID from the __NEXT_DATA__ JSON block embedded in the HTML.
    """
    print("  [build] Auto-detecting BUILD_ID from tow.whfb.app ...", end=" ", flush=True)
    req = urllib.request.Request(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")
    except Exception as e:
        sys.exit(f"\n  [error] Could not fetch {BASE_URL} to detect BUILD_ID: {e}")

    # Primary: parse __NEXT_DATA__ JSON block
    m = re.search(
        r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    if m:
        try:
            build_id = json.loads(m.group(1)).get("buildId", "")
            if build_id:
                print(build_id)
                return build_id
        except (json.JSONDecodeError, AttributeError):
            pass

    # Fallback: look for /_next/data/<id>/ in any script src
    m2 = re.search(r'/_next/data/([^/"]+)/', html)
    if m2:
        build_id = m2.group(1)
        print(build_id)
        return build_id

    sys.exit(
        "\n  [error] Could not detect BUILD_ID from tow.whfb.app. "
        "Use --build <id> to supply it manually."
    )


# -- helpers ------------------------------------------------------------------

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def first_field(fields, candidates):
    """Return the value of the first non-empty candidate field, or None."""
    for key in candidates:
        val = fields.get(key)
        if _is_present(val):
            return val
    return None


def extract_embedded_weapon_profile(body_rt):
    """
    Walk the body rich-text tree looking for embedded-entry-block nodes
    with contentType 'weaponProfile'. Return the first such entry's fields
    dict, or None if not found.
    """
    if not isinstance(body_rt, dict):
        return None
    
    node_type = body_rt.get("nodeType", "")
    
    # Check if this is an embedded-entry-block with weaponProfile contentType
    if node_type == "embedded-entry-block":
        target = body_rt.get("data", {}).get("target", {})
        ct = target.get("sys", {}).get("contentType", {}).get("sys", {}).get("id", "")
        if ct == "weaponProfile":
            return target.get("fields", {})
    
    # Recursively search content array
    content = body_rt.get("content", [])
    for child in content:
        result = extract_embedded_weapon_profile(child)
        if result:
            return result
    
    return None


def entry_url(target, context="auto"):
    """
    Build a tow.whfb.app URL for a Contentful linked entry.
    
    When context is 'equipment' or 'rules', use those fixed paths.
    Otherwise, read the entry's contentType ID from target.sys.contentType.sys.id
    and map it using CONTENT_TYPE_PATHS.
    
    For contentType "rule", check the ruleType field to distinguish between:
    - Troop Types (Infantry, Cavalry, etc.) → /troop-types-in-detail/
    - Special Rules (Ward Saves, Regeneration, etc.) → /special-rules/
    - Weapons of War rules → /weapons-of-war/
    """
    if not isinstance(target, dict):
        return BASE_URL
    
    fields = target.get("fields", {})
    slug   = fields.get("slug", "")
    
    if not slug:
        return BASE_URL
    
    # Override path based on explicit context hints
    if context == "equipment":
        return f"{BASE_URL}/weapons-of-war/{slug}"
    elif context == "rules":
        return f"{BASE_URL}/special-rules/{slug}"
    
    # Read contentType from the entry's sys metadata
    ct = target.get("sys", {}).get("contentType", {}).get("sys", {}).get("id", "")
    
    # Special handling for "rule" contentType: check ruleType to determine subdirectory
    if ct == "rule":
        rule_type_list = fields.get("ruleType", [])
        if rule_type_list:
            # ruleType is a list of linked entries; grab the first ID
            rule_type_id = None
            if isinstance(rule_type_list, list) and rule_type_list:
                first_rt = rule_type_list[0]
                if isinstance(first_rt, dict):
                    rule_type_id = first_rt.get("sys", {}).get("id", "")
            
            # Check if this ruleType ID is a known Troop Type
            if rule_type_id and rule_type_id in RULE_TYPE_IDS:
                path = RULE_TYPE_IDS[rule_type_id]
                return f"{BASE_URL}{path}/{slug}"
        
        # Default for "rule" contentType without a recognized ruleType: special-rules
        return f"{BASE_URL}/special-rules/{slug}"
    
    # Use CONTENT_TYPE_PATHS for all other contentTypes
    path = CONTENT_TYPE_PATHS.get(ct, "")
    
    if not path:
        # Fallback: just use the slug directly (no subdirectory)
        return f"{BASE_URL}/{slug}"
    
    return f"{BASE_URL}{path}/{slug}"


def render_rt(node, ctx="auto"):
    """Recursively render a Contentful rich-text node to HTML (no JS)."""
    if not isinstance(node, dict):
        return esc(str(node))
    nt      = node.get("nodeType", "")
    content = node.get("content", [])
    inner   = lambda: "".join(render_rt(c, ctx) for c in content)

    if nt == "text":
        out = esc(node.get("value", ""))
        for m in node.get("marks", []):
            t = m.get("type", "")
            if   t == "bold":      out = f"<b>{out}</b>"
            elif t == "italic":    out = f"<i>{out}</i>"
            elif t == "underline": out = f"<u>{out}</u>"
            elif t == "code":      out = f"<code>{out}</code>"
        return out
    elif nt == "hyperlink":
        return f'<a href="{esc(node["data"]["uri"])}">{inner()}</a>'
    elif nt == "entry-hyperlink":
        # For entry-hyperlinks, use context="auto" to let entry_url() read the contentType + ruleType
        return f'<a href="{entry_url(node["data"]["target"], "auto")}">{inner()}</a>'
    elif nt == "paragraph":
        # Handle paragraphs with multiple text segments (for multi-line cells like Range)
        # If this is a table cell context, check for multiple text nodes
        if ctx == "table-cell":
            # Collect all text values from direct text children
            text_values = []
            for child in content:
                if isinstance(child, dict) and child.get("nodeType") == "text":
                    text_values.append(esc(child.get("value", "")))
            # If we have multiple text values, join with <br>
            if len(text_values) > 1:
                return "<br>".join(text_values)
        return f"<p>{inner()}</p>"
    elif nt == "unordered-list":
        return "<ul>" + "".join(f"<li>{render_rt(i, ctx)}</li>" for i in content) + "</ul>"
    elif nt == "ordered-list":
        return "<ol>" + "".join(f"<li>{render_rt(i, ctx)}</li>" for i in content) + "</ol>"
    elif nt == "table":
        # Contentful embedded table node (magic items store profile tables here)
        rows_html = "".join(render_rt(row, ctx) for row in content)
        return (
            f'<table class="generic-table weapon-profile-table css-1hz7skb" '
            f'data-test-id="cf-ui-table" cellpadding="0" cellspacing="0">{rows_html}</table>'
        )
    elif nt == "table-row":
        cells_html = "".join(render_rt(cell, ctx) for cell in content)
        return f'<tr class="css-1sydf7g" data-test-id="cf-ui-table-row">{cells_html}</tr>'
    elif nt == "table-header-cell":
        return f'<th class="css-9p6xbs" data-test-id="cf-ui-table-cell">{render_rt(content[0], "table-cell") if content else ""}</th>'
    elif nt == "table-cell":
        # Pass table-cell context to handle multi-line content
        cell_html = ""
        for child in content:
            if isinstance(child, dict) and child.get("nodeType") == "paragraph":
                # For paragraphs in table cells, render specially to handle multi-line
                para_content = child.get("content", [])
                text_values = []
                for text_node in para_content:
                    if isinstance(text_node, dict) and text_node.get("nodeType") == "text":
                        text_values.append(esc(text_node.get("value", "")))
                if text_values:
                    cell_html += "<br>".join(text_values)
                else:
                    cell_html += render_rt(child, "table-cell")
            else:
                cell_html += render_rt(child, "table-cell")
        return f'<td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{cell_html}</td>'
    else:
        return inner()


def rt_to_html(val):
    """Convert a rich-text value or plain string to an HTML string."""
    if not _is_present(val):
        return ""
    if isinstance(val, dict) and "content" in val:
        return render_rt(val)
    if isinstance(val, str):
        return f"<p>{esc(val)}</p>"
    return ""


def collect_links(node, ctx="auto"):
    """Walk rich-text and return list of (href, label) for every hyperlink."""
    if not isinstance(node, dict):
        return []
    nt, content = node.get("nodeType", ""), node.get("content", [])
    if nt == "entry-hyperlink":
        href  = entry_url(node["data"]["target"], ctx)
        label = "".join(render_rt(c, ctx) for c in content)
        return [(href, label)]
    if nt == "hyperlink":
        href  = esc(node["data"]["uri"])
        label = "".join(render_rt(c, ctx) for c in content)
        return [(href, label)]
    return [pair for c in content for pair in collect_links(c, ctx)]


def _scalar_or_rt(val):
    """
    Render a profile cell value: plain scalar, rich-text doc, or list of
    linked entries. Returns '-' for absent/empty values.
    Handles multi-paragraph rich-text by extracting all text nodes and joining with <br>.
    """
    if not _is_present(val):
        return "-"
    if isinstance(val, dict) and "content" in val:
        # Handle rich-text with multiple paragraphs (like Range with multiple values)
        text_values = []
        for para in val.get("content", []):
            if isinstance(para, dict) and para.get("nodeType") == "paragraph":
                for text_node in para.get("content", []):
                    if isinstance(text_node, dict) and text_node.get("nodeType") == "text":
                        text_val = text_node.get("value", "").strip()
                        if text_val:
                            text_values.append(esc(text_val))
        if text_values:
            return "<br>".join(text_values)
        # Fallback to standard rendering
        return render_rt(val)
    if isinstance(val, list):
        parts = []
        for item in val:
            if isinstance(item, dict):
                f    = item.get("fields", {})
                name = f.get("name", "")
                slug = f.get("slug", "")
                ct   = item.get("sys", {}).get("contentType", {}).get("sys", {}).get("id", "")
                path = CONTENT_TYPE_PATHS.get(ct, "/special-rules")
                if slug:
                    parts.append(f'<a href="{BASE_URL}{path}/{slug}">{esc(name)}</a>')
                elif name:
                    parts.append(esc(name))
            else:
                parts.append(esc(str(item)))
        return ", ".join(parts) if parts else "-"
    return esc(str(val))


def _format_special_rules_cell(val):
    """
    Format special rules as a vertical list using <span class="detailed-link"> elements.
    Each rule gets wrapped in a span so the CSS stacks them on separate lines.
    SVG icons are removed for a cleaner appearance.
    
    Handles both:
    - List of linked entries (most common for unit pages)
    - Rich-text documents with entry-hyperlinks (weapons-of-war embedded profiles)
    """
    if not _is_present(val):
        return "-"
    
    # Handle rich-text documents (extract entry-hyperlinks and format them)
    if isinstance(val, dict) and "content" in val:
        # Extract all entry-hyperlinks from the rich-text document
        links = collect_links(val, "rules")
        if links:
            parts = []
            for href, label in links:
                parts.append(
                    f'<span class="detailed-link">'
                    f'<a href="{href}">{label}</a>'
                    f'</span>'
                )
            return "".join(parts)
        # If no links found, fall back to standard rich-text rendering
        return render_rt(val)
    
    # Handle list of linked entries (most common for special rules)
    if isinstance(val, list):
        parts = []
        for item in val:
            if isinstance(item, dict):
                f    = item.get("fields", {})
                name = f.get("name", "")
                slug = f.get("slug", "")
                ct   = item.get("sys", {}).get("contentType", {}).get("sys", {}).get("id", "")
                path = CONTENT_TYPE_PATHS.get(ct, "/special-rules")
                if slug:
                    parts.append(
                        f'<span class="detailed-link">'
                        f'<a href="{BASE_URL}{path}/{slug}">{esc(name)}</a>'
                        f'</span>'
                    )
                elif name:
                    parts.append(f'<span class="detailed-link">{esc(name)}</span>')
            else:
                parts.append(f'<span class="detailed-link">{esc(str(item))}</span>')
        
        return "".join(parts) if parts else "-"
    
    return esc(str(val))


# -- shared HTML shell (pure HTML, zero JavaScript) ---------------------------

def html_shell(title_text, body_html, canonical_path):
    css_path   = f"{CSS_BASE}/_next/static/css"
    disclaimer = (
        '<footer class="german-comp-disclaimer">'
        '<p><em>This ruleset has been modified for German Comp use only. '
        'It is not legal for any other Old World comp, official or otherwise.</em></p>'
        '</footer>'
    )
    return f"""<!DOCTYPE html>
<html lang="en" class="index-tow">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="apple-touch-icon" sizes="180x180" href="https://tow.whfb.app/icons/tow/apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="/owb/rules/icons/tow/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/owb/rules/icons/tow/favicon-16x16.png">
    <link rel="manifest" href="/owb/rules/icons/tow/site.webmanifest">
    <link rel="shortcut icon" href="/owb/rules/icons/tow/favicon.ico">
    <meta name="theme-color" content="#ffffff">
    <title>{esc(title_text)} | Warhammer: The Old World</title>
    <link rel="canonical" href="{canonical_path}">
    <link rel="preload" href="{css_path}/29367497e701a5f5.css" as="style">
    <link rel="stylesheet" href="{css_path}/29367497e701a5f5.css">
    <link rel="preload" href="{css_path}/0f8fcb57f7477acb.css" as="style">
    <link rel="stylesheet" href="{css_path}/0f8fcb57f7477acb.css">
    <style>
      /* Make weapon profile tables full width */
      .weapon-profile-table {{
        width: 100%;
      }}
      /* Center-align all cells in weapon profile tables */
      .weapon-profile-table tbody td {{
        text-align: center;
        vertical-align: middle;
      }}
      /* Stack special rules vertically using spans */
      .profile-table span {{
        display: block;
        margin: 0;
      }}
      .profile-table span:nth-of-type(n+2) {{
        margin-top: .25rem !important;
      }}
    </style>
  </head>
  <body>
    <div id="__next">
      <div data-test-id="cf-ui-workbench" class="css-1kvywv3 default-view tow-index">
        <div class="css-9szchg">
          <main data-test-id="cf-ui-workbench-content" id="main-content" class="css-17h5a9m main-content">
            <div class="css-flqhol">
              <p class="minimal-source">
                <span>Source: <a href="https://tow.whfb.app" target="_blank">Warhammer: The Old World Online Rules Index</a></span>
              </p>
{body_html}
            </div>
            {disclaimer}
          </main>
        </div>
      </div>
    </div>
    <style>
      /* Minimal mode styling - matches tow.whfb.app minimal header */
      body.minimal-mode .minimal-source {{
        font-size: 14px;
        margin: 10px 0;
        padding: 0;
      }}
      
      body.minimal-mode .minimal-source span {{
        display: none;
      }}
      
      body.minimal-mode .minimal-source::before {{
        content: 'Back';
        color: #0066cc;
        text-decoration: none;
        margin-right: 20px;
        cursor: pointer;
      }}
      
      body.minimal-mode .minimal-source::after {{
        content: 'Source: ';
        margin-left: 0;
      }}
      
      body.minimal-mode .minimal-source a {{
        color: #0066cc;
        text-decoration: none;
        font-weight: normal;
      }}
      
      body.minimal-mode .minimal-source a:hover {{
        text-decoration: underline;
      }}
      
      /* Hide the full header elements in minimal mode */
      body.minimal-mode .css-1kvywv3 {{
        padding: 10px;
      }}
    </style>
    <script>
      // Check for minimal=true parameter and apply minimal mode
      (function() {{
        const urlParams = new URLSearchParams(window.location.search);
        const isMinimal = urlParams.get('minimal') === 'true';
        
        if (isMinimal) {{
          document.body.classList.add('minimal-mode');
          
          // Add back button functionality
          const minimalSource = document.querySelector('.minimal-source');
          if (minimalSource) {{
            minimalSource.style.cursor = 'pointer';
            minimalSource.addEventListener('click', function(e) {{
              if (e.target === this || e.offsetX < 60) {{
                window.history.back();
              }}
            }});
          }}
          
          // Add minimal=true to all tow.whfb.app links for consistent navigation
          document.querySelectorAll('a[href^="https://tow.whfb.app"]').forEach(function(link) {{
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
          }});
        }}
      }})();
    </script>
  </body>
</html>
"""


# -- shared sub-renderers -----------------------------------------------------

def render_detail_link(obj, path):
    if isinstance(obj, list):
        obj = obj[0] if obj else None
    if not isinstance(obj, dict):
        return ""
    f = obj.get("fields", {})
    return (
        f'<span class="unit-profile__details__link">'
        f'<a href="{BASE_URL}{path}/{f.get("slug", "")}">{esc(f.get("name", ""))}</a>'
        f'</span>'
    )


def render_equipment(field):
    if not field:
        return ""
    if isinstance(field, dict) and "content" in field:
        body = render_rt(field, "equipment")
    elif isinstance(field, list):
        lis = ""
        for item in field:
            if not isinstance(item, dict):
                continue
            f     = item.get("fields", {})
            link  = f'<a href="{BASE_URL}/weapons-of-war/{f.get("slug", "")}">{esc(f.get("name", ""))}</a>'
            group = f.get("groupName", "")
            note  = f.get("note", "")
            inner = f"<b>{esc(group)}:</b> {esc(note)} {link}" if group else link
            lis  += f"\n              <li>\n                <p>{inner}</p>\n              </li>"
        body = f"<ul>{lis}\n            </ul>\n            <p></p>"
    else:
        return ""
    return (
        f'\n          <div class="unit-profile__details--equipment">'
        f'\n            <strong>Equipment:</strong>{body}'
        f'\n          </div>'
    )


def render_special_rules(field):
    pairs = []
    if isinstance(field, dict) and "content" in field:
        pairs = collect_links(field, "rules")
    elif isinstance(field, list):
        for r in field:
            if isinstance(r, dict) and "content" in r:
                pairs.extend(collect_links(r, "rules"))
            elif isinstance(r, dict):
                f     = r.get("fields", {})
                label = esc(f.get("name", ""))
                if f.get("note"):
                    label += f' ({esc(f["note"])})'
                pairs.append((
                    f'{BASE_URL}/special-rules/{f.get("slug", "")}',
                    label
                ))
    if not pairs:
        return ""
    links = ", ".join(f'<a href="{h}">{l}</a>' for h, l in pairs)
    return (
        f'\n          <div class="unit-profile__details--special-rules unit-profile__details--link-list">'
        f'\n            <strong>Special Rules:</strong> {links}'
        f'\n          </div>'
    )


def render_timestamp(last_upd):
    if not last_upd:
        return ""
    return (
        f'\n        <div class="breadcrumb__wrapper">'
        f'\n          <ul class="breadcrumb">'
        f'\n            <li class="update-timestamp">Last update: {esc(last_upd)}</li>'
        f'\n          </ul>'
        f'\n        </div>'
    )


def render_profile_table(fields, slug):
    """
    Build the Range / Strength / Armour Piercing / Special Rules table
    used by both weapons-of-war and magic-item pages.
    Returns empty string if none of the profile fields are present.
    """
    profile_vals = {k: fields.get(k) for k, _ in WEAPON_PROFILE_FIELDS}
    has_profile  = any(_is_present(v) for v in profile_vals.values())
    if not has_profile:
        return ""

    sr_field    = fields.get("specialRules")
    sr_col_html = _format_special_rules_cell(sr_field) if _is_present(sr_field) else "-"

    def _th(label):
        return f'\n                <th class="css-9p6xbs" data-test-id="cf-ui-table-cell">{label}</th>'

    def _td(k):
        return (
            f'\n                <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">'
            f'{_scalar_or_rt(profile_vals.get(k))}</td>'
        )

    return (
        f'\n        <div class="table-wrapper {slug}">'
        f'\n          <table class="generic-table weapon-profile-table profile-table css-1hz7skb"'
        f' data-test-id="cf-ui-table" cellpadding="0" cellspacing="0">'
        f'\n            <thead class="css-1sojo49" data-test-id="cf-ui-table-head">'
        f'\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        + _th("Range")
        + _th("Strength")
        + _th("Armour Piercing")
        + _th("Special Rules")
        + f'\n              </tr>'
        f'\n            </thead>'
        f'\n            <tbody class="css-0" data-test-id="cf-ui-table-body">'
        f'\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        + _td("range")
        + _td("strength")
        + _td("armourPiercing")
        + f'\n                <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{sr_col_html}</td>'
        + f'\n              </tr>'
        f'\n            </tbody>'
        f'\n          </table>'
        f'\n        </div>'
    )


# -- unit page renderer -------------------------------------------------------

def render_unit(fields, slug):
    name      = fields.get("name", slug)
    army      = fields.get("army") or {}
    army_f    = army.get("fields", {}) if isinstance(army, dict) else {}
    army_name = army_f.get("name", "")
    army_slug = army_f.get("slug", "")
    last_upd  = fields.get("lastUpdated", "")
    cost      = fields.get("cost", "")
    base_size = fields.get("baseSize", "")
    unit_size = fields.get("unitSize", "")
    armour    = fields.get("armourValue") or ""

    th     = '            <th class="css-9p6xbs" data-test-id="cf-ui-table-cell">'
    header = f'{th}</th>\n' + "".join(f'{th}{k}</th>\n' for k in STAT_KEYS[1:])

    rows = ""
    for row_idx, row in enumerate(fields.get("unitProfile", [])):
        unit_name = row.get("Name", f"Unit {row_idx + 1}")
        rows += f'\n            <!-- Stats for: {unit_name} -->'
        rows += f'\n            <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        for k in STAT_KEYS:
            val       = str(row.get(k)) if row.get(k) is not None else "-"
            stat_name = STAT_NAMES.get(k, k)
            rows += f'\n              <!-- {stat_name}: {val} -->'
            rows += f'\n              <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{esc(val)}</td>'
        rows += '\n            </tr>'

    table = (
        f'\n        <div class="table-wrapper {slug}">'
        f'\n          <table class="generic-table unit-profile-table css-1hz7skb"'
        f' data-test-id="cf-ui-table" cellpadding="0" cellspacing="0">'
        f'\n            <thead class="css-1sojo49" data-test-id="cf-ui-table-head">'
        f'\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        f'\n{header}              </tr>'
        f'\n            </thead>'
        f'\n            <tbody class="css-0" data-test-id="cf-ui-table-body">{rows}'
        f'\n            </tbody>'
        f'\n          </table>'
        f'\n        </div>'
    )

    def detail(css, label, val):
        return (
            f'\n          <div class="unit-profile__details--{css}">'
            f'\n            <strong>{label}:</strong> {val}'
            f'\n          </div>'
        )

    details = (
        f'\n        <div class="unit-profile__details">'
        + detail("points",        "Cost",          f"{esc(str(cost))} points per model")
        + detail("unit-category", "Unit Category", render_detail_link(fields.get("unitCategory"), "/troop-types-in-detail"))
        + detail("troop-type",    "Troop Type",    render_detail_link(fields.get("troopType"),    "/troop-types-in-detail"))
        + detail("base-size",     "Base Size",     esc(str(base_size)))
        + detail("unit-size",     "Unit Size",     esc(str(unit_size)))
        + (detail("armour-value", "Armour Value",  esc(str(armour))) if armour else "")
        + render_equipment(fields.get("equipment"))
        + render_special_rules(fields.get("specialRules"))
        + '\n        </div>'
    )

    breadcrumb = ""
    if army_slug:
        date_li    = f'\n            <li class="update-timestamp">Last update: {esc(last_upd)}</li>' if last_upd else ""
        breadcrumb = (
            f'\n        <div class="breadcrumb__wrapper">\n'
            f'          <ul class="breadcrumb">\n'
            f'            <li class="breadcrumb-link">\n'
            f'              <a href="{BASE_URL}/army/{army_slug}">{esc(army_name)}</a>\n'
            f'            </li>\n'
            f'          </ul>\n'
            f'          <ul class="breadcrumb">{date_li}\n'
            f'          </ul>\n'
            f'        </div>'
        )

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>{breadcrumb}'
        f'\n              <div class="unit-profile {slug}">{table}{details}'
        f'\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


# -- weapons-of-war page renderer ---------------------------------------------

def render_weapon(fields, slug):
    """
    Render a weapons-of-war page.
    Layout (matching live site):
      h1  name
      [breadcrumb timestamp]
      div.rule-entry.weapon-of-war
        [description para -- italic flavour text]
        [profile table: Range | Strength | Armour Piercing | Special Rules]
        [notes block: Notes: <bullet list>]
    """
    name     = fields.get("name", slug)
    last_upd = fields.get("lastUpdated", "")

    # Flavour / description text (italic, above the table)
    desc_val  = first_field(fields, DESCRIPTION_FIELD_CANDIDATES)
    desc_html = f'\n        <div class="rule-entry__description"><em>{rt_to_html(desc_val)}</em></div>' if desc_val else ""

    # Profile table: check top-level fields first, then look for embedded weaponProfile
    profile_fields = fields
    if not any(_is_present(fields.get(k)) for k, _ in WEAPON_PROFILE_FIELDS):
        # No top-level profile fields, try to extract from embedded weaponProfile in body
        body_val = fields.get("body")
        if body_val:
            embedded_profile = extract_embedded_weapon_profile(body_val)
            if embedded_profile:
                profile_fields = embedded_profile

    profile_html = render_profile_table(profile_fields, slug)

    # Notes / rules body (bullet list, below the table)
    notes_val  = first_field(fields, NOTES_FIELD_CANDIDATES)
    notes_html = rt_to_html(notes_val)
    notes_block = (
        f'\n        <div class="rule-entry__notes">'
        f'\n          <em>Notes:</em>'
        f'\n          {notes_html}'
        f'\n        </div>'
    ) if notes_html else ""

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>'
        f'{render_timestamp(last_upd)}'
        f'\n              <div class="rule-entry weapon-of-war {slug}">'
        f'{desc_html}'
        f'{profile_html}'
        f'{notes_block}'
        f'\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


# -- magic-item page renderer -------------------------------------------------

def render_magic_item(fields, slug):
    """
    Render a magic-item page.
    Layout (matching live site):
      h1  name
      [breadcrumb timestamp]
      div.rule-entry.magic-item
        div.unit-profile__details  (type + points badge)
        [description para -- italic flavour text]
        div.rule-entry__notes  Notes: <body rich-text, includes embedded table + bullet list>
    """
    name      = fields.get("name", slug)
    last_upd  = fields.get("lastUpdated", "")
    cost      = fields.get("cost") or fields.get("points") or ""
    item_type = fields.get("type") or fields.get("itemType") or ""

    # Resolve linked item-type entry to a plain string
    if isinstance(item_type, dict):
        item_type = item_type.get("fields", {}).get("name", "") or ""

    # --- type + points badge ---
    meta_parts = []
    if item_type:
        meta_parts.append(f'<span class="magic-item__type">{esc(str(item_type))}</span>')
    if cost:
        meta_parts.append(f'<span class="magic-item__cost">{esc(str(cost))} points</span>')
    meta_html = ""
    if meta_parts:
        meta_html = (
            f'\n        <div class="unit-profile__details">'
            f'\n          <div class="unit-profile__details--points">'
            f'\n            {" &nbsp;&middot;&nbsp; ".join(meta_parts)}'
            f'\n          </div>'
            f'\n        </div>'
        )

    # --- flavour / description text (italic, above the body) ---
    desc_val  = first_field(fields, DESCRIPTION_FIELD_CANDIDATES)
    desc_html = (
        f'\n        <div class="rule-entry__description"><em>{rt_to_html(desc_val)}</em></div>'
    ) if desc_val else ""

    # --- body: table + notes (all in one rich-text field) ---
    # For magic items, 'body' contains the embedded table node plus the notes bullet list.
    body_val  = first_field(fields, NOTES_FIELD_CANDIDATES)
    body_html = rt_to_html(body_val)
    notes_block = (
        f'\n        <div class="rule-entry__notes">'
        f'\n          <em>Notes:</em>'
        f'\n          {body_html}'
        f'\n        </div>'
    ) if body_html else ""

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>'
        f'{render_timestamp(last_upd)}'
        f'\n              <div class="rule-entry magic-item {slug}">'
        f'{meta_html}'
        f'{desc_html}'
        f'{notes_block}'
        f'\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


# -- special-rule page renderer -----------------------------------------------

def render_special_rule(fields, slug):
    """
    Render a special-rule page.
    Layout (matching live site):
      h1  name
      [breadcrumb timestamp]
      div.rule-entry.special-rule
        [description para -- italic flavour text]
        div.rule-entry__notes  <body rich-text with paragraphs and lists>
    """
    name     = fields.get("name", slug)
    last_upd = fields.get("lastUpdated", "")

    # Flavour / description text (italic, above the body)
    desc_val  = first_field(fields, DESCRIPTION_FIELD_CANDIDATES)
    desc_html = f'\n        <div class="rule-entry__description"><em>{rt_to_html(desc_val)}</em></div>' if desc_val else ""

    # Body text (main rule content)
    body_val  = first_field(fields, NOTES_FIELD_CANDIDATES)
    body_html = rt_to_html(body_val)
    notes_block = (
        f'\n        <div class="rule-entry__notes">'
        f'\n          {body_html}'
        f'\n        </div>'
    ) if body_html else ""

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>'
        f'{render_timestamp(last_upd)}'
        f'\n              <div class="rule-entry special-rule {slug}">'
        f'{desc_html}'
        f'{notes_block}'
        f'\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


# -- interactive stat editing (unit only) -------------------------------------

def edit_single_unit(unit_profile, unit_idx):
    selected_unit = unit_profile[unit_idx]
    unit_name     = selected_unit.get("Name", "Unit")

    print(f"\nEditing: {unit_name}")
    print("Enter the stat abbreviation (M, WS, BS, S, T, W, I, A, Ld) and new value.")
    print("Type 'done' when finished.\n")

    changes_made = False
    while True:
        print("\nCurrent values:")
        for key in EDITABLE_STATS:
            print(f"  {key}: {selected_unit.get(key, '-')}", end="  ")
        print()

        stat_input = input("\nEnter stat to edit (or 'done'): ").strip().upper()
        if stat_input.lower() == 'done':
            break
        if stat_input not in EDITABLE_STATS:
            print(f"  Invalid stat. Choose from: {', '.join(EDITABLE_STATS)}")
            continue

        current_val = selected_unit.get(stat_input, "-")
        print(f"  Current {stat_input} ({STAT_NAMES[stat_input]}): {current_val}")
        new_value   = input(f"  Enter new value (or press Enter to skip): ").strip()
        if not new_value:
            continue

        if new_value != '-':
            try:
                float(new_value) if '.' in new_value else int(new_value)
            except ValueError:
                print(f"  Invalid value '{new_value}'. Please enter a number or '-'.")
                continue

        selected_unit[stat_input] = (
            new_value if new_value == '-'
            else (int(new_value) if '.' not in new_value else float(new_value))
        )
        print(f"  ✓ Updated {stat_input} from {current_val} to {new_value}")
        changes_made = True

    return changes_made


def edit_unit_stats(fields):
    unit_profile = fields.get("unitProfile", [])
    if not unit_profile:
        print("\n  No unit profile found to edit.")
        return fields

    print("\n" + "="*60)
    print("STAT EDITING")
    print("="*60)

    if input("\nWould you like to edit unit stats? (y/n): ").strip().lower() not in ('y', 'yes'):
        print("  Skipping stat editing.")
        return fields

    print("\nCurrent Stats:")
    for idx, row in enumerate(unit_profile):
        print(f"\n  [{idx + 1}] {row.get('Name', f'Unit {idx + 1}')}")
        for key in EDITABLE_STATS:
            print(f"      {key:3s} ({STAT_NAMES.get(key, key):15s}): {row.get(key, '-')}")

    edited_units = set()
    any_changes  = False

    while True:
        unit_idx = 0
        if len(unit_profile) > 1:
            print(f"\nAvailable units: {', '.join(str(i+1) for i in range(len(unit_profile)))}")
            if edited_units:
                print(f"Already edited: {', '.join(str(i+1) for i in sorted(edited_units))}")
            while True:
                choice = input(f"\nWhich unit? (1-{len(unit_profile)} or 'done'): ").strip()
                if choice.lower() == 'done':
                    unit_idx = None
                    break
                try:
                    unit_idx = int(choice) - 1
                    if 0 <= unit_idx < len(unit_profile):
                        break
                    print(f"  Please enter a number between 1 and {len(unit_profile)}.")
                except ValueError:
                    print("  Invalid input.")

        if unit_idx is None:
            break

        if edit_single_unit(unit_profile, unit_idx):
            edited_units.add(unit_idx)
            any_changes = True

        if len(unit_profile) == 1:
            break

        if input("\nEdit another unit? (y/n): ").strip().lower() not in ('y', 'yes'):
            break

    if any_changes:
        print("\n" + "="*60 + "\nFINAL STATS AFTER EDITING:\n" + "="*60)
        for idx in sorted(edited_units):
            unit = unit_profile[idx]
            print(f"\n  {unit.get('Name', f'Unit {idx+1}')}:")
            for key in EDITABLE_STATS:
                print(f"    {key:3s} ({STAT_NAMES[key]:15s}): {unit.get(key, '-')}")
        print()
    else:
        print("\n  No changes made.")

    return fields


# -- stats extraction and formatting ------------------------------------------

def extract_stats_from_fields(fields):
    unit_profile = fields.get("unitProfile", [])
    if not unit_profile:
        return None
    stats = []
    for row in unit_profile:
        stat_dict = {
            k: ("-" if row.get(k) is None or row.get(k) == "" else str(row[k]))
            for k in STAT_KEYS
        }
        stats.append(stat_dict)
    return stats or None


def format_stats_for_js(stats):
    if not stats:
        return None
    lines = [
        "      { " + ", ".join(f'{k}: "{s.get(k, "-")}"' for k in STAT_KEYS) + " }"
        for s in stats
    ]
    return "[\n" + ",\n".join(lines) + "\n    ]"


# -- rules-map.js injection ---------------------------------------------------

def slug_to_display_name(slug):
    return slug.replace("-", " ")


def inject_rules_map_entry(slug, content_type, stats, rules_map_path):
    display_name = slug_to_display_name(slug)
    subdir       = RULES_MAP_SUBDIRS.get(content_type, content_type)
    full_url     = f"{OWB_RULES_BASE}/{subdir}/{slug}.html?minimal=true"

    if not os.path.isabs(rules_map_path):
        rules_map_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), rules_map_path
        )

    if not os.path.exists(rules_map_path):
        print(f"  [rules-map] WARNING: file not found at {rules_map_path} -- skipping")
        return

    with open(rules_map_path, "r", encoding="utf-8") as f:
        content = f.read()

    entry_exists = f'"{display_name}"' in content or f"'{display_name}'" in content

    if entry_exists:
        m = re.search(rf'"{re.escape(display_name)}":\s*\{{[^}}]*\}}', content)
        if m and "stats:" in m.group(0):
            print(f'  [rules-map] "{display_name}" already has stats -- skipping')
            return
        if stats and content_type == "unit":
            stats_js = format_stats_for_js(stats)
            if stats_js:
                pattern     = rf'("{re.escape(display_name)}":\s*\{{\s*fullUrl:[^,]+)(,?\s*\}})'
                replacement = rf'\1,\n    stats: {stats_js}\2'
                new_content, count = re.subn(pattern, replacement, content, count=1)
                if count:
                    with open(rules_map_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f'  [rules-map] Updated "{display_name}" with {len(stats)} stat row(s)')
                else:
                    print(f'  [rules-map] WARNING: could not update "{display_name}"')
        else:
            print(f'  [rules-map] "{display_name}" already exists -- skipping')
        return

    if stats and content_type == "unit":
        stats_js  = format_stats_for_js(stats)
        new_entry = (
            f'  "{display_name}": {{\n'
            f'    fullUrl: "{full_url}",\n'
            f'    stats: {stats_js}\n'
            f'  }}'
        )
    else:
        new_entry = f'  "{display_name}": {{ fullUrl: "{full_url}" }}'

    pattern     = r'(const additionalOWBRules\s*=\s*\{\n)'
    replacement = r'\1' + new_entry + ',\n'
    new_content, n = re.subn(pattern, replacement, content, count=1)

    if not n:
        print("  [rules-map] WARNING: could not locate additionalOWBRules -- skipping")
        return

    with open(rules_map_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    stat_info = f" with {len(stats)} stat row(s)" if stats and content_type == "unit" else ""
    print(f'  [rules-map] Injected{stat_info} "{display_name}" -> {full_url}')


# -- fetch & save -------------------------------------------------------------

def fetch_json(slug, content_type, build_id):
    route = FETCH_ROUTES[content_type]
    url   = f"{BASE_URL}/_next/data/{build_id}/{route}/{slug}.json"
    print(f"  [json] {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def debug_fields(fields):
    """
    Print every field key, its Python type, and a short preview of its value.
    Useful for diagnosing missing content.
    """
    print("\n" + "="*60)
    print("DEBUG: raw fields from Contentful JSON")
    print("="*60)
    for key, val in sorted(fields.items()):
        if isinstance(val, dict):
            preview = f"{{nodeType: {val.get('nodeType', '?')} ...}}" if "nodeType" in val else f"dict({list(val.keys())[:4]})"
        elif isinstance(val, list):
            preview = f"list[{len(val)}]"
        elif isinstance(val, str) and len(val) > 80:
            preview = repr(val[:80]) + "..."
        else:
            preview = repr(val)
        print(f"  {key:<28}  {type(val).__name__:<12}  {preview}")
    print("="*60 + "\n")


def fetch_and_save(slug, content_type, build_id, out_dir, rules_map_path, debug=False):
    print(f"\nFetching: {slug}  (type: {content_type})")
    try:
        data = fetch_json(slug, content_type, build_id)
    except Exception as e:
        sys.exit(f"  [error] {e}")

    fields = data.get("pageProps", {}).get("entry", {}).get("fields", {})
    if not fields:
        sys.exit(
            "  [error] No 'fields' in JSON response. "
            "The BUILD_ID may be stale -- try re-running (auto-detection will pick up a fresh one)."
        )

    if debug:
        debug_fields(fields)
        print("  [debug] Exiting without writing HTML (--debug flag set).")
        return

    if content_type == "unit":
        fields = edit_unit_stats(fields)
        stats  = extract_stats_from_fields(fields)
        if stats:
            print(f"\n  Extracted {len(stats)} stat row(s):")
            for s in stats:
                print(f"    - {s.get('Name', 'Unknown')}")
        else:
            print("  No stats found in source data.")
        html = render_unit(fields, slug)

    elif content_type == "weapons-of-war":
        stats      = None
        html       = render_weapon(fields, slug)
        desc_key   = next((k for k in DESCRIPTION_FIELD_CANDIDATES if fields.get(k)), None)
        notes_key  = next((k for k in NOTES_FIELD_CANDIDATES       if fields.get(k)), None)
        print(f"  Description field : {desc_key  or '(none)'}")
        print(f"  Notes field       : {notes_key or '(none)'}")

    elif content_type == "magic-item":
        stats      = None
        html       = render_magic_item(fields, slug)
        desc_key   = next((k for k in DESCRIPTION_FIELD_CANDIDATES if fields.get(k)), None)
        notes_key  = next((k for k in NOTES_FIELD_CANDIDATES       if fields.get(k)), None)
        print(f"  Description field : {desc_key  or '(none)'}")
        print(f"  Notes field       : {notes_key or '(none)'}")

    elif content_type == "special-rule":
        stats      = None
        html       = render_special_rule(fields, slug)
        desc_key   = next((k for k in DESCRIPTION_FIELD_CANDIDATES if fields.get(k)), None)
        notes_key  = next((k for k in NOTES_FIELD_CANDIDATES       if fields.get(k)), None)
        print(f"  Description field : {desc_key  or '(none)'}")
        print(f"  Notes field       : {notes_key or '(none)'}")

    else:
        sys.exit(f"  [error] Unknown content type: {content_type}")

    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, f"{slug}.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Saved: {dest}  ({len(html):,} bytes)")

    inject_rules_map_entry(slug, content_type, stats, rules_map_path)


# -- entry point --------------------------------------------------------------

def main():
    args = sys.argv[1:]

    if "--fetch" not in args:
        print(__doc__)
        sys.exit(1)

    i = args.index("--fetch")
    if i + 1 >= len(args):
        print(__doc__)
        sys.exit(1)
    slug = args[i + 1]

    # --type  (default: unit)
    content_type = "unit"
    if "--type" in args:
        j = args.index("--type")
        if j + 1 < len(args):
            content_type = args[j + 1]
    content_type = _normalise_type(content_type)
    if content_type not in FETCH_ROUTES:
        sys.exit(
            f"  [error] --type must be one of: {', '.join(sorted(FETCH_ROUTES.keys()))} "
            f"(or 'magic-items' as a legacy alias for 'magic-item')"
        )

    # --build  (manual BUILD_ID override; auto-detect when omitted)
    build_id = None
    if "--build" in args:
        j = args.index("--build")
        if j + 1 < len(args):
            build_id = args[j + 1]
    if not build_id:
        build_id = detect_build_id()

    # --out
    out_dir = DEFAULT_OUT_DIRS[content_type]
    if "--out" in args:
        j = args.index("--out")
        if j + 1 < len(args):
            out_dir = args[j + 1]
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), out_dir)

    # --rules-map
    rules_map_path = RULES_MAP_PATH
    if "--rules-map" in args:
        j = args.index("--rules-map")
        if j + 1 < len(args):
            rules_map_path = args[j + 1]

    # --debug
    debug = "--debug" in args

    fetch_and_save(slug, content_type, build_id, out_dir, rules_map_path, debug=debug)
    if not debug:
        print("\nDone.")


if __name__ == "__main__":
    main()
