"""
Builds the static site from stories/*.json into site/.
index.html is the latest story. Each story also lives at s/<date>.html.
archive.html lists every past edition.

Run: python scripts/build_site.py
"""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORIES_DIR = ROOT / "stories"
SITE_DIR = ROOT / "site"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__NAME__ | The Study</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,600;9..144,900&family=Spectral:wght@300;400;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --ink: #10151d;
    --ink-2: #161d27;
    --paper: #ede6d6;
    --paper-dim: #b9b2a2;
    --brass: #c9a24b;
    --rule: #2a3341;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { height: 100%; }
  body {
    background: var(--ink);
    color: var(--paper);
    font-family: 'Spectral', serif;
    font-weight: 300;
    overflow: hidden;
  }
  .deck { height: 100%; position: relative; }
  .slide {
    position: absolute; inset: 0;
    display: none;
    padding: 6vh 8vw;
    overflow-y: auto;
  }
  .slide.active { display: flex; flex-direction: column; justify-content: center; }
  .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--brass);
    margin-bottom: 1.4rem;
  }
  /* Cover slide */
  .cover { text-align: left; }
  .cover .date {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    color: var(--paper-dim);
    margin-bottom: 3rem;
  }
  .cover h1 {
    font-family: 'Fraunces', serif;
    font-weight: 900;
    font-size: clamp(2.6rem, 8vw, 6.5rem);
    line-height: 0.98;
    letter-spacing: -0.015em;
    margin-bottom: 1.2rem;
  }
  .cover .tagline {
    font-size: clamp(1.05rem, 2.2vw, 1.4rem);
    color: var(--paper-dim);
    max-width: 34em;
    margin-bottom: 2.4rem;
  }
  .cover .meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.14em;
    color: var(--brass);
  }
  .cover .meta span { margin-right: 2.2rem; }
  /* Story slides */
  .slide h2 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(1.7rem, 4vw, 2.8rem);
    line-height: 1.1;
    margin-bottom: 1.6rem;
    max-width: 20em;
  }
  .slide .body {
    font-size: clamp(1rem, 1.7vw, 1.2rem);
    line-height: 1.72;
    max-width: 38em;
  }
  .slide .body p + p { margin-top: 1.1em; }
  /* Part divider slide */
  .divider { text-align: center; align-items: center; }
  .divider h2 {
    font-family: 'Fraunces', serif;
    font-weight: 300;
    font-style: italic;
    font-size: clamp(1.8rem, 4.5vw, 3.2rem);
    max-width: 18em;
    margin: 0 auto;
  }
  .divider .eyebrow { margin-bottom: 2rem; }
  /* Breakdown slides: the signature element */
  .step { border-left: 1px solid var(--rule); padding-left: clamp(1.4rem, 3vw, 2.6rem); position: relative; }
  .step::before {
    content: '';
    position: absolute; left: -4px; top: 0.5rem;
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--brass);
  }
  .step .label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--paper-dim);
    margin: 1.8rem 0 0.5rem;
  }
  .step .label:first-of-type { margin-top: 1.6rem; }
  .step .label.works { color: var(--brass); }
  .step .body { font-size: clamp(0.98rem, 1.6vw, 1.15rem); }
  /* Lesson slide */
  .lesson { text-align: center; align-items: center; }
  .lesson blockquote {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(1.6rem, 4vw, 3rem);
    line-height: 1.25;
    max-width: 20em;
    margin: 0 auto 3rem;
  }
  .lesson a {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    color: var(--brass);
    text-decoration: none;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 4px;
  }
  /* Progress ticks */
  .progress {
    position: fixed; bottom: 0; left: 0; right: 0;
    display: flex; gap: 3px;
    padding: 0 8vw 18px;
    z-index: 10;
  }
  .progress .tick { flex: 1; height: 2px; background: var(--rule); transition: background 0.25s; }
  .progress .tick.done { background: var(--brass); }
  /* Nav hints */
  .navhint {
    position: fixed; top: 22px; right: 8vw;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.16em;
    color: var(--paper-dim); z-index: 10;
  }
  .brand {
    position: fixed; top: 22px; left: 8vw;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.24em;
    color: var(--paper-dim); z-index: 10;
    text-decoration: none;
  }
  .brand:hover, .lesson a:hover { color: var(--paper); }
  @media (max-width: 640px) {
    .slide { padding: 10vh 7vw 12vh; }
    .slide.active { justify-content: flex-start; }
  }
  @media (prefers-reduced-motion: no-preference) {
    .slide.active > * { animation: rise 0.5s ease both; }
    @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
  }
