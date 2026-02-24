#!/usr/bin/env python3
"""
clean_unit_html.py -- Generate static HTML pages mirroring tow.whfb.app

Usage:
  python3 clean_unit_html.py --fetch <slug> [--type unit|weapons-of-war|magic-items] [--out <dir>]

  --type defaults to 'unit' for backward compatibility.
  --out  defaults to ../rules/<type>/ relative to this script.

Examples:
  python3 clean_unit_html.py --fetch halberd --type weapons-of-war
  python3 clean_unit_html.py --fetch sword-of-sigismund --type magic-items
  python3 clean_unit_html.py --fetch grave-guard
"""

import sys, os, re, json, urllib.request
from html import unescape

BASE_URL   = "https://tow.whfb.app"
BUILD_ID   = "Z8fFjDNe5IyXteSHILQuO"
CSS_BASE   = "/owb/rules"

# Supported content types and their URL segments
CONTENT_TYPES = {
    "unit":           "unit",
    "weapons-of-war": "weapons-of-war",
    "magic-items":    "magic-items",
}

# Default output dirs relative to this script
DEFAULT_OUT_DIRS = {
    "unit":           "../rules/unit",
    "weapons-of-war": "../rules/weapons-of-war",
    "magic-items":    "../rules/magic-items",
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
    "rule":         "/weapons-of-war",
    "magicItem":    "/magic-items",
    "spell":        "/spells",
}

STAT_KEYS = ["Name", "M", "WS", "BS", "S", "T", "W", "I", "A", "Ld"]

STAT_NAMES = {
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


# ── shared HTML shell ─────────────────────────────────────────────────────────

def html_shell(title_text, slug, body_html, canonical_path):
    """
    Wrap body_html in the standard OWB page shell used for all content types.
    canonical_path is the relative .html path used in <link rel=canonical>.
    """
    css_path = f"{CSS_BASE}/_next/static/css"
    disclaimer = (
        f'\n        <footer class="german-comp-disclaimer">\n'
        f'          <p>\n'
        f'            <em>This ruleset has been modified for German Comp use only. '
        f'It is not legal for any other Old World comp, official or otherwise.</em>\n'
        f'          </p>\n'
        f'        </footer>'
    )
    return f'''<!DOCTYPE html>
<html lang="en" class="index-tow">
  <head>
    <meta charSet="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <link rel="apple-touch-icon" sizes="180x180" href="https://tow.whfb.app/icons/tow/apple-touch-icon.png"/>
    <link rel="icon" type="image/png" sizes="32x32" href="/owb/rules/icons/tow/favicon-32x32.png"/>
    <link rel="icon" type="image/png" sizes="16x16" href="/owb/rules/icons/tow/favicon-16x16.png"/>
    <link rel="manifest" href="/owb/rules/icons/tow/site.webmanifest"/>
    <link rel="shortcut icon" href="/owb/rules/icons/tow/favicon.ico"/>
    <meta name="theme-color" content="#ffffff"/>
    <title>{esc(title_text)} | Warhammer: The Old World</title>
    <link rel="canonical" href="{canonical_path}"/>
    <link rel="preload" href="{css_path}/29367497e701a5f5.css" as="style"/>
    <link rel="stylesheet" href="{css_path}/29367497e701a5f5.css" data-n-g=""/>
    <link rel="preload" href="{css_path}/0f8fcb57f7477acb.css" as="style"/>
    <link rel="stylesheet" href="{css_path}/0f8fcb57f7477acb.css" data-n-p=""/>
  </head>
  <body>
    <div id="__next">
      <div data-test-id="cf-ui-workbench" class="css-1kvywv3 default-view tow-index ">
        <div class="css-9szchg">
          <main data-test-id="cf-ui-workbench-content" id="main-content" class="css-17h5a9m main-content">
            <div class="css-flqhol">
              <p class="minimal-source">
                <span>Source: <a href="https://tow.whfb.app" target="_blank">Warhammer: The Old World Online Rules Index</a></span>
              </p>
{body_html}
            </div>{disclaimer}
          </main>
        </div>
      </div>
    </div>
  </body>
</html>
'''


# ── field renderers (unit) ────────────────────────────────────────────────────

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
            lis  += f"\n              <li>\n                <p>{inner}</p>\n              </li>"
        body = f"<ul>{lis}\n            </ul>\n            <p></p>"
    else:
        return ""
    return f'\n          <div class="unit-profile__details--equipment">\n            <strong>Equipment:</strong>{body}\n          </div>'


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
        f'\n          <div class="unit-profile__details--special-rules unit-profile__details--link-list">\n'
        f'            <strong>Special Rules:</strong> {links}\n'
        f'          </div>'
    )


