# PROJECT CONTEXT: The Study (success-daily)

Handoff document for AI. Read this fully before doing anything. It contains the complete project vision, all decisions made, the full source code of every file, deployment state, and the owner's working preferences. Nothing else should need to be re-explained.

Last updated: August 20, 2026.

---

## 1. WHO OWNS THIS

Ethan Lyles, 26, Georgetown/Austin TX. Founder of Panda AI Systems LLC, an AI automation consultancy for HVAC companies. He builds with Make.com and Claude Code inside VS Code. He does NOT read or write code himself; AI writes all code for him. This project is a PERSONAL project (not client work), though he may invite others to view it later and it is built public-ready.

## 2. THE VISION (in Ethan's own framing)

A live website that publishes, every single day, a beautiful slideshow that is a 10 to 15 minute read profiling ONE successful person. AI does really, really in-depth research on that person, then the piece is structured as:

- Top portion (about 1/3): abbreviated but vivid version of their life story. WHAT they did.
- Bottom portion (about 2/3): the breakdown of HOW they were actually able to become successful. What actions, what events, what really happened. The reader should be able to figure out the actual mechanism of the person's success.
- Added later at Ethan's request: a third section, "Apply it today", with 3 to 5 practical modern applications a reader could act on this week, each tied to a specific breakdown step.
- Ends with a one-line lesson.

Focus: mostly business, career, financial, and engineering success. Other fields occasionally.

Ethan's stated key to the project: the depth of the AI research is what makes it great. Not surface-level Wikipedia summaries. The research must figure out how the success was actually possible.

## 3. ARCHITECTURE (as built and approved by Ethan)

Repo name: success-daily. Site brand name used in the UI: "The Study".

Four components:

1. RESEARCH ENGINE: scripts/research.py. Three-pass loop on the Anthropic API (model claude-sonnet-4-6) with the web_search server tool (web_search_20250305, max 10 uses per pass):
   - Pass 1: chronological life timeline with specifics (years, dollar amounts, names).
   - Pass 2: deep dive into success mechanics: first money, pivotal decisions, skills, mentors/partners, risks, luck/timing, near-failures. Flags disputed vs documented claims.
   - Pass 3: no search. Synthesizes into structured JSON (schema in section 5) in the two-part + applications format. Style rules baked into prompt: plain confident prose, no em dashes anywhere, no bullets in body text, no generic advice.
   - Person selection: pops next name from queue.json "seed" list; if empty, Claude picks someone not in "covered", biased to business/career/financial/engineering, including lesser-known figures.
   - Output: stories/YYYY-MM-DD.json, then appends the person to "covered".

2. PERSON QUEUE: queue.json with "seed" (names Ethan wants covered, in order) and "covered" (no repeats). Ethan controls coverage by editing the seed list.

