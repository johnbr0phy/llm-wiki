#!/usr/bin/env python3
"""Build a single-file HTML wiki from markdown source."""

import os
import re
import json
import html as html_module
from dataclasses import dataclass, field
from pathlib import Path

import markdown

WIKI_DIR = Path(__file__).parent / "wiki"
OUTPUT_FILE = Path(__file__).parent / "wiki-site.html"
SECTIONS = ["projects", "people", "decisions", "concepts", "timeline"]
SKIP_FILES = {"INDEX.md", "log.md"}

# Section display names and sort order
SECTION_LABELS = {
    "projects": "Projects",
    "people": "People",
    "decisions": "Decisions",
    "concepts": "Concepts",
    "timeline": "Timeline",
}

# People sub-groups (parsed from people/INDEX.md headers)
PEOPLE_GROUPS = {
    "Leadership & Product": [],
    "Design": [],
    "Engineering": [],
    "GTM & Customer Success": [],
    "External Partners": [],
}

# --- Privacy Filter ---
# Add exact quoted strings to strip from the output.
# Example: quotes from private 1:1 conversations that shouldn't be shared.
PRIVATE_QUOTES = [
    # '"Exact quote to strip"',
]

# Patterns that indicate private attribution (e.g., 1:1 meeting quotes)
PRIVATE_ATTRIBUTION_PATTERNS = [
    # r"Person Name's framing",
    # r"Person Name said",
]


@dataclass
class Article:
    id: str
    section: str
    source_path: str
    title: str = ""
    metadata: dict = field(default_factory=dict)
    tldr: str = ""
    raw_body: str = ""
    html_body: str = ""
    search_text: str = ""
    people_group: str = ""


# --- Stage 1: Discover ---
def discover_articles():
    articles = []
    for section in SECTIONS:
        section_dir = WIKI_DIR / section
        if not section_dir.exists():
            continue
        for md_file in sorted(section_dir.glob("*.md")):
            if md_file.name in SKIP_FILES:
                continue
            article_id = md_file.stem
            articles.append(Article(
                id=article_id,
                section=section,
                source_path=str(md_file),
            ))
    return articles