# ── unit page renderer ────────────────────────────────────────────────────────

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

    # stat table
    th = '            <th class="css-9p6xbs" data-test-id="cf-ui-table-cell">'
    header = f'{th}</th>\n' + "".join(f'{th}{k}</th>\n' for k in STAT_KEYS[1:])

    rows = ""
    for row_idx, row in enumerate(fields.get("unitProfile", [])):
        unit_name = row.get("Name", f"Unit {row_idx + 1}")
        rows += f'\n            <!-- Stats for: {unit_name} -->'
        rows += f'\n            <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
        for k in STAT_KEYS:
            val = str(row.get(k)) if row.get(k) is not None else "-"
            stat_name = STAT_NAMES.get(k, k)
            rows += f'\n              <!-- {stat_name}: {val} -->'
            rows += f'\n              <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{esc(val)}</td>'
        rows += '\n            </tr>'

    table = (
        f'\n        <div class="table-wrapper {slug}">'
        f'\n          <table class="generic-table unit-profile-table css-1hz7skb" data-test-id="cf-ui-table" cellPadding="0" cellSpacing="0">'
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
    return html_shell(name, slug, body, f"{slug}.html")


# ── weapons-of-war page renderer ─────────────────────────────────────────────

def render_weapon(fields, slug):
    """
    Render a weapons-of-war page to match the OWB rule popup format.

    The popup iframe (RulesIndex.js) loads tow.whfb.app/<type>/<slug>?minimal=true.
    That page shows:
      - h1.page-title  with the item name
      - div.rule-entry (or similar) wrapping the description rich-text
      - optional sub-sections: Range, Strength, AP, Special Rules etc. as a
        definition-list or table, depending on whether the weapon has profile fields.

    We reproduce that structure using the same CSS classes the live site uses.
    """
    name        = fields.get("name", slug)
    description = fields.get("description") or fields.get("rules") or fields.get("text") or {}
    last_upd    = fields.get("lastUpdated", "")

    # Weapon profile table (Range / Strength / AP / Special)
    profile_rows = ""
    profile_keys = [
        ("range",       "Range"),
        ("strength",    "Strength"),
        ("armourPiercing", "AP"),
        ("specialRules", None),   # handled separately below
    ]

    has_profile = any(fields.get(k) for k, _ in profile_keys if k != "specialRules")

    if has_profile:
        def _pval(k):
            v = fields.get(k)
            if v is None:
                return "-"
            if isinstance(v, dict) and "content" in v:
                return render_rt(v)
            if isinstance(v, list):
                return ", ".join(
                    f'<a href="{entry_url(r)}">{esc(r.get("fields", {}).get("name", ""))}</a>'
                    if isinstance(r, dict) else esc(str(r))
                    for r in v
                )
            return esc(str(v))

        profile_rows = (
            f'\n        <div class="table-wrapper {slug}">'
            f'\n          <table class="generic-table weapon-profile-table css-1hz7skb"'
            f' data-test-id="cf-ui-table" cellPadding="0" cellSpacing="0">'
            f'\n            <thead class="css-1sojo49" data-test-id="cf-ui-table-head">'
            f'\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
            f'\n                <th class="css-9p6xbs" data-test-id="cf-ui-table-cell">Range</th>'
            f'\n                <th class="css-9p6xbs" data-test-id="cf-ui-table-cell">Strength</th>'
            f'\n                <th class="css-9p6xbs" data-test-id="cf-ui-table-cell">AP</th>'
            f'\n              </tr>'
            f'\n            </thead>'
            f'\n            <tbody class="css-0" data-test-id="cf-ui-table-body">'
            f'\n              <tr class="css-1sydf7g" data-test-id="cf-ui-table-row">'
            f'\n                <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{_pval("range")}</td>'
            f'\n                <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{_pval("strength")}</td>'
            f'\n                <td class="css-s8xoeu" data-test-id="cf-ui-table-cell">{_pval("armourPiercing")}</td>'
            f'\n              </tr>'
            f'\n            </tbody>'
            f'\n          </table>'
            f'\n        </div>'
        )

    # Rich-text description / rules body
    desc_html = ""
    if isinstance(description, dict) and "content" in description:
        desc_html = render_rt(description)
    elif isinstance(description, str) and description:
        desc_html = f"<p>{esc(description)}</p>"

    # Special rules links
    sr_html = render_special_rules(fields.get("specialRules"))

    # Last-updated timestamp
    date_html = ""
    if last_upd:
        date_html = (
            f'\n        <div class="breadcrumb__wrapper">'
            f'\n          <ul class="breadcrumb">'
            f'\n            <li class="update-timestamp">Last update: {esc(last_upd)}</li>'
            f'\n          </ul>'
            f'\n        </div>'
        )

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>{date_html}'
        f'\n              <div class="rule-entry weapon-of-war {slug}">'
        f'{profile_rows}'
        f'\n                <div class="rule-entry__body">'
        f'\n                  {desc_html}'
        f'                </div>'
        f'{sr_html}'
        f'\n              </div>'
    )
    return html_shell(name, slug, body, f"{slug}.html")


