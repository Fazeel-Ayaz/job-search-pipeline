#!/usr/bin/env python3
"""
query_approved.py — Query Notion directly for approved "To Apply" roles from the last N days.

Uses the Notion REST API (POST /v1/databases/{id}/query) with a compound filter — the only
reliable way to filter by checkbox property. The Notion MCP search tool cannot do this.

Returns a JSON array to stdout:
  [{page_id, page_url, title, company, date_found, has_resume, has_cover_letter}]

Each row is then processed by /filling-in — no MCP search cascade needed.

Usage:
  python3 scripts/query_approved.py              # last 3 days (default)
  python3 scripts/query_approved.py --days 7     # last 7 days
  python3 scripts/query_approved.py --debug      # verbose logging to stderr

Setup:
  Add "notion_token": "secret_..." to claude-job-profile.json under "apis".
  Add "database_id": "..." to claude-job-profile.json under "notion".
  Create token at: https://www.notion.so/profile/integrations
  Then share the "Job Application Tracker" database with the integration.
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────
# Profile lives at the project root — one level up from scripts/
PROFILE_PATH = Path(__file__).resolve().parent.parent / "claude-job-profile.json"
NOTION_VER   = "2022-06-28"
NOTION_BASE  = "https://api.notion.com/v1"

_debug = False


# ── Helpers ───────────────────────────────────────────────────────────

def load_config():
    """Load token and database ID from profile JSON or environment variables."""
    token = os.environ.get("NOTION_TOKEN")
    db_id = os.environ.get("NOTION_DATABASE_ID")

    if not PROFILE_PATH.exists():
        if not token or not db_id:
            print("ERROR: claude-job-profile.json not found in project root.", file=sys.stderr)
            print("       Copy claude-job-profile.template.json → claude-job-profile.json and fill in your values.", file=sys.stderr)
            print("       Or set NOTION_TOKEN and NOTION_DATABASE_ID environment variables.", file=sys.stderr)
            sys.exit(1)
        return token, db_id

    with open(PROFILE_PATH) as f:
        profile = json.load(f)

    if not token:
        token = profile.get("apis", {}).get("notion_token", "")
    if not token:
        print("ERROR: notion_token not found in claude-job-profile.json under apis.", file=sys.stderr)
        print("       Create one at https://www.notion.so/profile/integrations", file=sys.stderr)
        sys.exit(1)

    if not db_id:
        db_id = profile.get("notion", {}).get("database_id", "")
    if not db_id:
        print("ERROR: notion.database_id not found in claude-job-profile.json.", file=sys.stderr)
        print("       Add it under the 'notion' key — it's the 32-char ID from your Notion database URL.", file=sys.stderr)
        sys.exit(1)

    return token, db_id


def notion_req(token, method, path, body=None):
    url  = f"{NOTION_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req  = Request(url, data=data, method=method, headers={
        "Authorization":    f"Bearer {token}",
        "Notion-Version":   NOTION_VER,
        "Content-Type":     "application/json",
    })
    if _debug:
        print(f"  [notion] {method} {path}", file=sys.stderr)
    try:
        with urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except HTTPError as e:
        err = e.read().decode()
        print(f"ERROR: Notion {method} {path} → {e.code}: {err}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"ERROR: Network error calling Notion: {e}", file=sys.stderr)
        sys.exit(1)


def prop(page, name, kind):
    """Extract a typed property value from a Notion page result."""
    p = page.get("properties", {}).get(name, {})
    if kind == "title":
        return "".join(r.get("plain_text", "") for r in p.get("title", []))
    if kind == "text":
        return "".join(r.get("plain_text", "") for r in p.get("rich_text", []))
    if kind == "date":
        d = p.get("date"); return d["start"] if d else None
    if kind == "select":
        s = p.get("select"); return s["name"] if s else None
    if kind == "checkbox":
        return p.get("checkbox", False)
    return None


def page_has_section(token, page_id, heading_text):
    """Return True if a heading block containing heading_text exists in the page body."""
    cursor, found = None, False
    while not found:
        path = f"/blocks/{page_id}/children" + (f"?start_cursor={cursor}" if cursor else "")
        result = notion_req(token, "GET", path)
        for block in result.get("results", []):
            btype = block.get("type", "")
            if btype in ("heading_1", "heading_2", "heading_3"):
                text = "".join(
                    r.get("plain_text", "")
                    for r in block.get(btype, {}).get("rich_text", [])
                )
                if heading_text.lower() in text.lower():
                    return True
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")
    return False


# ── Main ──────────────────────────────────────────────────────────────

def main():
    global _debug
    args   = sys.argv[1:]
    _debug = "--debug" in args
    days   = 3
    if "--days" in args:
        idx = args.index("--days")
        if idx + 1 < len(args):
            days = int(args[idx + 1])

    token, database_id = load_config()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    if _debug:
        print(f"[query_approved] database={database_id}", file=sys.stderr)
        print(f"[query_approved] filter: Approved=true · Status=To Apply · Date Found >= {cutoff}", file=sys.stderr)

    # ── Query database with compound filter ───────────────────────────
    filter_body = {
        "filter": {
            "and": [
                {"property": "Approved?",   "checkbox": {"equals": True}},
                {"property": "Status",      "select":   {"equals": "To Apply"}},
                {"property": "Date Found",  "date":     {"on_or_after": cutoff}},
            ]
        },
        "sorts": [{"property": "Date Found", "direction": "descending"}],
    }

    pages, cursor = [], None
    while True:
        body = dict(filter_body)
        if cursor:
            body["start_cursor"] = cursor
        result = notion_req(token, "POST", f"/databases/{database_id}/query", body)
        pages.extend(result.get("results", []))
        if not result.get("has_more"):
            break
        cursor = result.get("next_cursor")

    if _debug:
        print(f"[query_approved] {len(pages)} rows matched filter", file=sys.stderr)

    # ── Check each page for resume / cover letter sections ────────────
    output = []
    for page in pages:
        page_id  = page["id"]
        page_url = page.get("url", f"https://notion.so/{page_id.replace('-', '')}")
        title    = prop(page, "Role Title", "title")
        company  = prop(page, "Company",    "text")
        date_found = prop(page, "Date Found", "date")

        if _debug:
            print(f"  [query_approved] checking blocks: {company} — {title}", file=sys.stderr)

        has_resume = page_has_section(token, page_id, "Tailored Resume")
        has_cl     = page_has_section(token, page_id, "Cover Letter")

        output.append({
            "page_id":           page_id,
            "page_url":          page_url,
            "title":             title,
            "company":           company,
            "date_found":        date_found,
            "has_resume":        has_resume,
            "has_cover_letter":  has_cl,
        })

    print(json.dumps(output, indent=2))

    # Summary to stderr so Claude Code can log it without polluting JSON stdout
    print(f"\n[query_approved] Done: {len(output)} eligible rows", file=sys.stderr)
    for r in output:
        res = "✓ resume" if r["has_resume"] else "✗ no resume"
        cl  = "✓ CL"     if r["has_cover_letter"] else "✗ no CL"
        print(f"  {r['company']} — {r['title']} | {res} | {cl}", file=sys.stderr)


if __name__ == "__main__":
    main()
