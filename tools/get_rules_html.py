#!/usr/bin/env python3
"""
clean_unit_html.py -- Generate static HTML pages mirroring tow.whfb.app

Usage:
  python3 clean_unit_html.py --fetch <slug> [--type unit|weapons-of-war|magic-item|special-rule|troop-types-in-detail] [--out <dir>]

  --type   defaults to 'unit' for backward compatibility.
           Use 'magic-item' (singular) to match the live site URL.
  --out    defaults to ../rules/<type>/ relative to this script.
  --build  optional: override the Next.js BUILD_ID (auto-detected when omitted).
  --debug  dump all raw field keys and types from the JSON response, then exit.

Examples:
  python3 clean_unit_html.py --fetch halberd --type weapons-of-war
  python3 clean_unit_html.py --fetch the-fellblade --type magic-item
  python3 clean_unit_html.py --fetch the-fellblade --type magic-item --debug
  python3 clean_unit_html.py --fetch fly --type special-rule
  python3 clean_unit_html.py --fetch grave-guard
  python3 clean_unit_html.py --fetch monstrous-infantry --type troop-types-in-detail
"""

import sys, os, re, json, urllib.request, argparse, datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://tow.whfb.app"
CSS_BASE = "/owb/rules"

# Log to file instead of console
LOG_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
LOG_BASENAME = "clean_unit_html.log"


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log_path():
    ts = datetime.datetime.now().strftime("%Y%m%d")
    return os.path.join(LOG_DIR, f"{LOG_BASENAME}.{ts}")


def log(msg):
    """Append a line to the log file."""
    ensure_log_dir()
    with open(log_path(), "a", encoding="utf-8") as f:
        f.write(msg.rstrip() + "\n")


def die(msg, code=1):
    log(msg)
    sys.exit(msg)


# Maps the --type flag value to the exact Next.js page-route segment
FETCH_ROUTES = {
    "unit":                   "unit",
    "weapons-of-war":         "weapons-of-war",
    "magic-item":             "magic-item",
    "special-rule":           "special-rules",
    "troop-types-in-detail":  "troop-types-in-detail",
}

# Default local output dirs relative to this script
DEFAULT_OUT_DIRS = {
    "unit":                   "../rules/unit",
    "weapons-of-war":         "../rules/weapons-of-war",
    "magic-item":             "../rules/magic-items",
    "magic-items":            "../rules/magic-items",
    "special-rule":           "../rules/special-rules",
    "troop-types-in-detail":  "../rules/troop-types-in-detail",
}

# rules-map fullUrl subdirectory names
RULES_MAP_SUBDIRS = {
    "unit":                   "unit",
    "weapons-of-war":         "weapons-of-war",
    "magic-item":             "magic-items",
    "magic-items":            "magic-items",
    "special-rule":           "special-rules",
    "troop-types-in-detail":  "troop-types-in-detail",
}

OWB_RULES_BASE = "https://owapps.grra.me/owb/rules"

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