# ── magic-items page renderer ─────────────────────────────────────────────────

def render_magic_item(fields, slug):
    """
    Render a magic-items page to match the OWB rule popup format.

    Magic items on tow.whfb.app show:
      - h1.page-title
      - item type / points cost metadata
      - rich-text description/rules body

    We use the same rule-entry structure as weapon pages so the popup
    looks identical to any other official rule the app displays.
    """
    name        = fields.get("name", slug)
    description = fields.get("description") or fields.get("rules") or fields.get("text") or {}
    item_type   = fields.get("itemType") or fields.get("type") or ""
    cost        = fields.get("cost") or fields.get("points") or ""
    last_upd    = fields.get("lastUpdated", "")

    # Resolve linked item-type entry to a plain string
    if isinstance(item_type, dict):
        item_type = item_type.get("fields", {}).get("name", "") or ""

    # Metadata row (type + cost)
    meta_parts = []
    if item_type:
        meta_parts.append(f'<span class="magic-item__type">{esc(str(item_type))}</span>')
    if cost:
        meta_parts.append(f'<span class="magic-item__cost">{esc(str(cost))} points</span>')
    meta_html = ""
    if meta_parts:
        meta_html = (
            f'\n                <div class="unit-profile__details">'
            f'\n                  <div class="unit-profile__details--points">'
            f'\n                    {" &nbsp;·&nbsp; ".join(meta_parts)}'
            f'\n                  </div>'
            f'\n                </div>'
        )

    # Rich-text rules body
    desc_html = ""
    if isinstance(description, dict) and "content" in description:
        desc_html = render_rt(description)
    elif isinstance(description, str) and description:
        desc_html = f"<p>{esc(description)}</p>"

    # Special rules links
    sr_html = render_special_rules(fields.get("specialRules"))

    # Last-updated timestamp
    date_html = ""
    if last_upd:
        date_html = (
            f'\n        <div class="breadcrumb__wrapper">'
            f'\n          <ul class="breadcrumb">'
            f'\n            <li class="update-timestamp">Last update: {esc(last_upd)}</li>'
            f'\n          </ul>'
            f'\n        </div>'
        )

    body = (
        f'              <h1 class="page-title">{esc(name)}</h1>{date_html}'
        f'\n              <div class="rule-entry magic-item {slug}">'
        f'{meta_html}'
        f'\n                <div class="rule-entry__body">'
        f'\n                  {desc_html}'
        f'                </div>'
        f'{sr_html}'
        f'\n              </div>'
    )
    return html_shell(name, slug, body, f"{slug}.html")


# ── interactive stat editing (unit only) ──────────────────────────────────────