</style>
</head>
<body>
<a class="brand" href="archive.html">THE STUDY</a>
<div class="navhint">&larr; &rarr; TO READ</div>
<div class="deck" id="deck">
__SLIDES__
</div>
<div class="progress" id="progress"></div>
<script>
  var slides = document.querySelectorAll('.slide');
  var progress = document.getElementById('progress');
  var i = 0;
  slides.forEach(function () {
    var t = document.createElement('div');
    t.className = 'tick';
    progress.appendChild(t);
  });
  var ticks = progress.children;
  function show(n) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    for (var k = 0; k < slides.length; k++) {
      slides[k].classList.toggle('active', k === i);
      ticks[k].classList.toggle('done', k <= i);
    }
    slides[i].scrollTop = 0;
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight' || e.key === ' ') show(i + 1);
    if (e.key === 'ArrowLeft') show(i - 1);
  });
  document.addEventListener('click', function (e) {
    if (e.target.closest('a')) return;
    show(e.clientX > window.innerWidth / 2 ? i + 1 : i - 1);
  });
  var x0 = null;
  document.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; });
  document.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) show(dx < 0 ? i + 1 : i - 1);
    x0 = null;
  });
  show(0);
</script>
</body>
</html>
"""

ARCHIVE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Archive | The Study</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,900&family=Spectral:wght@300;400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root { --ink:#10151d; --paper:#ede6d6; --paper-dim:#b9b2a2; --brass:#c9a24b; --rule:#2a3341; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--ink); color:var(--paper); font-family:'Spectral',serif; font-weight:300; padding:10vh 8vw; }
  h1 { font-family:'Fraunces',serif; font-weight:900; font-size:clamp(2.4rem,6vw,4.5rem); margin-bottom:0.6rem; }
  .sub { font-family:'IBM Plex Mono',monospace; font-size:0.75rem; letter-spacing:0.2em; color:var(--paper-dim); text-transform:uppercase; margin-bottom:4rem; }
  a.entry { display:flex; align-items:baseline; gap:2rem; padding:1.4rem 0; border-bottom:1px solid var(--rule); text-decoration:none; color:var(--paper); }
  a.entry:hover .name { color:var(--brass); }
  .date { font-family:'IBM Plex Mono',monospace; font-size:0.72rem; letter-spacing:0.14em; color:var(--paper-dim); min-width:7.5em; }
  .name { font-family:'Fraunces',serif; font-weight:600; font-size:clamp(1.2rem,2.6vw,1.8rem); transition:color 0.2s; }
  .tag { color:var(--paper-dim); font-size:0.95rem; display:none; }
  @media (min-width:700px) { .tag { display:block; } }
</style>
</head>
<body>
<h1>The Study</h1>
<div class="sub">One person a day. How they actually did it.</div>
__ENTRIES__
</body>
</html>
"""


def paragraphs(text):
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "".join(f"<p>{html.escape(p)}</p>" for p in parts)


