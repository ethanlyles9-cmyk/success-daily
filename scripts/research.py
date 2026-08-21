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