# --- Stage 2: Parse ---
def parse_article(article):
    text = Path(article.source_path).read_text(encoding="utf-8")
    lines = text.split("\n")

    # Title from first H1
    for line in lines:
        if line.startswith("# "):
            article.title = line[2:].strip()
            break

    # Parse metadata and TLDR
    meta = {}
    body_start = 0
    found_tldr = False

    for i, line in enumerate(lines):
        if line.startswith("# "):
            continue
        m = re.match(r'^\*\*([^*]+):\*\*\s*(.*)', line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip()
            if key == "TLDR":
                article.tldr = val
                found_tldr = True
            else:
                meta[key] = val
        elif found_tldr or line.startswith("## "):
            body_start = i
            break

    article.metadata = meta
    article.raw_body = "\n".join(lines[body_start:])
    return article


# --- Stage 3: Privacy filter ---
def apply_privacy_filter(text):
    # Remove exact private quotes (try both straight and smart quotes)
    for quote in PRIVATE_QUOTES:
        text = text.replace(quote, "[private]")
        smart = quote.replace('"', '\u201c', 1).replace('"', '\u201d', 1)
        text = text.replace(smart, "[private]")

    # Clean up lines that now have dangling attribution + [private]
    for pattern in PRIVATE_ATTRIBUTION_PATTERNS:
        text = re.sub(
            pattern + r'[^.]*\[private\][^.]*\.',
            '',
            text
        )

    # Remove any remaining [private] markers
    text = text.replace("[private]", "")

    # Clean up double spaces and empty lines left behind
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


# --- Stage 4: Markdown to HTML ---
def md_to_html(text):
    md = markdown.Markdown(extensions=['tables', 'fenced_code'])
    return md.convert(text)


# --- Stage 5: Resolve backlinks ---
def build_article_lookup(articles):
    lookup = {}
    for a in articles:
        lookup[a.id] = a
        # For decisions, also register without date prefix
        if a.section == "decisions" and re.match(r'\d{4}-\d{2}-\d{2}_', a.id):
            short = re.sub(r'^\d{4}-\d{2}-\d{2}_', '', a.id)
            if short not in lookup:
                lookup[short] = a
    return lookup


def resolve_backlinks(html_text, lookup):
    def replace_backlink(match):
        slug = match.group(1)
        if slug in lookup:
            a = lookup[slug]
            return f'<a href="#{a.id}" onclick="navigateTo(\'{a.id}\'); return false;" class="wiki-link">{a.title}</a>'
        else:
            display = slug.replace("-", " ").title()
            return f'<span class="dead-link">{display}</span>'

    return re.sub(r'\[\[([^\]]+)\]\]', replace_backlink, html_text)


def neutralize_raw_links(html_text):
    """Convert ../../raw/ links to non-clickable source citations."""
    def replace_raw_link(match):
        text = match.group(1)
        return f'<em class="source-ref">{text}</em>'

    return re.sub(r'<a href="[^"]*\.\./\.\./raw/[^"]*">([^<]*)</a>', replace_raw_link, html_text)


# --- Stage 6: Search index ---
def build_search_index(articles):
    index = []
    for a in articles:
        plain = re.sub(r'<[^>]+>', '', a.html_body)
        plain = re.sub(r'\s+', ' ', plain)[:300]
        index.append({
            "id": a.id,
            "title": a.title,
            "section": a.section,
            "tldr": a.tldr,
            "text": plain,
        })
    return index


# --- Stage 7: Parse people groups ---
def assign_people_groups(articles):
    index_path = WIKI_DIR / "people" / "INDEX.md"
    if not index_path.exists():
        return

    text = index_path.read_text(encoding="utf-8")
    current_group = ""
    slug_to_group = {}

    for line in text.split("\n"):
        if line.startswith("## "):
            current_group = line[3:].strip()
        m = re.search(r'\[([^\]]+)\]\(([^)]+)\.md\)', line)
        if m and current_group:
            slug = m.group(2)
            slug_to_group[slug] = current_group

    for a in articles:
        if a.section == "people":
            a.people_group = slug_to_group.get(a.id, "Other")


# --- Stage 8: Assemble HTML ---
def build_sidebar_html(articles):
    sections = {}
    for a in articles:
        if a.section not in sections:
            sections[a.section] = []
        sections[a.section].append(a)

    # Sort within sections
    for s in sections:
        if s == "decisions":
            sections[s].sort(key=lambda a: a.id, reverse=True)
        elif s == "timeline":
            sections[s].sort(key=lambda a: a.id, reverse=True)
        else:
            sections[s].sort(key=lambda a: a.title.lower())

    html_parts = []
    for section in SECTIONS:
        if section not in sections:
            continue
        label = SECTION_LABELS[section]
        count = len(sections[section])

        if section == "people":
            # Group people by role
            groups = {}
            for a in sections[section]:
                g = a.people_group or "Other"
                if g not in groups:
                    groups[g] = []
                groups[g].append(a)

            items = []
            group_order = ["Leadership & Product", "Design", "Engineering",
                          "GTM & Customer Success", "External Partners", "Other"]
            for g in group_order:
                if g not in groups:
                    continue
                items.append(f'<li class="group-header">{g}</li>')
                for a in groups[g]:
                    items.append(
                        f'<li><a href="#{a.id}" data-article="{a.id}" '
                        f'onclick="navigateTo(\'{a.id}\'); return false;">{a.title}</a></li>'
                    )
            items_html = "\n".join(items)
        else:
            items_html = "\n".join(
                f'<li><a href="#{a.id}" data-article="{a.id}" '
                f'onclick="navigateTo(\'{a.id}\'); return false;">{a.title}</a></li>'
                for a in sections[section]
            )

        html_parts.append(f'''
        <div class="nav-section" data-section="{section}">
          <button class="section-toggle" onclick="toggleSection(this)">
            {label} <span class="count">{count}</span>
            <span class="chevron">&#9660;</span>
          </button>
          <ul class="section-list">
            {items_html}
          </ul>
        </div>''')

    return "\n".join(html_parts)


def build_articles_json(articles):
    data = {}
    for a in articles:
        meta_html = ""
        for key, val in a.metadata.items():
            meta_html += f"<dt>{html_module.escape(key)}</dt><dd>{val}</dd>"

        data[a.id] = {
            "title": a.title,
            "section": a.section,
            "tldr": a.tldr,
            "metadata": meta_html,
            "html": a.html_body,
        }
    return json.dumps(data, ensure_ascii=False)


def build_html(articles, search_index, sidebar_html):
    articles_json = build_articles_json(articles)
    search_json = json.dumps(search_index, ensure_ascii=False)

    total = len(articles)
    section_counts = {}
    for a in articles:
        section_counts[a.section] = section_counts.get(a.section, 0) + 1

    welcome_stats = " &middot; ".join(
        f"{SECTION_LABELS[s]} ({section_counts.get(s, 0)})" for s in SECTIONS
    )

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wiki</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: system-ui, -apple-system, sans-serif;
  background: #fafaf5;
  color: #1a1a1a;
}}

