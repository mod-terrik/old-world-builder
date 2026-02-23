#!/usr/bin/env python3
"""
clean_unit_html.py -- Generate static HTML unit pages mirroring tow.whfb.app

Usage:
  python3 clean_unit_html.py --fetch <unit-slug> [--out <dir>]
"""

import sys, os, re, json, urllib.request

BASE_URL   = "https://tow.whfb.app"
BUILD_ID   = "Z8fFjDNe5IyXteSHILQuO"
OUTPUT_DIR = "../rules/unit"
CSS_BASE   = "/owb/rules"

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
    "rule":         "/weapons-of-war",
    "magicItem":    "/magic-items",
    "spell":        "/spells",
}

STAT_KEYS = ["Name", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld"]

DISCLAIMER = (
    '<footer class="german-comp-disclaimer">'
    '<p><em>This ruleset has been modified for German Comp use only. '
    'It is not legal for any other Old World comp, official or otherwise.</em></p>'
    '</footer>'
)

HEAD = (
    '<!DOCTYPE html><html lang="en" class="index-tow"><head>'
    '<meta charSet="utf-8"/>'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0"/>'
    '<link rel="apple-touch-icon" sizes="180x180" href="https://tow.whfb.app/icons/tow/apple-touch-icon.png"/>'
    '<link rel="icon" type="image/png" sizes="32x32" href="/owb/rules/icons/tow/favicon-32x32.png"/>'
    '<link rel="icon" type="image/png" sizes="16x16" href="/owb/rules/icons/tow/favicon-16x16.png"/>'
    '<link rel="manifest" href="/owb/rules/icons/tow/site.webmanifest"/>'
    '<link rel="shortcut icon" href="/owb/rules/icons/tow/favicon.ico"/>'
    '<meta name="theme-color" content="#ffffff"/>'
    '<title>{title} | Warhammer: The Old World</title>'
    '<link rel="canonical" href="{slug}.html"/>'
    '<link rel="preload" href="{css}/29367497e701a5f5.css" as="style"/>'
    '<link rel="stylesheet" href="{css}/29367497e701a5f5.css" data-n-g=""/>'
    '<link rel="preload" href="{css}/0f8fcb57f7477acb.css" as="style"/>'
    '<link rel="stylesheet" href="{css}/0f8fcb57f7477acb.css" data-n-p=""/>'
    '</head>'
)


# ── helpers ───────────────────────────────────────────────────────────────────

def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def entry_url(target, context="auto"):
    slug = target.get("fields", {}).get("slug", "") if isinstance(target, dict) else ""
    if context == "equipment":
        path = "/weapons-of-war"
    elif context == "rules":
        path = "/special-rules"
    else:
        ct   = target.get("sys", {}).get("contentType", {}).get("sys", {}).get("id", "")
        path = CONTENT_TYPE_PATHS.get(ct, f"/{ct}")
    return f"{BASE_URL}{path}/{slug}"


def render_rt(node, ctx="auto"):
    """Recursively render a Contentful rich-text node to HTML."""
    if not isinstance(node, dict):
        return esc(str(node))
    nt, content = node.get("nodeType", ""), node.get("content", [])
    inner = lambda: "".join(render_rt(c, ctx) for c in content)

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
        return f'<a href="{entry_url(node["data"]["target"], ctx)}">{inner()}</a>'
    elif nt == "paragraph":
        return f"<p>{inner()}</p>"
    elif nt == "unordered-list":
        return "<ul>" + "".join(f"<li>{render_rt(i, ctx)}</li>" for i in content) + "</ul>"
    elif nt == "ordered-list":
        return "<ol>" + "".join(f"<li>{render_rt(i, ctx)}</li>" for i in content) + "</ol>"
    else:
        return inner()


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


# ── field renderers ───────────────────────────────────────────────────────────

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
            if not isinstance(item, dict): continue
            f     = item.get("fields", {})
            link  = f'<a href="{BASE_URL}/weapons-of-war/{f.get("slug", "")}">{esc(f.get("name", ""))}</a>'
            group = f.get("groupName", "")
            note  = f.get("note", "")
            inner = f"<b>{esc(group)}:</b> {esc(note)} {link}" if group else link
            lis  += f"<li><p>{inner}</p></li>"
        body = f"<ul>{lis}</ul>"
    else:
        return ""
    return f'<div class="unit-profile__details--equipment"><strong>Equipment:</strong>{body}</div>'


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
                if f.get("note"): label += f' ({esc(f["note"])})'
                pairs.append((f'{BASE_URL}/special-rules/{f.get("slug", "")}', label))
    if not pairs:
        return ""
    links = ", ".join(f'<a href="{h}">{l}</a>' for h, l in pairs)
    return (
        f'<div class="unit-profile__details--special-rules unit-profile__details--link-list">'
        f'<strong>Special Rules:</strong> {links}</div>'
    )


# ── page render ───────────────────────────────────────────────────────────────

def render(fields, slug):
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

    # stat table
    th = '<th class="css-9p6xbs" data-test-id="cf-ui-table-cell">'
    header = f'{th}</th>' + "".join(f'{th}{k}</th>' for k in STAT_KEYS[1:])
    rows = ""
    for row in fields.get("unitProfile", []):
        cells = "".join(
            f'<td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{esc(str(row.get(k))) if row.get(k) is not None else "-"}</td>'
            for k in STAT_KEYS
        )
        rows += f'<tr class="css-1sydf7g" data-test-id="cf-ui-table-row">{cells}</tr>'

    table = (
        f'<div class="table-wrapper {slug}">'
        f'<table class="generic-table unit-profile-table css-1hz7skb" data-test-id="cf-ui-table" cellPadding="0" cellSpacing="0">'
        f'<thead class="css-1sojo49" data-test-id="cf-ui-table-head"><tr class="css-1sydf7g" data-test-id="cf-ui-table-row">{header}</tr></thead>'
        f'<tbody class="css-0" data-test-id="cf-ui-table-body">{rows}</tbody>'
        f'</table></div>'
    )

    # details block
    def detail(css, label, val):
        return f'<div class="unit-profile__details--{css}"><strong>{label}:</strong> {val}</div>'

    details = (
        f'<div class="unit-profile__details">'
        + detail("points",        "Cost",          f"{esc(str(cost))} points per model")
        + detail("unit-category", "Unit Category", render_detail_link(fields.get("unitCategory"), "/troop-types-in-detail"))
        + detail("troop-type",    "Troop Type",    render_detail_link(fields.get("troopType"),    "/troop-types-in-detail"))
        + detail("base-size",     "Base Size",     esc(str(base_size)))
        + detail("unit-size",     "Unit Size",     esc(str(unit_size)))
        + (detail("armour-value", "Armour Value",  esc(str(armour))) if armour else "")
        + render_equipment(fields.get("equipment"))
        + render_special_rules(fields.get("specialRules"))
        + '</div>'
    )

    # breadcrumb (only when army data present)
    breadcrumb = ""
    if army_slug:
        date_li    = f'<li class="update-timestamp">Last update: {esc(last_upd)}</li>' if last_upd else ""
        breadcrumb = (
            f'<div class="breadcrumb__wrapper">'
            f'<ul class="breadcrumb"><li class="breadcrumb-link"><a href="{BASE_URL}/army/{army_slug}">{esc(army_name)}</a></li></ul>'
            f'<ul class="breadcrumb">{date_li}</ul>'
            f'</div>'
        )

    css_path = f"{CSS_BASE}/_next/static/css"
    head = HEAD.format(title=esc(name), slug=slug, css=css_path)

    return (
        head
        + '<body><div id="__next">'
        + '<div data-test-id="cf-ui-workbench" class="css-1kvywv3 default-view tow-index ">'
        + '<div class="css-9szchg">'
        + '<main data-test-id="cf-ui-workbench-content" id="main-content" class="css-17h5a9m main-content">'
        + '<div class="css-flqhol">'
        + '<p class="minimal-source"><span>Source: <a href="https://tow.whfb.app" target="_blank">Warhammer: The Old World Online Rules Index</a></span></p>'
        + f'<h1 class="page-title">{esc(name)}</h1>'
        + breadcrumb
        + f'<div class="unit-profile {slug}">{table}{details}</div>'
        + '</div>'
        + DISCLAIMER
        + '</main></div></div></div></body></html>\n'
    )


# ── rules-map.js injection ────────────────────────────────────────────────────

def slug_to_display_name(slug):
    """Convert a hyphenated slug to a space-separated display name."""
    return slug.replace("-", " ")


def inject_rules_map_entry(slug, rules_map_path):
    """
    Insert a new fullUrl entry for `slug` at the top of the
    `const additionalOWBRules` object in rules-map.js.

    Skips insertion if the slug is already present.
    """
    display_name = slug_to_display_name(slug)
    full_url = f"https://owapps.grra.me/owb/rules/unit/{slug}.html?minimal=true"
    new_entry = f'  "{display_name}": {{ fullUrl: "{full_url}" }},'

    # Resolve the path relative to this script when the default is used
    if not os.path.isabs(rules_map_path):
        rules_map_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), rules_map_path
        )

    if not os.path.exists(rules_map_path):
        print(f"  [rules-map] WARNING: file not found at {rules_map_path} — skipping injection")
        return

    with open(rules_map_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Guard: skip if an entry for this slug already exists
    if f'"{display_name}"' in content or f"'{display_name}'" in content:
        print(f"  [rules-map] Entry for \"{display_name}\" already exists — skipping")
        return

    # Find the opening brace of `const additionalOWBRules = {` and insert
    # the new entry immediately after it on the very next line, with no
    # blank line between the brace and the new entry.
    pattern = r'(const additionalOWBRules\s*=\s*\{\n)'
    replacement = r'\1' + new_entry + '\n'
    new_content, n = re.subn(pattern, replacement, content, count=1)

    if n == 0:
        print("  [rules-map] WARNING: could not locate `const additionalOWBRules = {` — skipping injection")
        return

    with open(rules_map_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  [rules-map] Injected entry: \"{display_name}\" → {full_url}")


# ── fetch & save ──────────────────────────────────────────────────────────────

def fetch_json(slug):
    url = f"{BASE_URL}/_next/data/{BUILD_ID}/unit/{slug}.json"
    print(f"  [json] {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def fetch_unit(slug, out_dir, rules_map_path):
    print(f"\nFetching: {slug}")
    try:
        data = fetch_json(slug)
    except Exception as e:
        sys.exit(f"  [error] {e}")
    fields = data.get("pageProps", {}).get("entry", {}).get("fields", {})
    if not fields:
        sys.exit("  [error] No fields in JSON response")
    html = render(fields, slug)
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, f"{slug}.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Saved: {dest}  ({len(html):,} bytes)")

    # Inject the new entry into rules-map.js
    inject_rules_map_entry(slug, rules_map_path)


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--fetch":
        print(__doc__)
        sys.exit(1)
    slug    = sys.argv[2]
    out_dir = OUTPUT_DIR
    if "--out" in sys.argv:
        i = sys.argv.index("--out")
        if i + 1 < len(sys.argv):
            out_dir = sys.argv[i + 1]
    rules_map_path = RULES_MAP_PATH
    if "--rules-map" in sys.argv:
        i = sys.argv.index("--rules-map")
        if i + 1 < len(sys.argv):
            rules_map_path = sys.argv[i + 1]
    fetch_unit(slug, out_dir, rules_map_path)
    print("\nDone.")


if __name__ == "__main__":
    main()
