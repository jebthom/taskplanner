#!/usr/bin/env python3
"""Build static site from milestones.py into public/."""

import os
import shutil
from datetime import datetime
from milestones import milestones

YEAR = 2026  # default year for parsing dates

# Consistent color palette for projects
COLORS = [
    "#2563eb",  # blue
    "#dc2626",  # red
    "#16a34a",  # green
    "#9333ea",  # purple
    "#ea580c",  # orange
    "#0891b2",  # cyan
    "#be185d",  # pink
    "#854d0e",  # amber
]

def parse_date(s):
    """Parse colloquial date strings like 'Jun 14' or 'June 14'."""
    import calendar
    parts = s.strip().split()
    if len(parts) == 2:
        month_str, day_str = parts
        day = int(day_str)
        for i in range(1, 13):
            full = calendar.month_name[i].lower()
            abbr = calendar.month_abbr[i].lower()
            if month_str.lower() == full or month_str.lower() == abbr:
                return datetime(YEAR, i, day)
    raise ValueError(f"Cannot parse date: {s!r}")


def format_date(dt):
    """Format a datetime as 'Jun 14'."""
    return dt.strftime("%b %-d") if os.name != "nt" else dt.strftime("%b %d").replace(" 0", " ")


def slug(name):
    return name.lower().replace(" ", "-")


def assign_colors(projects):
    return {name: COLORS[i % len(COLORS)] for i, name in enumerate(projects)}


def hex_to_rgba(hex_color, alpha):
    """Convert '#rrggbb' to 'rgba(r,g,b,a)'."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def render_row(date_str, entry_type, description, complete, color):
    style_parts = [f"border-left: 4px solid {color}", f"background: {hex_to_rgba(color, 0.06)}"]
    classes = []
    if complete:
        classes.append("complete")

    tag_open = "<em>" if entry_type == "A" else "<strong>"
    tag_close = "</em>" if entry_type == "A" else "</strong>"

    cls = f' class="{" ".join(classes)}"' if classes else ""
    style = f' style="{"; ".join(style_parts)}"'

    type_label = "Activity" if entry_type == "A" else "Deliverable"
    badge_cls = "badge-activity" if entry_type == "A" else "badge-deliverable"

    return (
        f'<tr{cls}{style}>'
        f'<td class="date-col">{date_str}</td>'
        f'<td class="desc-col">{tag_open}{description}{tag_close}</td>'
        f'<td class="type-col"><span class="badge {badge_cls}">{type_label}</span></td>'
        f'</tr>\n'
    )


def build_nav(project_names, color_map, active=None):
    links = []
    cls = "active" if active is None else ""
    links.append(f'<a href="index.html" class="nav-link {cls}">All Projects</a>')
    for name in project_names:
        cls = "active" if active == name else ""
        dot = f'<span class="dot" style="background:{color_map[name]}"></span>'
        links.append(f'<a href="{slug(name)}.html" class="nav-link {cls}">{dot}{name}</a>')
    return "\n".join(links)


CSS = """\
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       background: #f8fafc; color: #1e293b; line-height: 1.6; }
header { background: #0f172a; color: #f8fafc; padding: 1rem 2rem; }
header h1 { font-size: 1.25rem; font-weight: 600; }
nav { display: flex; gap: 0.5rem; flex-wrap: wrap; padding: 0.75rem 2rem;
      background: #1e293b; }
.nav-link { color: #94a3b8; text-decoration: none; padding: 0.4rem 0.8rem;
            border-radius: 6px; font-size: 0.9rem; display: flex; align-items: center; gap: 0.4rem; }
.nav-link:hover { background: #334155; color: #f1f5f9; }
.nav-link.active { background: #334155; color: #f1f5f9; font-weight: 600; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
main { max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
h2 { margin-bottom: 1rem; font-size: 1.4rem; }
table { width: 100%; border-collapse: collapse; background: #fff;
        border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
th { background: #f1f5f9; text-align: left; padding: 0.75rem 1rem;
     font-size: 0.8rem; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; }
td { padding: 0.75rem 1rem; border-top: 1px solid #e2e8f0; }
tr { transition: background 0.15s; }
tr:hover { background: #f8fafc; }
tr.complete td { color: #94a3b8; text-decoration: line-through; }
.date-col { white-space: nowrap; width: 100px; font-weight: 500; }
.type-col { width: 100px; text-align: right; }
.badge { font-size: 0.7rem; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600;
         text-transform: uppercase; letter-spacing: 0.03em; }
.badge-activity { background: #dbeafe; color: #1d4ed8; }
.badge-deliverable { background: #fef3c7; color: #92400e; }
footer { text-align: center; padding: 2rem; color: #94a3b8; font-size: 0.8rem; }
"""


def page(title, nav_html, body_html):
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{CSS}</style>
</head>
<body>
<header><h1>Project Milestones</h1></header>
<nav>{nav_html}</nav>
<main>
{body_html}
</main>
<footer>Last built {datetime.now().strftime("%Y-%m-%d %H:%M")}</footer>
</body>
</html>
"""


def build_table(rows_data, color_map):
    """rows_data: list of (datetime, project, date_str, type, desc, complete)"""
    rows_html = ""
    for dt, project, date_str, etype, desc, complete in rows_data:
        rows_html += render_row(date_str, etype, desc, complete, color_map[project])
    return (
        '<table>\n<thead><tr><th>Date</th><th>Description</th><th>Type</th></tr></thead>\n'
        f'<tbody>\n{rows_html}</tbody>\n</table>\n'
    )


def main():
    out = "public"
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)

    project_names = list(milestones.keys())
    color_map = assign_colors(project_names)

    # Collect all rows with parsed dates
    all_rows = []
    per_project = {name: [] for name in project_names}

    for project, items in milestones.items():
        for date_str, etype, desc, complete in items:
            dt = parse_date(date_str)
            formatted = format_date(dt)
            row = (dt, project, formatted, etype, desc, complete)
            all_rows.append(row)
            per_project[project].append(row)

    all_rows.sort(key=lambda r: r[0])
    for name in per_project:
        per_project[name].sort(key=lambda r: r[0])

    # Overall page
    nav = build_nav(project_names, color_map, active=None)
    legend = " &nbsp; ".join(
        f'<span class="dot" style="background:{color_map[n]}"></span> {n}'
        for n in project_names
    )
    body = f"<h2>All Projects</h2>\n<p style='margin-bottom:1rem'>{legend}</p>\n"
    body += build_table(all_rows, color_map)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(page("Milestones — All Projects", nav, body))

    # Per-project pages
    for name in project_names:
        nav = build_nav(project_names, color_map, active=name)
        body = f"<h2>{name}</h2>\n"
        body += build_table(per_project[name], color_map)
        with open(os.path.join(out, f"{slug(name)}.html"), "w") as f:
            f.write(page(f"Milestones — {name}", nav, body))

    print(f"Built {len(project_names) + 1} pages in {out}/")


if __name__ == "__main__":
    main()