#app {{ display: flex; min-height: 100vh; }}

/* Sidebar */
#sidebar {{
  width: 300px;
  flex-shrink: 0;
  border-right: 1px solid #d4d4d4;
  background: #f0f0ea;
  overflow-y: auto;
  position: sticky;
  top: 0;
  height: 100vh;
}}

.sidebar-header {{
  padding: 20px 16px 12px;
  border-bottom: 1px solid #d4d4d4;
}}

.site-title {{
  font-size: 22px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 4px;
}}

.site-subtitle {{
  font-size: 12px;
  color: #888;
  margin-bottom: 12px;
}}

#search-input {{
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  outline: none;
}}

#search-input:focus {{ border-color: #0645ad; }}

#search-results {{
  display: none;
  max-height: 400px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #ccc;
  border-top: none;
  border-radius: 0 0 6px 6px;
}}

.search-result {{
  padding: 8px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}}

.search-result:hover {{ background: #f5f5f0; }}
.search-result .result-title {{ font-weight: 600; font-size: 14px; }}
.search-result .result-section {{ font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }}
.search-result .result-tldr {{ font-size: 12px; color: #666; margin-top: 2px; }}
mark {{ background: #fff3a8; padding: 0 1px; }}

/* Navigation */
.sidebar-nav {{ padding: 8px 0; }}

.section-toggle {{
  width: 100%;
  text-align: left;
  background: none;
  border: none;
  padding: 10px 16px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  color: #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
}}

.section-toggle:hover {{ background: #e8e8e0; }}
.section-toggle .count {{ font-weight: 400; color: #888; font-size: 12px; margin-left: 6px; }}
.section-toggle .chevron {{ font-size: 10px; color: #888; transition: transform 0.2s; }}
.section-toggle.open .chevron {{ transform: rotate(180deg); }}

.section-list {{ list-style: none; display: none; padding-bottom: 4px; }}
.section-list.expanded {{ display: block; }}

.section-list li a {{
  display: block;
  padding: 4px 16px 4px 28px;
  font-size: 13px;
  color: #444;
  text-decoration: none;
  line-height: 1.5;
}}

.section-list li a:hover {{ background: #e8e8e0; }}
.section-list li a.active {{ background: #ddd; font-weight: 600; }}

.group-header {{
  padding: 8px 16px 2px 20px;
  font-size: 11px;
  font-weight: 700;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

/* Main content */
#content {{
  flex: 1;
  padding: 2rem 3rem;
  max-width: 960px;
  overflow-y: auto;
}}

/* Welcome page */
.welcome {{ text-align: center; padding-top: 15vh; }}
.welcome h1 {{ font-size: 3rem; font-weight: 700; margin-bottom: 8px; }}
.welcome .tagline {{ font-size: 16px; color: #666; margin-bottom: 2rem; }}
.welcome .stats {{ font-size: 14px; color: #888; }}

/* Article view */
.article-view {{ display: none; }}
.article-view.active {{ display: block; }}

.breadcrumb {{
  font-size: 12px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}}

.article-header h1 {{
  font-size: 2rem;
  font-weight: 700;
  border-bottom: 2px solid #c8c8b4;
  padding-bottom: 8px;
  margin-bottom: 12px;
}}

.metadata-grid {{
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2px 16px;
  font-size: 13px;
  color: #555;
  margin-bottom: 12px;
}}

.metadata-grid dt {{ font-weight: 600; color: #444; }}
.metadata-grid dd {{ margin: 0; }}

.tldr-box {{
  background: #fff8dc;
  border: 1px solid #e6d9a3;
  border-radius: 6px;
  padding: 12px 16px;
  margin: 12px 0 24px;
  font-size: 15px;
  font-style: italic;
  color: #555;
  line-height: 1.5;
}}

/* Article body */
.article-body {{
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 16px;
  line-height: 1.75;
}}

.article-body h2 {{
  font-family: system-ui, sans-serif;
  font-size: 1.4rem;
  font-weight: 600;
  border-bottom: 1px solid #e0e0d4;
  padding-bottom: 4px;
  margin-top: 2rem;
  margin-bottom: 0.8rem;
}}

.article-body h3 {{
  font-family: system-ui, sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}}

.article-body p {{ margin-bottom: 1rem; }}
.article-body ul, .article-body ol {{ margin-bottom: 1rem; padding-left: 24px; }}
.article-body li {{ margin-bottom: 4px; }}

.article-body table {{
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
  font-family: system-ui, sans-serif;
  font-size: 13px;
}}

.article-body th {{
  background: #eaecf0;
  text-align: left;
  font-weight: 600;
}}

.article-body th, .article-body td {{
  border: 1px solid #c8c8c0;
  padding: 6px 10px;
  vertical-align: top;
}}

.article-body tr:nth-child(even) {{ background: #f8f8f4; }}

.article-body code {{
  background: #f0f0ea;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 14px;
}}

.article-body pre {{
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1rem 0;
}}

.article-body pre code {{
  background: none;
  padding: 0;
  color: inherit;
}}

/* Wiki links */
a.wiki-link {{
  color: #0645ad;
  text-decoration: none;
  border-bottom: 1px dotted #0645ad;
  cursor: pointer;
}}

a.wiki-link:hover {{ border-bottom-style: solid; }}
span.dead-link {{ color: #ba0000; border-bottom: 1px dotted #ba0000; }}
em.source-ref {{ font-style: italic; color: #888; font-size: 0.9em; }}

/* Mobile */
.mobile-toggle {{
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 200;
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 18px;
  cursor: pointer;
}}

@media (max-width: 768px) {{
  #sidebar {{
    position: fixed;
    left: -300px;
    z-index: 100;
    transition: left 0.3s;
    box-shadow: 2px 0 8px rgba(0,0,0,0.1);
  }}
  #sidebar.open {{ left: 0; }}
  #content {{ padding: 1rem; padding-top: 60px; }}
  .mobile-toggle {{ display: block; }}
  .article-header h1 {{ font-size: 1.5rem; }}
}}
</style>
</head>
<body>
<button class="mobile-toggle" onclick="document.getElementById('sidebar').classList.toggle('open')">&#9776;</button>

<div id="app">
  <nav id="sidebar">
    <div class="sidebar-header">
      <div class="site-title">Wiki</div>
      <div class="site-subtitle">LLM-Compiled Knowledge Base</div>
      <input type="text" id="search-input" placeholder="Search articles..." autocomplete="off">
      <div id="search-results"></div>
    </div>
    <div class="sidebar-nav">
      {sidebar_html}
    </div>
  </nav>

  <main id="content">
    <div id="welcome" class="welcome active">
      <h1>Wiki</h1>
      <p class="tagline">Knowledge Base</p>
      <p class="stats">{total} articles &middot; {welcome_stats}</p>
      <p style="margin-top: 2rem; font-size: 14px; color: #aaa;">Select an article from the sidebar or search above.</p>
    </div>
    <div id="article-view" class="article-view">
      <div class="article-header">
        <div class="breadcrumb" id="article-section"></div>
        <h1 id="article-title"></h1>
        <dl class="metadata-grid" id="article-metadata"></dl>
        <div class="tldr-box" id="article-tldr"></div>
      </div>
      <div id="article-body" class="article-body"></div>
    </div>
  </main>
</div>

<script>
const ARTICLES = {articles_json};
const SEARCH_INDEX = {search_json};

function navigateTo(id) {{
  const article = ARTICLES[id];
  if (!article) return;

  history.pushState({{article: id}}, '', '#' + id);

  document.getElementById('welcome').classList.remove('active');
  document.getElementById('article-view').classList.add('active');

  document.getElementById('article-section').textContent = article.section.charAt(0).toUpperCase() + article.section.slice(1);
  document.getElementById('article-title').textContent = article.title;
  document.getElementById('article-metadata').innerHTML = article.metadata;
  document.getElementById('article-tldr').innerHTML = article.tldr || '';
  document.getElementById('article-body').innerHTML = article.html;

  // Show/hide TLDR box
  document.getElementById('article-tldr').style.display = article.tldr ? 'block' : 'none';

  // Active nav state
  document.querySelectorAll('.section-list li a').forEach(a => a.classList.remove('active'));
  const active = document.querySelector('[data-article="' + id + '"]');
  if (active) {{
    active.classList.add('active');
    const section = active.closest('.nav-section');
    if (section) {{
      section.querySelector('.section-list').classList.add('expanded');
      section.querySelector('.section-toggle').classList.add('open');
    }}
  }}

  document.getElementById('content').scrollTo(0, 0);

  // Close mobile sidebar
  if (window.innerWidth <= 768) {{
    document.getElementById('sidebar').classList.remove('open');
  }}

  // Clear search
  document.getElementById('search-input').value = '';
  document.getElementById('search-results').style.display = 'none';
}}

function toggleSection(btn) {{
  btn.classList.toggle('open');
  btn.nextElementSibling.classList.toggle('expanded');
}}

// Search
document.getElementById('search-input').addEventListener('input', function() {{
  const query = this.value.toLowerCase().trim();
  const results = document.getElementById('search-results');

  if (query.length < 2) {{
    results.style.display = 'none';
    results.innerHTML = '';
    return;
  }}

  const matches = SEARCH_INDEX.filter(e =>
    e.title.toLowerCase().includes(query) ||
    e.tldr.toLowerCase().includes(query) ||
    e.text.toLowerCase().includes(query)
  ).sort((a, b) => {{
    const at = a.title.toLowerCase().includes(query) ? 0 : 1;
    const bt = b.title.toLowerCase().includes(query) ? 0 : 1;
    if (at !== bt) return at - bt;
    const atl = a.tldr.toLowerCase().includes(query) ? 0 : 1;
    const btl = b.tldr.toLowerCase().includes(query) ? 0 : 1;
    return atl - btl;
  }});

  function hl(text, q) {{
    if (!text) return '';
    const esc = q.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&');
    return text.replace(new RegExp('(' + esc + ')', 'gi'), '<mark>$1</mark>');
  }}

  results.innerHTML = matches.slice(0, 10).map(m =>
    '<div class="search-result" onclick="navigateTo(\\'' + m.id + '\\')">' +
    '<div class="result-title">' + hl(m.title, query) + '</div>' +
    '<div class="result-section">' + m.section + '</div>' +
    '<div class="result-tldr">' + hl(m.tldr, query) + '</div>' +
    '</div>'
  ).join('');

  results.style.display = matches.length ? 'block' : 'none';
}});

// Hash routing
window.addEventListener('hashchange', function() {{
  const hash = location.hash.slice(1);
  if (hash && ARTICLES[hash]) navigateTo(hash);
}});

window.addEventListener('popstate', function(e) {{
  if (e.state && e.state.article) {{
    navigateTo(e.state.article);
  }} else {{
    document.getElementById('article-view').classList.remove('active');
    document.getElementById('welcome').classList.add('active');
  }}
}});

// Init
window.addEventListener('load', function() {{
  const hash = location.hash.slice(1);
  if (hash && ARTICLES[hash]) navigateTo(hash);
}});
</script>
</body>
</html>'''


def main():
    print("Discovering articles...")
    articles = discover_articles()
    print(f"  Found {len(articles)} articles")

    print("Parsing articles...")
    for a in articles:
        parse_article(a)

    print("Assigning people groups...")
    assign_people_groups(articles)

    lookup = build_article_lookup(articles)
    print(f"  Backlink lookup: {len(lookup)} entries")

    print("Applying privacy filter and converting to HTML...")
    for a in articles:
        a.raw_body = apply_privacy_filter(a.raw_body)
        a.html_body = md_to_html(a.raw_body)
        a.html_body = resolve_backlinks(a.html_body, lookup)
        a.html_body = neutralize_raw_links(a.html_body)

        # Resolve backlinks in metadata values too
        for key in a.metadata:
            if '[[' in str(a.metadata[key]):
                a.metadata[key] = resolve_backlinks(a.metadata[key], lookup)

        # Resolve backlinks in TLDR
        if '[[' in a.tldr:
            a.tldr = resolve_backlinks(a.tldr, lookup)

    print("Building search index...")
    search_index = build_search_index(articles)

    print("Building sidebar...")
    sidebar_html = build_sidebar_html(articles)

    print("Assembling HTML...")
    html_output = build_html(articles, search_index, sidebar_html)

    OUTPUT_FILE.write_text(html_output, encoding="utf-8")
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\nDone! Built {OUTPUT_FILE.name}")
    print(f"  Size: {size_kb:.0f} KB")
    print(f"  Articles: {len(articles)}")
    print(f"  Open in browser: file://{OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