def render_story_page(piece):
    slides = []

    slides.append(
        '<section class="slide cover">'
        f'<div class="date">{html.escape(piece["date"])} &middot; DAILY EDITION</div>'
        f'<h1>{html.escape(piece["name"])}</h1>'
        f'<div class="tagline">{html.escape(piece["tagline"])}</div>'
        f'<div class="meta"><span>{html.escape(piece.get("domain", ""))}</span>'
        f'<span>{html.escape(piece.get("era", ""))}</span></div>'
        "</section>"
    )

    for idx, s in enumerate(piece["story"], 1):
        slides.append(
            '<section class="slide">'
            f'<div class="eyebrow">The story &middot; {idx} of {len(piece["story"])}</div>'
            f'<h2>{html.escape(s["heading"])}</h2>'
            f'<div class="body">{paragraphs(s["body"])}</div>'
            "</section>"
        )

    slides.append(
        '<section class="slide divider">'
        '<div class="eyebrow">Part two</div>'
        "<h2>That is what happened. Here is how it was actually possible.</h2>"
        "</section>"
    )

    for idx, b in enumerate(piece["breakdown"], 1):
        slides.append(
            '<section class="slide">'
            f'<div class="eyebrow">The mechanism &middot; step {idx} of {len(piece["breakdown"])}</div>'
            '<div class="step">'
            f'<h2>{html.escape(b["title"])}</h2>'
            '<div class="label">What happened</div>'
            f'<div class="body">{paragraphs(b["what_happened"])}</div>'
            '<div class="label works">Why it worked</div>'
            f'<div class="body">{paragraphs(b["why_it_worked"])}</div>'
            "</div></section>"
        )

    apps = piece.get("applications", [])
    if apps:
        slides.append(
            '<section class="slide divider">'
            '<div class="eyebrow">Part three</div>'
            "<h2>How you could use this today.</h2>"
            "</section>"
        )
        for idx, a in enumerate(apps, 1):
            slides.append(
                '<section class="slide">'
                f'<div class="eyebrow">Apply it today &middot; {idx} of {len(apps)}</div>'
                '<div class="step">'
                f'<h2>{html.escape(a["title"])}</h2>'
                f'<div class="body" style="margin-top:1.4rem">{paragraphs(a["body"])}</div>'
                "</div></section>"
            )

    slides.append(
        '<section class="slide lesson">'
        '<div class="eyebrow">The lesson</div>'
        f'<blockquote>{html.escape(piece["one_line_lesson"])}</blockquote>'
        '<a href="archive.html">READ PAST EDITIONS &rarr;</a>'
        "</section>"
    )

    return PAGE_TEMPLATE.replace("__NAME__", html.escape(piece["name"])).replace(
        "__SLIDES__", "\n".join(slides)
    )


def main():
    SITE_DIR.mkdir(exist_ok=True)
    (SITE_DIR / "s").mkdir(exist_ok=True)

    story_files = sorted(STORIES_DIR.glob("*.json"))
    if not story_files:
        raise SystemExit("No stories found in stories/. Run research.py first.")

    pieces = [json.loads(f.read_text()) for f in story_files]
    pieces.sort(key=lambda p: p["date"])

    for piece in pieces:
        page = render_story_page(piece)
        (SITE_DIR / "s" / f"{piece['date']}.html").write_text(page)

    latest = render_story_page(pieces[-1]).replace('href="archive.html"', 'href="archive.html"')
    (SITE_DIR / "index.html").write_text(latest)

    entries = []
    for piece in reversed(pieces):
        entries.append(
            f'<a class="entry" href="s/{piece["date"]}.html">'
            f'<span class="date">{html.escape(piece["date"])}</span>'
            f'<span class="name">{html.escape(piece["name"])}</span>'
            f'<span class="tag">{html.escape(piece["tagline"])}</span>'
            "</a>"
        )
    archive = ARCHIVE_TEMPLATE.replace("__ENTRIES__", "\n".join(entries))
    (SITE_DIR / "archive.html").write_text(archive)
    # Story pages link to archive.html one level up
    for f in (SITE_DIR / "s").glob("*.html"):
        f.write_text(f.read_text().replace('href="archive.html"', 'href="../archive.html"'))

    print(f"Built site with {len(pieces)} edition(s) into {SITE_DIR}")


if __name__ == "__main__":
    main()