RULE_TYPE_IDS = {
    "1cxV0Jnvb1D701DgF8Y7Op": "/troop-types-in-detail",
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
EDITABLE_STATS = [k for k in STAT_KEYS if k != "Name"]

WEAPON_PROFILE_FIELDS = [
    ("range",          "Range"),
    ("strength",       "Strength"),
    ("armourPiercing", "Armour Piercing"),
]

DESCRIPTION_FIELD_CANDIDATES = [
    "description",
    "flavourText",
    "flavour",
    "intro",
    "summary",
]

NOTES_FIELD_CANDIDATES = [
    "body",
    "notes",
    "rules",
    "text",
    "content",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise_type(content_type):
    return "magic-item" if content_type == "magic-items" else content_type


def _is_present(val):
    if val is None:
        return False
    return not (isinstance(val, str) and val.strip() == "")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def first_field(fields, candidates):
    for key in candidates:
        val = fields.get(key)
        if _is_present(val):
            return val
    return None


# ---------------------------------------------------------------------------
# BUILD_ID detection
# ---------------------------------------------------------------------------

def detect_build_id():
    log("  [build] Auto-detecting BUILD_ID from tow.whfb.app ...")
    req = urllib.request.Request(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")
    except Exception as e:
        die(f"  [error] Could not fetch {BASE_URL} to detect BUILD_ID: {e}")

    m = re.search(
        r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    if m:
        try:
            build_id = json.loads(m.group(1)).get("buildId", "")
            if build_id:
                log(f"  [build] Detected BUILD_ID: {build_id}")
                return build_id
        except (json.JSONDecodeError, AttributeError):
            pass

    m2 = re.search(r'/_next/data/([^/"]+)/', html)
    if m2:
        build_id = m2.group(1)
        log(f"  [build] Fallback BUILD_ID: {build_id}")
        return build_id

    die("  [error] Could not detect BUILD_ID from tow.whfb.app. Use --build <id> to supply it manually.")


# ---------------------------------------------------------------------------
# Rich text rendering
# ---------------------------------------------------------------------------

def extract_embedded_weapon_profile(body_rt):
    if not isinstance(body_rt, dict):
        return None

    node_type = body_rt.get("nodeType", "")
    if node_type == "embedded-entry-block":
        target = body_rt.get("data", {}).get("target", {})
        ct = target.get("sys", {}).get("contentType", {}).get("sys", {}).get("id", "")
        if ct == "weaponProfile":
            return target.get("fields", {})

    for child in body_rt.get("content", []):
        result = extract_embedded_weapon_profile(child)
        if result:
            return result
    return None


def entry_url(target, context="auto"):
    if not isinstance(target, dict):
        return BASE_URL

    fields = target.get("fields", {})
    slug   = fields.get("slug", "")
    if not slug:
        return BASE_URL

    if context == "equipment":
        return f"{BASE_URL}/weapons-of-war/{slug}"
    if context == "rules":
        return f"{BASE_URL}/special-rules/{slug}"

    ct = target.get("sys", {}).get("contentType", {}).get("sys", {}).get("id", "")

    if ct == "rule":
        rule_type_list = fields.get("ruleType", [])
        rule_type_id = None
        if isinstance(rule_type_list, list) and rule_type_list:
            first_rt = rule_type_list[0]
            if isinstance(first_rt, dict):
                rule_type_id = first_rt.get("sys", {}).get("id", "")
        if rule_type_id and rule_type_id in RULE_TYPE_IDS:
            path = RULE_TYPE_IDS[rule_type_id]
            return f"{BASE_URL}{path}/{slug}"
        return f"{BASE_URL}/special-rules/{slug}"

    path = CONTENT_TYPE_PATHS.get(ct, "")
    if not path:
        return f"{BASE_URL}/{slug}"
    return f"{BASE_URL}{path}/{slug}"


def render_rt(node, ctx="auto"):
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

    if nt == "hyperlink":
        return f'<a href="{esc(node["data"]["uri"])}">{inner()}</a>'

    if nt == "entry-hyperlink":
        return f'<a href="{entry_url(node["data"]["target"], "auto")}">{inner()}</a>'

    if nt == "paragraph":
        if ctx == "table-cell":
            text_values = [
                esc(child.get("value", ""))
                for child in content
                if isinstance(child, dict) and child.get("nodeType") == "text"
            ]
            if len(text_values) > 1:
                return "<br>".join(text_values)
        return f"<p>{inner()}</p>"

    if nt == "unordered-list":
        return "<ul>" + "".join(f"<li>{render_rt(i, ctx)}</li>" for i in content) + "</ul>"

    if nt == "ordered-list":
        return "<ol>" + "".join(f"<li>{render_rt(i, ctx)}</li>" for i in content) + "</ol>"

    if nt == "table":
        rows_html = "".join(render_rt(row, ctx) for row in content)
        return (
            '<table class="generic-table weapon-profile-table css-1hz7skb" '
            'data-test-id="cf-ui-table" cellpadding="0" cellspacing="0">'
            f"{rows_html}</table>"
        )

    if nt == "table-row":
        cells_html = "".join(render_rt(cell, ctx) for cell in content)
        return f'<tr class="css-1sydf7g" data-test-id="cf-ui-table-row">{cells_html}</tr>'

    if nt == "table-header-cell":
        return (
            '<th class="css-9p6xbs" data-test-id="cf-ui-table-cell">'
            f'{render_rt(content[0], "table-cell") if content else ""}</th>'
        )

    if nt == "table-cell":
        cell_html = ""
        for child in content:
            if isinstance(child, dict) and child.get("nodeType") == "paragraph":
                para_content = child.get("content", [])
                text_values = [
                    esc(tn.get("value", ""))
                    for tn in para_content
                    if isinstance(tn, dict) and tn.get("nodeType") == "text"
                ]
                cell_html += "<br>".join(text_values) if text_values else render_rt(child, "table-cell")
            else:
                cell_html += render_rt(child, "table-cell")
        return f'<td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{cell_html}</td>'

    return inner()


def rt_to_html(val):
    if not _is_present(val):
        return ""
    if isinstance(val, dict) and "content" in val:
        return render_rt(val)
    if isinstance(val, str):
        return f"<p>{esc(val)}</p>"
    return ""


def collect_links(node, ctx="auto"):
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
    links = []
    for c in content:
        links.extend(collect_links(c, ctx))
    return links


def _scalar_or_rt(val):
    if not _is_present(val):
        return "-"
    if isinstance(val, dict) and "content" in val:
        text_values = []
        for para in val.get("content", []):
            if isinstance(para, dict) and para.get("nodeType") == "paragraph":
                for text_node in para.get("content", []):
                    if isinstance(text_node, dict) and text_node.get("nodeType") == "text":
                        t = text_node.get("value", "").strip()
                        if t:
                            text_values.append(esc(t))
        if text_values:
            return "<br>".join(text_values)
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
    if not _is_present(val):
        return "-"
    if isinstance(val, dict) and "content" in val:
        links = collect_links(val, "rules")
        if links:
            return "".join(
                f'<span class="detailed-link"><a href="{href}">{label}</a></span>'
                for href, label in links
            )
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
                    parts.append(
                        f'<span class="detailed-link"><a href="{BASE_URL}{path}/{slug}">{esc(name)}</a></span>'
                    )
                elif name:
                    parts.append(f'<span class="detailed-link">{esc(name)}</span>')
            else:
                parts.append(f'<span class="detailed-link">{esc(str(item))}</span>')
        return "".join(parts) if parts else "-"
    return esc(str(val))


# ---------------------------------------------------------------------------
# HTML shell
# ---------------------------------------------------------------------------

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
      .weapon-profile-table {{
        width: 100%;
      }}
      .weapon-profile-table tbody td {{
        text-align: center;
        vertical-align: middle;
      }}
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
      body.minimal-mode .css-1kvywv3 {{
        padding: 10px;
      }}
    </style>
    <script>
      (function() {{
        const urlParams = new URLSearchParams(window.location.search);
        const isMinimal = urlParams.get('minimal') === 'true';
        if (isMinimal) {{
          document.body.classList.add('minimal-mode');
          const minimalSource = document.querySelector('.minimal-source');
          if (minimalSource) {{
            minimalSource.style.cursor = 'pointer';
            minimalSource.addEventListener('click', function(e) {{
              if (e.target === this || e.offsetX < 60) {{
                window.history.back();
              }}
            }});
          }}
          document.querySelectorAll('a[href^="https://tow.whfb.app"]').forEach(function(link) {{
            const href = link.getAttribute('href');
            if (href.includes('minimal=')) return;
            const skipExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js', '.woff', '.woff2', '.ttf', '.webmanifest', '.json'];
            if (skipExtensions.some(ext => href.toLowerCase().endsWith(ext))) return;
            if (href.includes('/icons/') || href.includes('/static/') || href.includes('/_next/')) return;
            const separator = href.includes('?') ? '&' : '?';
            link.setAttribute('href', href + separator + 'minimal=true');
          }});
        }}
      }})();
    </script>
  </body>
</html>
"""


# ---------------------------------------------------------------------------
# Shared sub-renderers
# ---------------------------------------------------------------------------

def render_detail_link(obj, path):
    if isinstance(obj, list):
        obj = obj[0] if obj else None
    if not isinstance(obj, dict):
        return ""
    f = obj.get("fields", {})
    return (
        '<span class="unit-profile__details__link">'
        f'<a href="{BASE_URL}{path}/{f.get("slug", "")}">{esc(f.get("name", ""))}</a>'
        '</span>'
    )


def render_equipment(field):
    if not field:
        return ""
    if isinstance(field, dict) and "content" in field:
        body = render_rt(field, "equipment")
    elif isinstance(field, list):
        lis = []
        for item in field:
            if not isinstance(item, dict):
                continue
            f     = item.get("fields", {})
            link  = f'<a href="{BASE_URL}/weapons-of-war/{f.get("slug", "")}">{esc(f.get("name", ""))}</a>'
            group = f.get("groupName", "")
            note  = f.get("note", "")
            inner = f"<b>{esc(group)}:</b> {esc(note)} {link}" if group else link
            lis.append(f"<li><p>{inner}</p></li>")
        body = "<ul>\n" + "\n".join(lis) + "\n</ul>\n<p></p>"
    else:
        return ""
    return (
        '\n          <div class="unit-profile__details--equipment">'
        f'\n            <strong>Equipment:</strong>{body}'
        '\n          </div>'
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
                pairs.append((f'{BASE_URL}/special-rules/{f.get("slug", "")}', label))
    if not pairs:
        return ""
    links = ", ".join(f'<a href="{h}">{l}</a>' for h, l in pairs)
    return (
        '\n          <div class="unit-profile__details--special-rules unit-profile__details--link-list">'
        f'\n            <strong>Special Rules:</strong> {links}'
        '\n          </div>'
    )


def render_timestamp(last_upd):
    if not last_upd:
        return ""
    return (
        '\n        <div class="breadcrumb__wrapper">'
        '\n          <ul class="breadcrumb">'
        f'\n            <li class="update-timestamp">Last update: {esc(last_upd)}</li>'
        '\n          </ul>'
        '\n        </div>'
    )


def render_profile_table(fields, slug):
    profile_vals = {k: fields.get(k) for k, _ in WEAPON_PROFILE_FIELDS}
    if not any(_is_present(v) for v in profile_vals.values()):
        return ""

    sr_field    = fields.get("specialRules")
    sr_col_html = _format_special_rules_cell(sr_field) if _is_present(sr_field) else "-"

    def _th(label):
        return f'\n                <th class="css-9p6xbs" data-test-id="cf-ui-table-cell">{label}</th>'

    def _td(k):
        return (
            '\n                <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">'
            f'{_scalar_or_rt(profile_vals.get(k))}</td>'
        )

    return (
        f'\n        <div class="table-wrapper {slug}">'
        '\n          <table class="generic-table weapon-profile-table profile-table css-1hz7skb"'
        ' data-test-id="cf-ui-table" cellpadding="0" cellspacing="0">'
        '\n            <thead class="css-1sojo49" data-test-id="cf-ui-table-head">'
        '\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        + _th("Range") + _th("Strength") + _th("Armour Piercing") + _th("Special Rules")
        + '\n              </tr>'
        '\n            </thead>'
        '\n            <tbody class="css-0" data-test-id="cf-ui-table-body">'
        '\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        + _td("range") + _td("strength") + _td("armourPiercing")
        + f'\n                <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{sr_col_html}</td>'
        + '\n              </tr>'
        '\n            </tbody>'
        '\n          </table>'
        '\n        </div>'
    )


# ---------------------------------------------------------------------------
# Page renderers
# ---------------------------------------------------------------------------

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

    rows = []
    for row_idx, row in enumerate(fields.get("unitProfile", [])):
        unit_name = row.get("Name", f"Unit {row_idx + 1}")
        row_html = [
            f'            <!-- Stats for: {unit_name} -->',
            '            <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        ]
        for k in STAT_KEYS:
            val       = str(row.get(k)) if row.get(k) is not None else "-"
            stat_name = STAT_NAMES.get(k, k)
            row_html.append(f'              <!-- {stat_name}: {val} -->')
            row_html.append(
                f'              <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{esc(val)}</td>'
            )
        row_html.append("            </tr>")
        rows.append("\n".join(row_html))

    table = (
        f'\n        <div class="table-wrapper {slug}">'
        '\n          <table class="generic-table unit-profile-table css-1hz7skb"'
        ' data-test-id="cf-ui-table" cellpadding="0" cellspacing="0">'
        '\n            <thead class="css-1sojo49" data-test-id="cf-ui-table-head">'
        '\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        f'\n{header}              </tr>'
        '\n            </thead>'
        '\n            <tbody class="css-0" data-test-id="cf-ui-table-body">'
        + "\n".join(rows) +
        '\n            </tbody>'
        '\n          </table>'
        '\n        </div>'
    )

    def detail(css, label, val):
        return (
            f'\n          <div class="unit-profile__details--{css}">'
            f'\n            <strong>{label}:</strong> {val}'
            '\n          </div>'
        )

    details = (
        '\n        <div class="unit-profile__details">'
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
        date_li = f'\n            <li class="update-timestamp">Last update: {esc(last_upd)}</li>' if last_upd else ""
        breadcrumb = (
            '\n        <div class="breadcrumb__wrapper">\n'
            '          <ul class="breadcrumb">\n'
            f'            <li class="breadcrumb-link">\n'
            f'              <a href="{BASE_URL}/army/{army_slug}">{esc(army_name)}</a>\n'
            '            </li>\n'
            '          </ul>\n'
            f'          <ul class="breadcrumb">{date_li}\n'
            '          </ul>\n'
            '        </div>'
        )

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>{breadcrumb}'
        f'\n              <div class="unit-profile {slug}">{table}{details}'
        '\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


def render_weapon(fields, slug):
    name     = fields.get("name", slug)
    last_upd = fields.get("lastUpdated", "")

    desc_val  = first_field(fields, DESCRIPTION_FIELD_CANDIDATES)
    desc_html = f'\n        <div class="rule-entry__description"><em>{rt_to_html(desc_val)}</em></div>' if desc_val else ""

    profile_fields = fields
    if not any(_is_present(fields.get(k)) for k, _ in WEAPON_PROFILE_FIELDS):
        body_val = fields.get("body")
        embedded_profile = extract_embedded_weapon_profile(body_val) if body_val else None
        if embedded_profile:
            profile_fields = embedded_profile

    profile_html = render_profile_table(profile_fields, slug)

    notes_val  = first_field(fields, NOTES_FIELD_CANDIDATES)
    notes_html = rt_to_html(notes_val)
    notes_block = (
        '\n        <div class="rule-entry__notes">'
        '\n          <em>Notes:</em>'
        f'\n          {notes_html}'
        '\n        </div>'
    ) if notes_html else ""

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>'
        f'{render_timestamp(last_upd)}'
        f'\n              <div class="rule-entry weapon-of-war {slug}">'
        f'{desc_html}{profile_html}{notes_block}'
        '\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


def render_magic_item(fields, slug):
    name      = fields.get("name", slug)
    last_upd  = fields.get("lastUpdated", "")
    cost      = fields.get("cost") or fields.get("points") or ""
    item_type = fields.get("type") or fields.get("itemType") or ""

    if isinstance(item_type, dict):
        item_type = item_type.get("fields", {}).get("name", "") or ""

    meta_parts = []
    if item_type:
        meta_parts.append(f'<span class="magic-item__type">{esc(str(item_type))}</span>')
    if cost:
        meta_parts.append(f'<span class="magic-item__cost">{esc(str(cost))} points</span>')
    meta_html = ""
    if meta_parts:
        meta_html = (
            '\n        <div class="unit-profile__details">'
            '\n          <div class="unit-profile__details--points">'
            f'\n            {" &nbsp;&middot;&nbsp; ".join(meta_parts)}'
            '\n          </div>'
            '\n        </div>'
        )

    desc_val  = first_field(fields, DESCRIPTION_FIELD_CANDIDATES)
    desc_html = f'\n        <div class="rule-entry__description"><em>{rt_to_html(desc_val)}</em></div>' if desc_val else ""

    body_val  = first_field(fields, NOTES_FIELD_CANDIDATES)
    body_html = rt_to_html(body_val)
    notes_block = (
        '\n        <div class="rule-entry__notes">'
        '\n          <em>Notes:</em>'
        f'\n          {body_html}'
        '\n        </div>'
    ) if body_html else ""

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>'
        f'{render_timestamp(last_upd)}'
        f'\n              <div class="rule-entry magic-item {slug}">'
        f'{meta_html}{desc_html}{notes_block}'
        '\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


def render_special_rule(fields, slug):
    name     = fields.get("name", slug)
    last_upd = fields.get("lastUpdated", "")

    desc_val  = first_field(fields, DESCRIPTION_FIELD_CANDIDATES)
    desc_html = f'\n        <div class="rule-entry__description"><em>{rt_to_html(desc_val)}</em></div>' if desc_val else ""

    body_val  = first_field(fields, NOTES_FIELD_CANDIDATES)
    body_html = rt_to_html(body_val)
    notes_block = (
        '\n        <div class="rule-entry__notes">'
        f'\n          {body_html}'
        '\n        </div>'
    ) if body_html else ""

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>'
        f'{render_timestamp(last_upd)}'
        f'\n              <div class="rule-entry special-rule {slug}">'
        f'{desc_html}{notes_block}'
        '\n              </div>'
    )
    return html_shell(name, body, f"{slug}.html")


#def render_troop_type_detail(fields, slug):
#    name     = fields.get("name", slug)
#    last_upd = fields.get("lastUpdated", "")
#
 #   body_val  = fields.get("body")
  #  body_html = rt_to_html(body_val)
   #    '\n        <div class="rule-entry__notes">'
 #       f'\n          {body_html}'
 #       '\n        </div>'
 #   ) if body_html else ""
#
#    body = (
#        f'              <h1 class="page-title">{esc(name)}</h1>'
#        f'{render_timestamp(last_upd)}'
#        f'\n              <div class="rule-entry troop-types-in-detail {slug}">'
#        f'{notes_block}'
#        '\n              </div>'
#    )
#    return html_shell(name, body, f"{slug}.html")

def render_troop_type_detail(fields, slug):
    name = fields.get('name', '')
    slug = fields.get('slug', '')
    last_upd = fields.get('lastUpdated', '')
    
    # Full rich-text body → renders table + text + hyperlinks
    body_val = fields.get('body')
    body_html = rt_to_html(body_val)  # Key change: full RT, not scalar
    
    # Parent/related links section (e.g., Infantry)
    related_html = ''
    related = fields.get('relatedLinks', [])
    if related:
        links_html = ', '.join(render_detail_link(item, 'troop-types-in-detail') for item in related)
        related_html = f'<div class="section-link"><span class="section-linkheader">Parent</span><span>{links_html}</span></div>'
    
    note_sblock = f'<div class="rule-entrynotes">{body_html}</div>' if body_html else ''
    
    body = f'''
    <h1 class="page-title">{esc(name)}</h1>
    {render_timestamp(last_upd)}
    <div class="rule-entry troop-types-in-detail" data-slug="{slug}">
        {related_html}
        {note_sblock}
    </div>'''
    return html_shell(name, body, f'{slug}.html')


# ---------------------------------------------------------------------------
# Stats editing
# ---------------------------------------------------------------------------

def edit_single_unit(unit_profile, unit_idx):
    selected_unit = unit_profile[unit_idx]
    unit_name     = selected_unit.get("Name", "Unit")

    log(f"  [edit] Editing stats for: {unit_name}")
    changes_made = False

    while True:
        stat_input = input("\nEnter stat to edit (M, WS, BS, S, T, W, I, A, Ld or 'done'): ").strip().upper()
        if stat_input.lower() == 'done':
            break
        if stat_input not in EDITABLE_STATS:
            print(f"  Invalid stat. Choose from: {', '.join(EDITABLE_STATS)}")
            continue

        current_val = selected_unit.get(stat_input, "-")
        print(f"  Current {stat_input} ({STAT_NAMES[stat_input]}): {current_val}")
        new_value   = input("  Enter new value (or press Enter to skip): ").strip()
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
        log(f"  [edit] {unit_name}: {stat_input} {current_val} -> {new_value}")
        changes_made = True

    return changes_made


def edit_unit_stats(fields):
    unit_profile = fields.get("unitProfile", [])
    if not unit_profile:
        log("  [edit] No unit profile found to edit.")
        return fields

    if input("\nWould you like to edit unit stats? (y/n): ").strip().lower() not in ('y', 'yes'):
        log("  [edit] Skipping stat editing.")
        return fields

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
            choice = input(f"Which unit? (1-{len(unit_profile)} or 'done'): ").strip()
            if choice.lower() == 'done':
                unit_idx = None
            else:
                try:
                    unit_idx = int(choice) - 1
                    if not (0 <= unit_idx < len(unit_profile)):
                        print(f"  Please enter a number between 1 and {len(unit_profile)}.")
                        continue
                except ValueError:
                    print("  Invalid input.")
                    continue

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
        for idx in sorted(edited_units):
            unit = unit_profile[idx]
            log(f"  [edit] Final stats for {unit.get('Name', f'Unit {idx+1}')} = "
                + ", ".join(f"{k}:{unit.get(k, '-')}" for k in EDITABLE_STATS))
    else:
        log("  [edit] No stat changes made.")

    return fields


# ---------------------------------------------------------------------------
# Stats extraction and rules-map injection
# ---------------------------------------------------------------------------

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
        log(f"  [rules-map] WARNING: file not found at {rules_map_path} -- skipping")
        return

    with open(rules_map_path, "r", encoding="utf-8") as f:
        content = f.read()

    entry_exists = f'"{display_name}"' in content or f"'{display_name}'" in content

    if entry_exists:
        m = re.search(rf'"{re.escape(display_name)}":\s*\{{[^}}]*\}}', content)
        if m and "stats:" in m.group(0):
            log(f'  [rules-map] "{display_name}" already has stats -- skipping')
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
                    log(f'  [rules-map] Updated "{display_name}" with {len(stats)} stat row(s)')
                else:
                    log(f'  [rules-map] WARNING: could not update "{display_name}"')
        else:
            log(f'  [rules-map] "{display_name}" already exists -- skipping')
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
        log("  [rules-map] WARNING: could not locate additionalOWBRules -- skipping")
        return

    with open(rules_map_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    stat_info = f" with {len(stats)} stat row(s)" if stats and content_type == "unit" else ""
    log(f'  [rules-map] Injected{stat_info} "{display_name}" -> {full_url}')


# ---------------------------------------------------------------------------
# Fetch & save
# ---------------------------------------------------------------------------

def fetch_json(slug, content_type, build_id):
    route = FETCH_ROUTES[content_type]
    url   = f"{BASE_URL}/_next/data/{build_id}/{route}/{slug}.json"
    log(f"  [json] {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def debug_fields(fields):
    lines = ["", "="*60, "DEBUG: raw fields from Contentful JSON", "="*60]
    for key, val in sorted(fields.items()):
        if isinstance(val, dict):
            preview = f"{{nodeType: {val.get('nodeType', '?')} ...}}" if "nodeType" in val else f"dict({list(val.keys())[:4]})"
        elif isinstance(val, list):
            preview = f"list[{len(val)}]"
        elif isinstance(val, str) and len(val) > 80:
            preview = repr(val[:80]) + "..."
        else:
            preview = repr(val)
        lines.append(f"  {key:<28}  {type(val).__name__:<12}  {preview}")
    lines.append("="*60)
    log("\n".join(lines))


def fetch_and_save(slug, content_type, build_id, out_dir, rules_map_path, debug=False):
    log(f"\nFetching: {slug}  (type: {content_type})")
    try:
        data = fetch_json(slug, content_type, build_id)
    except Exception as e:
        die(f"  [error] {e}")

    fields = data.get("pageProps", {}).get("entry", {}).get("fields", {})
    if not fields:
        die("  [error] No 'fields' in JSON response. BUILD_ID may be stale.")

    if debug:
        debug_fields(fields)
        log("  [debug] Exiting without writing HTML (--debug flag set).")
        return

    content_type = _normalise_type(content_type)

    if content_type == "unit":
        fields = edit_unit_stats(fields)
        stats  = extract_stats_from_fields(fields)
        if stats:
            log(f"  [stats] Extracted {len(stats)} stat row(s).")
        else:
            log("  [stats] No stats found.")
        html = render_unit(fields, slug)

    elif content_type == "weapons-of-war":
        stats = None
        html  = render_weapon(fields, slug)
        desc_key  = next((k for k in DESCRIPTION_FIELD_CANDIDATES if fields.get(k)), None)
        notes_key = next((k for k in NOTES_FIELD_CANDIDATES       if fields.get(k)), None)
        log(f"  [meta] Description field: {desc_key or '(none)'}")
        log(f"  [meta] Notes field      : {notes_key or '(none)'}")

    elif content_type == "magic-item":
        stats = None
        html  = render_magic_item(fields, slug)
        desc_key  = next((k for k in DESCRIPTION_FIELD_CANDIDATES if fields.get(k)), None)
        notes_key = next((k for k in NOTES_FIELD_CANDIDATES       if fields.get(k)), None)
        log(f"  [meta] Description field: {desc_key or '(none)'}")
        log(f"  [meta] Notes field      : {notes_key or '(none)'}")

    elif content_type == "special-rule":
        stats = None
        html  = render_special_rule(fields, slug)
        desc_key  = next((k for k in DESCRIPTION_FIELD_CANDIDATES if fields.get(k)), None)
        notes_key = next((k for k in NOTES_FIELD_CANDIDATES       if fields.get(k)), None)
        log(f"  [meta] Description field: {desc_key or '(none)'}")
        log(f"  [meta] Notes field      : {notes_key or '(none)'}")

    elif content_type == "troop-types-in-detail":
        stats = None
        html  = render_troop_type_detail(fields, slug)
        desc_key = next((k for k in DESCRIPTION_FIELD_CANDIDATES if fields.get(k)), None)
        notes_key = "body"
        log(f"  [meta] Description field: {desc_key or '(none)'}")
        log(f"  [meta] Notes field      : {notes_key}")

    else:
        die(f"  [error] Unknown content type: {content_type}")

    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, f"{slug}.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    log(f"  [write] Saved: {dest}  ({len(html):,} bytes)")

    inject_rules_map_entry(slug, content_type, stats, rules_map_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv):
    parser = argparse.ArgumentParser(description="Fetch tow.whfb.app JSON and render static HTML.")
    parser.add_argument("--fetch", required=True, help="slug to fetch, e.g. 'grave-guard'")
    parser.add_argument(
        "--type",
        default="unit",
        choices=list(FETCH_ROUTES.keys()),
        help="content type: unit | weapons-of-war | magic-item | special-rule | troop-types-in-detail"
    )
    parser.add_argument("--out", help="output directory (default based on --type)")
    parser.add_argument("--build", help="override BUILD_ID (auto-detect when omitted)")
    parser.add_argument("--rules-map", default=RULES_MAP_PATH, help="path to rules-map.js")
    parser.add_argument("--debug", action="store_true", help="debug JSON fields and exit (no HTML output)")
    args = parser.parse_args(argv)

    content_type = _normalise_type(args.type)
    if content_type not in FETCH_ROUTES:
        die(f"[error] --type must be one of: {', '.join(FETCH_ROUTES.keys())}")

    out_dir = args.out or DEFAULT_OUT_DIRS.get(content_type)
    if not out_dir:
        die(f"[error] No default output directory for type '{content_type}', please use --out")

    build_id = args.build or detect_build_id()
    fetch_and_save(
        slug=args.fetch,
        content_type=content_type,
        build_id=build_id,
        out_dir=out_dir,
        rules_map_path=args.rules_map,
        debug=args.debug,
    )
    print(f"Done. See log: {log_path()}")


if __name__ == "__main__":
    main(sys.argv[1:])