def edit_single_unit(unit_profile, unit_idx):
    selected_unit = unit_profile[unit_idx]
    unit_name = selected_unit.get("Name", "Unit")

    print(f"\nEditing: {unit_name}")
    print("Enter the stat abbreviation (M, WS, BS, S, T, W, I, A, Ld) and new value.")
    print("Type 'done' when finished.\n")

    changes_made = False

    while True:
        print("\nCurrent values:")
        for key in EDITABLE_STATS:
            val = selected_unit.get(key, "-")
            print(f"  {key}: {val}", end="  ")
        print()

        stat_input = input("\nEnter stat to edit (or 'done'): ").strip().upper()

        if stat_input.lower() == 'done':
            break

        if stat_input not in EDITABLE_STATS:
            print(f"  Invalid stat. Choose from: {', '.join(EDITABLE_STATS)}")
            continue

        current_val = selected_unit.get(stat_input, "-")
        print(f"  Current {stat_input} ({STAT_NAMES[stat_input]}): {current_val}")

        new_value = input(f"  Enter new value (or press Enter to skip): ").strip()

        if not new_value:
            continue

        if new_value != '-':
            try:
                if '.' in new_value:
                    float(new_value)
                else:
                    int(new_value)
            except ValueError:
                print(f"  Invalid value '{new_value}'. Please enter a number or '-'.")
                continue

        selected_unit[stat_input] = new_value if new_value == '-' else (
            int(new_value) if '.' not in new_value else float(new_value)
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

    response = input("\nWould you like to edit unit stats? (y/n): ").strip().lower()
    if response not in ['y', 'yes']:
        print("  Skipping stat editing.")
        return fields

    print("\nCurrent Stats:")
    for idx, row in enumerate(unit_profile):
        unit_name = row.get("Name", f"Unit {idx + 1}")
        print(f"\n  [{idx + 1}] {unit_name}")
        for key in EDITABLE_STATS:
            val = row.get(key, "-")
            stat_name = STAT_NAMES.get(key, key)
            print(f"      {key:3s} ({stat_name:15s}): {val}")

    edited_units = set()
    any_changes  = False

    while True:
        unit_idx = 0
        if len(unit_profile) > 1:
            available_units = [f"{i+1}" for i in range(len(unit_profile))]
            print(f"\nAvailable units: {', '.join(available_units)}")
            if edited_units:
                edited_list = ', '.join([str(i+1) for i in sorted(edited_units)])
                print(f"Already edited: {edited_list}")

            while True:
                try:
                    choice = input(f"\nWhich unit would you like to edit? (1-{len(unit_profile)} or 'done' to finish): ").strip()
                    if choice.lower() == 'done':
                        unit_idx = None
                        break
                    unit_idx = int(choice) - 1
                    if 0 <= unit_idx < len(unit_profile):
                        break
                    else:
                        print(f"  Please enter a number between 1 and {len(unit_profile)}.")
                except ValueError:
                    print("  Invalid input. Please enter a number or 'done'.")

        if unit_idx is None:
            break

        if edit_single_unit(unit_profile, unit_idx):
            edited_units.add(unit_idx)
            any_changes = True

        if len(unit_profile) == 1:
            break

        if len(unit_profile) > 1:
            more = input("\nWould you like to edit another unit? (y/n): ").strip().lower()
            if more not in ['y', 'yes']:
                break

    if any_changes:
        print("\n" + "="*60)
        print("FINAL STATS AFTER EDITING:")
        print("="*60)
        for idx in sorted(edited_units):
            unit = unit_profile[idx]
            unit_name = unit.get("Name", f"Unit {idx + 1}")
            print(f"\n  {unit_name}:")
            for key in EDITABLE_STATS:
                val = unit.get(key, "-")
                print(f"    {key:3s} ({STAT_NAMES[key]:15s}): {val}")
        print()
    else:
        print("\n  No changes made.")

    return fields


# ── stats extraction and formatting ───────────────────────────────────────────

def extract_stats_from_fields(fields):
    unit_profile = fields.get("unitProfile", [])
    if not unit_profile:
        return None
    stats = []
    for row in unit_profile:
        stat_dict = {}
        for key in STAT_KEYS:
            value = row.get(key)
            if value is None or value == "":
                value = "-"
            else:
                value = str(value)
            stat_dict[key] = value
        stats.append(stat_dict)
    return stats if stats else None


def format_stats_for_js(stats):
    if not stats:
        return None
    lines = []
    for stat in stats:
        fields = ", ".join(
            f'{key}: "{stat.get(key, "-")}"' for key in STAT_KEYS
        )
        lines.append(f"      {{ {fields} }}")
    return "[\n" + ",\n".join(lines) + "\n    ]"


# ── rules-map.js injection ────────────────────────────────────────────────────

def slug_to_display_name(slug):
    return slug.replace("-", " ")


def inject_rules_map_entry(slug, content_type, stats, rules_map_path):
    """
    Insert (or update) an entry in the `const additionalOWBRules` object
    inside rules-map.js.

    - For 'unit' entries: fullUrl + optional stats array (existing behaviour).
    - For 'weapons-of-war' / 'magic-items': fullUrl only (no stat table).
    """
    display_name = slug_to_display_name(slug)
    full_url = f"{OWB_RULES_BASE}/{content_type}/{slug}.html?minimal=true"

    if not os.path.isabs(rules_map_path):
        rules_map_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), rules_map_path
        )

    if not os.path.exists(rules_map_path):
        print(f"  [rules-map] WARNING: file not found at {rules_map_path} — skipping injection")
        return

    with open(rules_map_path, "r", encoding="utf-8") as f:
        content = f.read()

    entry_exists = f'"{display_name}"' in content or f"'{display_name}'" in content

    if entry_exists:
        entry_pattern = rf'"{re.escape(display_name)}":\s*\{{[^}}]*\}}'
        match = re.search(entry_pattern, content)
        if match and "stats:" in match.group(0):
            print(f'  [rules-map] Entry for "{display_name}" already has stats — skipping')
            return

        if stats and content_type == "unit":
            stats_js = format_stats_for_js(stats)
            if stats_js:
                pattern = rf'("{re.escape(display_name)}":\s*\{{\s*fullUrl:[^,]+)(,?\s*\}})'
                replacement = rf'\1,\n    stats: {stats_js}\2'
                new_content, count = re.subn(pattern, replacement, content, count=1)
                if count > 0:
                    with open(rules_map_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    print(f'  [rules-map] Updated entry with {len(stats)} stat line(s) for "{display_name}"')
                else:
                    print(f'  [rules-map] WARNING: Could not update entry for "{display_name}"')
        else:
            print(f'  [rules-map] Entry for "{display_name}" already exists — skipping')
    else:
        if stats and content_type == "unit":
            stats_js = format_stats_for_js(stats)
            new_entry = (
                f'  "{display_name}": {{\n'
                f'    fullUrl: "{full_url}",\n'
                f'    stats: {stats_js}\n'
                f'  }}'
            )
        else:
            new_entry = f'  "{display_name}": {{ fullUrl: "{full_url}" }}'

        pattern = r'(const additionalOWBRules\s*=\s*\{\n)'
        replacement = r'\1' + new_entry + ',\n'
        new_content, n = re.subn(pattern, replacement, content, count=1)

        if n == 0:
            print("  [rules-map] WARNING: could not locate `const additionalOWBRules = {` — skipping injection")
            return

        with open(rules_map_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        stat_info = f" with {len(stats)} stat line(s)" if stats and content_type == "unit" else ""
        print(f'  [rules-map] Injected new entry{stat_info} for "{display_name}" → {full_url}')


# ── fetch & save ──────────────────────────────────────────────────────────────

def fetch_json(slug, content_type):
    """
    Fetch the Next.js JSON for any supported content type.
    URL pattern: <BASE_URL>/_next/data/<BUILD_ID>/<type>/<slug>.json
    """
    url = f"{BASE_URL}/_next/data/{BUILD_ID}/{content_type}/{slug}.json"
    print(f"  [json] {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def fetch_and_save(slug, content_type, out_dir, rules_map_path):
    print(f"\nFetching: {slug}  (type: {content_type})")
    try:
        data = fetch_json(slug, content_type)
    except Exception as e:
        sys.exit(f"  [error] {e}")

    fields = data.get("pageProps", {}).get("entry", {}).get("fields", {})
    if not fields:
        sys.exit("  [error] No fields in JSON response")

    if content_type == "unit":
        # Interactive stat editing for units
        fields = edit_unit_stats(fields)

        stats = extract_stats_from_fields(fields)
        if stats:
            print(f"\n  Extracted {len(stats)} stat line(s):")
            for stat in stats:
                print(f"    - {stat.get('Name', 'Unknown')}")
        else:
            print("  No stats found in source data")

        html = render_unit(fields, slug)

    elif content_type == "weapons-of-war":
        stats = None
        html  = render_weapon(fields, slug)

    elif content_type == "magic-items":
        stats = None
        html  = render_magic_item(fields, slug)

    else:
        sys.exit(f"  [error] Unknown content type: {content_type}")

    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, f"{slug}.html")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  Saved HTML: {dest}  ({len(html):,} bytes)")

    inject_rules_map_entry(slug, content_type, stats, rules_map_path)


def main():
    args = sys.argv[1:]

    if "--fetch" not in args:
        print(__doc__)
        sys.exit(1)

    i_fetch = args.index("--fetch")
    if i_fetch + 1 >= len(args):
        print(__doc__)
        sys.exit(1)
    slug = args[i_fetch + 1]

    # --type  (default: unit)
    content_type = "unit"
    if "--type" in args:
        i_type = args.index("--type")
        if i_type + 1 < len(args):
            content_type = args[i_type + 1]
    if content_type not in CONTENT_TYPES:
        sys.exit(f"  [error] --type must be one of: {', '.join(CONTENT_TYPES)}")

    # --out  (default: per-type directory)
    out_dir = DEFAULT_OUT_DIRS[content_type]
    if "--out" in args:
        i_out = args.index("--out")
        if i_out + 1 < len(args):
            out_dir = args[i_out + 1]
    # Resolve relative paths against this script's directory
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), out_dir)

    # --rules-map
    rules_map_path = RULES_MAP_PATH
    if "--rules-map" in args:
        i_rm = args.index("--rules-map")
        if i_rm + 1 < len(args):
            rules_map_path = args[i_rm + 1]

    fetch_and_save(slug, content_type, out_dir, rules_map_path)
    print("\nDone.")


if __name__ == "__main__":
    main()