3. SITE BUILDER: scripts/build_site.py. Pure Python, no dependencies. Reads all stories/*.json, renders:
   - site/index.html = latest edition as a full-screen slideshow
   - site/s/YYYY-MM-DD.html = every edition permanently
   - site/archive.html = list of all editions ("The Study / One person a day. How they actually did it.")
   Slideshow navigation: arrow keys, space, click left/right half of screen, touch swipe. Progress ticks along the bottom. Older stories without an "applications" field still render fine (backward compatible via .get).

4. SCHEDULER + HOSTING: .github/workflows/daily.yml. GitHub Actions cron at 11:00 UTC (6:00 AM Central) daily, plus manual workflow_dispatch, plus rebuild-on-push. Scheduled/manual runs execute research.py (needs repo secret ANTHROPIC_API_KEY), commit the new story JSON + queue.json back to main as "study-bot", build the site, deploy via GitHub Pages (actions/deploy-pages, Pages source must be set to "GitHub Actions"). Pushes only rebuild+deploy without running research. Site URL: https://USERNAME.github.io/success-daily/

Cost note given to Ethan: roughly $0.50 to a couple dollars per daily run depending on research depth.

## 4. DESIGN SYSTEM (approved, Ethan said he was "blown away")

Aesthetic: dark study/archive feel. NOT the generic cream-and-terracotta AI look.

- Colors: ink #10151d (background), paper #ede6d6 (text), paper-dim #b9b2a2 (secondary), brass #c9a24b (accent), rule #2a3341 (lines)
- Type: Fraunces (display, weights 300/600/900), Spectral (body, light), IBM Plex Mono (eyebrows/labels/meta), loaded from Google Fonts
- Signature element: breakdown steps rendered as a left-ruled "step" block with a brass dot, monospace labels "What happened" / "Why it worked" (the "works" label is brass)
- Slide flow: Cover (date, huge Fraunces 900 name, tagline, domain + era in brass mono) -> "The story" slides -> divider slide ("That is what happened. Here is how it was actually possible.") -> "The mechanism" step slides -> divider ("Part three / How you could use this today.") -> "Apply it today" slides -> closing lesson blockquote with link to archive
- Subtle rise animation on slide change, respects prefers-reduced-motion; responsive to mobile (top-aligned scrollable slides under 640px)

## 5. STORY JSON SCHEMA

{
  "date": "YYYY-MM-DD",
  "name": "Full Name",
  "tagline": "one line describing who they are",
  "domain": "e.g. Business, Engineering, Finance",
  "era": "e.g. 1877 to 1961",
  "story": [ {"heading": "...", "body": "2-4 paragraphs separated by \n\n"} ],            // 4-6 slides
  "breakdown": [ {"title": "...", "what_happened": "paragraph", "why_it_worked": "paragraph"} ],  // 6-10 steps, chronological
  "applications": [ {"title": "...", "body": "paragraph"} ],                                // 3-5 items, each tied to a breakdown step
  "one_line_lesson": "the single sharpest takeaway"
}

## 6. CURRENT STATUS / WHERE WE LEFT OFF

DONE:
- Full project built and syntax-verified. Site builder tested and rendering correctly (14 slides from the sample edition).
- Sample edition stories/2026-08-19.json (Sam Zemurray) written by hand as a design preview, clearly labeled as a sample inside its content. It includes the applications section.
- v1 zip and an update zip (applications feature) delivered to Ethan with exact push commands.

NOT YET CONFIRMED DONE BY ETHAN (ask before assuming):
- Whether he created the GitHub repo and pushed
- Whether he added the ANTHROPIC_API_KEY secret and set Pages source to "GitHub Actions"
- Whether the first real research run succeeded. The API pipeline was never live-tested (no key available in the build environment). If the first Actions run errored, debugging that is the immediate next task. Ask him to paste the Actions log.

DEPLOYMENT STEPS GIVEN TO HIM (for reference):
1. Create repo success-daily on github.com
2. unzip, git init, add, commit, branch -M main, add remote, push
3. Repo Settings > Secrets and variables > Actions > new secret ANTHROPIC_API_KEY
4. Settings > Pages > Source: GitHub Actions
5. Actions tab > "Daily edition" > Run workflow (first live edition)

LIKELY FUTURE IDEAS (mentioned or natural next steps, none committed):
- Inviting others to view it (it is already public-web ready)
- Possibly a custom domain later
- Deleting or keeping the sample Zemurray edition once real editions exist (his call; to remove it, delete stories/2026-08-19.json and rebuild)

## 7. HOW TO WORK WITH ETHAN ON THIS PROJECT (important)

- NEVER use em dashes. Not in chat, not in code comments, not in generated site copy. This rule is also baked into the research prompt.
- Every file you deliver must come with its exact terminal commands in the same message, in a copy-paste block right after the file. Never hand over a file without the command line.
- Simple, direct answers. When he asks a question mid-build, answer in a few short lines. No giant paragraph dumps unless he asks for depth.
- Do not add features, cards, or design changes to his deliverables without his explicit sign-off first. Flag new ideas as decisions and get agreement before building them in.
- Research before answering product-specific or third-party-tool questions. Do not guess at UIs or vendor capabilities.
- For hard requirements (deadlines, money, government stuff), verify against primary sources, link them, and label what is verified vs judgment.
- He prefers normal chat text over files/artifacts unless he explicitly asks for a file (like this one).
- Plain text note format for his Google Docs notes: topic as first short sentence, simple short sentences, no headers/bullets/bold.

## 8. COMPLETE SOURCE CODE

Every file in the repo follows. This is the exact tested code. Repo layout:

success-daily/
  .github/workflows/daily.yml
  .gitignore
  README.md
  queue.json
  scripts/research.py
  scripts/build_site.py
  stories/2026-08-19.json   (sample edition)
  site/                     (generated, gitignored)


### FILE: queue.json

```json
{
  "seed": [
    "Sam Zemurray",
    "Jensen Huang",
    "Estee Lauder",
    "Andrew Carnegie",
    "Sara Blakely"
  ],
  "covered": []
}
```

### FILE: .gitignore

```text
site/
__pycache__/
.env
```

### FILE: README.md

```text
# The Study

Daily AI-researched profile of one successful person, published as a slideshow.

- scripts/research.py  runs the 3-pass research and writes stories/YYYY-MM-DD.json
- scripts/build_site.py  builds the site/ folder from all stories
- .github/workflows/daily.yml  runs it every morning and deploys to GitHub Pages

Add names you want covered to the "seed" list in queue.json.
```

### FILE: .github/workflows/daily.yml

```yaml
name: Daily edition

on:
  schedule:
    - cron: "0 11 * * *" # 6:00 AM Central (11:00 UTC)
  workflow_dispatch: {}
  push:
    branches: [main]

permissions:
  contents: write
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install anthropic

      - name: Run daily research (scheduled runs only)
        if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scripts/research.py

      - name: Commit new story
        if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
        run: |
          git config user.name "study-bot"
          git config user.email "actions@github.com"
          git add stories/ queue.json
          git diff --cached --quiet || git commit -m "Daily edition $(date +%F)"
          git push

      - name: Build site
        run: python scripts/build_site.py

      - name: Upload site
        uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

### FILE: scripts/research.py

```python
"""
Daily research engine.
Picks one successful person, researches them in depth with web search,
and writes a story JSON to stories/YYYY-MM-DD.json.

Run: python scripts/research.py
Needs: ANTHROPIC_API_KEY environment variable.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent
QUEUE_FILE = ROOT / "queue.json"
STORIES_DIR = ROOT / "stories"

MODEL = "claude-sonnet-4-6"
client = anthropic.Anthropic()

WEB_SEARCH = {"type": "web_search_20250305", "name": "web_search", "max_uses": 10}


def extract_text(response):
    """Pull all text blocks out of a response (ignores search blocks)."""
    parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            parts.append(block.text)
    return "\n".join(parts)


def parse_json(text):
    """Parse JSON out of a model response, stripping code fences if present."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response")
    return json.loads(text[start : end + 1])


def pick_person(queue):
    """Take the next seeded person, or have Claude pick one."""
    if queue["seed"]:
        return queue["seed"].pop(0)

    covered = ", ".join(queue["covered"]) if queue["covered"] else "none yet"
    msg = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[
            {
                "role": "user",
                "content": (
                    "Pick one real person with a remarkable success story worth studying. "
                    "Focus mostly on business, career, financial, or engineering success. "
                    "Occasionally someone from another field is fine. "
                    "Prefer people whose path is well documented and instructive, "
                    "including lesser-known figures, not only famous billionaires. "
                    f"Already covered, do not repeat: {covered}. "
                    "Reply with ONLY the person's full name, nothing else."
                ),
            }
        ],
    )
    return extract_text(msg).strip()


def pass_1_timeline(person):
    """Broad research: build the person's full timeline with web search."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        tools=[WEB_SEARCH],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Research the life of {person} using web search. "
                    "Build a detailed chronological timeline of their life: "
                    "upbringing, education, early jobs, first money earned, "
                    "every major venture or role, failures, and the outcome of their career. "
                    "Include specific years, dollar amounts, and names where you can find them. "
                    "Write it as detailed research notes, not a polished article."
                ),
            }
        ],
    )
    return extract_text(msg)


def pass_2_turning_points(person, timeline):
    """Deep dive: dig into HOW they actually succeeded."""
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        tools=[WEB_SEARCH],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Here are research notes on {person}:\n\n{timeline}\n\n"
                    "Now dig deeper with web search into the mechanics of HOW they became successful. "
                    "Investigate specifically:\n"
                    "1. How they made their first real money and how much it was\n"
                    "2. The 2 to 4 pivotal decisions or events that changed their trajectory\n"
                    "3. What skills or knowledge they built, and how they built them\n"
                    "4. Who helped them (mentors, partners, investors) and how those relationships started\n"
                    "5. What risks they took and what they actually risked\n"
                    "6. What role timing, markets, or luck played\n"
                    "7. What almost ruined them and how they survived it\n"
                    "Write detailed findings with specifics. Flag anything that is disputed or mythologized "
                    "versus well documented."
                ),
            }
        ],
    )
    return extract_text(msg)


def pass_3_write(person, timeline, mechanics):
    """Synthesis: write the final two-part piece as structured JSON."""
    today = date.today().isoformat()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": (
                    f"You are writing today's edition of a daily study of successful people. "
                    f"Subject: {person}. Use ONLY the research below.\n\n"
                    f"TIMELINE RESEARCH:\n{timeline}\n\n"
                    f"MECHANICS RESEARCH:\n{mechanics}\n\n"
                    "Write a 10 to 15 minute read in two parts.\n"
                    "PART 1 (about one third): their life story, abbreviated but vivid. What they did.\n"
                    "PART 2 (about two thirds): the breakdown of HOW they became successful. "
                    "Each breakdown step is a real action, decision, or event from their life, "
                    "explained as: what happened, and why it worked. Concrete and specific. "
                    "No generic advice, no 'they worked hard'. The reader should finish able to "
                    "explain the actual mechanism of this person's success.\n\n"
                    "Style rules: plain confident prose, short sentences welcome, no em dashes anywhere, "
                    "no bullet points inside body text.\n\n"
                    "Respond with ONLY valid JSON, no code fences, in exactly this shape:\n"
                    "{\n"
                    f'  "date": "{today}",\n'
                    '  "name": "Full Name",\n'
                    '  "tagline": "one line describing who they are",\n'
                    '  "domain": "e.g. Business, Engineering, Finance",\n'
                    '  "era": "e.g. 1877 to 1961",\n'
                    '  "story": [ {"heading": "...", "body": "2-4 paragraphs separated by \\n\\n"} ],\n'
                    '  "breakdown": [ {"title": "...", "what_happened": "paragraph", "why_it_worked": "paragraph"} ],\n'
                    '  "applications": [ {"title": "...", "body": "paragraph"} ],\n'
                    '  "one_line_lesson": "the single sharpest takeaway"\n'
                    "}\n"
                    "story should have 4 to 6 slides. breakdown should have 6 to 10 steps in chronological order. "
                    "applications should have 3 to 5 items: practical, modern, specific ways a person today "
                    "could apply this person's actual mechanisms in their own career, business, or finances. "
                    "Each application must tie directly to a specific breakdown step, translated to today's world. "
                    "Concrete actions a reader could start this week, not platitudes."
                ),
            }
        ],
    )
    return parse_json(extract_text(msg))


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set")

    queue = json.loads(QUEUE_FILE.read_text())

    person = pick_person(queue)
    print(f"Today's person: {person}")

    print("Pass 1: timeline research...")
    timeline = pass_1_timeline(person)

    print("Pass 2: success mechanics research...")
    mechanics = pass_2_turning_points(person, timeline)

    print("Pass 3: writing the piece...")
    piece = pass_3_write(person, timeline, mechanics)

    out_file = STORIES_DIR / f"{date.today().isoformat()}.json"
    out_file.write_text(json.dumps(piece, indent=2))
    print(f"Wrote {out_file}")

    queue["covered"].append(person)
    QUEUE_FILE.write_text(json.dumps(queue, indent=2))
    print("Queue updated.")


if __name__ == "__main__":
    main()
```

### FILE: scripts/build_site.py

```python
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
```

### FILE: stories/2026-08-19.json

```json
{
  "date": "2026-08-19",
  "name": "Sam Zemurray",
  "tagline": "Penniless Russian immigrant who took over the most powerful company in Central America by out-working and out-thinking everyone above him.",
  "domain": "Business",
  "era": "1877 to 1961",
  "story": [
    {
      "heading": "A kid selling ripe bananas nobody wanted",
      "body": "Sam Zemurray arrived in America in 1891 at age 14 with nothing. He settled in Selma, Alabama, and worked odd jobs until he noticed something at the port of Mobile: banana companies threw away fruit that had ripened too much to survive the rail journey north.\n\nThey called them ripes. To the big importers they were garbage. To Zemurray they were free inventory. He bought them for almost nothing, loaded them on trains, and telegraphed grocers in towns along the line to meet him at the station. By 21 he had $100,000 in the bank, a fortune at the time, built entirely on fruit other people considered worthless."
    },
    {
      "heading": "Going to the source",
      "body": "Instead of staying a middleman, Zemurray went upstream. In 1910 he bought 5,000 acres of land along the Cuyamel River in Honduras, much of it on borrowed money, and started growing his own bananas.\n\nHe did not run the company from an office. He lived in the jungle camps, learned Spanish, worked alongside his field crews, and learned more about growing bananas than any executive in the industry. His company, Cuyamel Fruit, became known for better fruit and better land than the giant United Fruit Company."
    },
    {
      "heading": "The takeover nobody saw coming",
      "body": "In 1930 United Fruit bought Cuyamel for stock worth about $31.5 million, and Zemurray retired as one of the largest shareholders of his old rival.\n\nThen the Depression crushed United Fruit's stock by roughly 90 percent, and management drifted. Zemurray showed up at a board meeting to complain and was dismissed by the chairman. He returned with proxies from other shareholders, took control of the company, and famously told the board: you have been fucking up this business long enough. He ran United Fruit for the next two decades and rebuilt its value many times over."
    },
    {
      "heading": "This is a sample edition",
      "body": "This edition was written as a design preview so you can see the slideshow before the research engine runs. The real daily editions will be longer, deeper, and fully researched by the AI pipeline with web search behind every claim."
    }
  ],
  "breakdown": [
    {
      "title": "He found value in what experts had already discarded",
      "what_happened": "The entire banana industry had decided ripes were trash because they could not survive long shipping. Zemurray did not argue with that fact. He changed the constraint: instead of shipping far, he sold fast and close, telegraphing ahead to grocers so buyers were waiting when the train arrived.",
      "why_it_worked": "His cost of goods was near zero because incumbents had priced the fruit as garbage. Any sale at all was nearly pure profit. He was not competing with United Fruit, he was harvesting their waste stream, which meant a teenager with no capital could enter the hardest industry in America without anyone trying to stop him."
    },
    {
      "title": "He built knowledge nobody above him had",
      "what_happened": "While United Fruit was run by Boston executives who rarely saw a plantation, Zemurray lived in Honduras, physically worked his own land, and mastered every step: soil, drainage, ripening, rail, shipping.",
      "why_it_worked": "It gave him a permanent judgment advantage. When he later took over United Fruit during the Depression, he could walk onto any plantation and fix operations personally. His authority did not come from his title, it came from being the only man in the room who had done every job in the company."
    },
    {
      "title": "He converted a humiliation into a takeover",
      "what_happened": "When United Fruit's chairman brushed him off at the board meeting, Zemurray did not write an angry letter. He quietly gathered proxy votes from other frustrated shareholders, then returned with the legal power to fire the board on the spot.",
      "why_it_worked": "He understood that in a public company, power is votes, not seniority. The stock collapse meant thousands of shareholders were desperate for change, so the proxies were there for anyone willing to do the unglamorous work of collecting them. The insiders never imagined an outsider would actually do it."
    }
  ],
  "applications": [
    {
      "title": "Sell the ripes in your industry",
      "body": "Look for what the big players in your field throw away or ignore: leads they mark dead, customers too small for them, jobs too messy or low-margin. That is discounted inventory. A marketing agency can reactivate a client's dead lead list. A contractor can take the small repair calls the big shops decline and turn them into replacement customers later. Ask this week: what does the biggest company in my market treat as garbage?"
    },
    {
      "title": "Go live where the work happens",
      "body": "Zemurray's edge was jungle knowledge his Boston rivals refused to get. The modern version: if you sell to an industry, spend real days inside it. Ride along on jobs, sit in the office, watch the software get used. A few weeks of firsthand exposure gives you judgment your competitors can't fake on a sales call."
    },
    {
      "title": "Collect the proxies nobody else will",
      "body": "His takeover was just unglamorous legwork others thought was beneath them. Today that looks like personally calling 50 past customers, manually cleaning a data list, or writing individual messages instead of blasts. When a result depends on boring accumulation, the person willing to actually do it usually wins by default."
    }
  ],
  "one_line_lesson": "The biggest opportunities hide inside whatever the incumbents have decided is beneath them."
}
```

END OF PROJECT CONTEXT.
