#!/usr/bin/env python3
"""
Post-filling-in Notion updater.
Reads generated PDFs, extracts text, and appends Tailored Resume + Cover Letter +
Filling-In Log blocks to each Notion tracker page. Also updates Keywords property.

Run after gen_*.py scripts have all verified 1-page PDFs.
"""
import json
import os
import sys
import re
import time
import requests
from pypdf import PdfReader

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "claude-job-profile.json")
RESUMES_DIR  = os.path.join(os.path.dirname(__file__), "..", "resumes")

with open(PROFILE_PATH) as f:
    profile = json.load(f)

NOTION_TOKEN = profile["apis"]["notion_token"]
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type":  "application/json",
    "Notion-Version": "2022-06-28",
}

from datetime import date
TODAY = date.today().isoformat()


def extract_pdf_text(path):
    r = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in r.pages).strip()


def chunks(text, size=1900):
    """Split text into chunks safe for Notion rich_text (2000 char limit)."""
    for i in range(0, len(text), size):
        yield text[i:i + size]


def para_blocks(text):
    blocks = []
    for chunk in chunks(text):
        blocks.append({
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}
        })
    return blocks


def h2_block(title):
    return {
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": title}}]}
    }


def bullet_block(text):
    return {
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]}
    }


def divider():
    return {"type": "divider", "divider": {}}


def append_blocks(page_id, children):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    # Notion allows max 100 children per request — batch if needed
    for i in range(0, len(children), 90):
        batch = children[i:i + 90]
        r = requests.patch(url, headers=HEADERS, json={"children": batch})
        if not r.ok:
            print(f"  [ERROR] append_blocks {page_id}: {r.status_code} {r.text[:200]}")
            return False
        time.sleep(0.4)
    return True


def update_keywords(page_id, keywords):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    body = {
        "properties": {
            "Keywords": {
                "rich_text": [{"type": "text", "text": {"content": keywords}}]
            }
        }
    }
    r = requests.patch(url, headers=HEADERS, json=body)
    if not r.ok:
        print(f"  [ERROR] update_keywords {page_id}: {r.status_code} {r.text[:200]}")
        return False
    return True


# ── Role definitions ────────────────────────────────────────────────────────
# Add one entry per role you want to update. The Notion Logger agent populates
# page_id automatically — copy it from your Notion tracker URL or the Logger output.
#
# Template:
# {
#     "company":    "Company Name",
#     "title":      "Role Title",
#     "page_id":    "NOTION_PAGE_ID_FROM_TRACKER",
#     "resume_pdf": "Your-Name-Company-RoleSlug.pdf",
#     "cl_pdf":     "Your-Name-Company-RoleSlug-Cover-Letter.pdf",
#     "linkedin":   "LinkedIn outreach note or 'No connections found.'",
#     "keywords":   "comma, separated, keywords, used, in, resume",
# }

ROLES = [
    # Add your roles here after running the Notion Logger.
    # Each gen_*.py script in resumes/ logs the page_id it created.
]


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    results = []
    for role in ROLES:
        label = f"{role['company']} — {role['title']}"
        print(f"\n[{label}]")

        resume_path = os.path.join(RESUMES_DIR, role["resume_pdf"])
        cl_path     = os.path.join(RESUMES_DIR, role["cl_pdf"])

        if not os.path.exists(resume_path):
            print(f"  SKIP — resume PDF not found: {resume_path}")
            continue
        if not os.path.exists(cl_path):
            print(f"  SKIP — cover letter PDF not found: {cl_path}")
            continue

        resume_text = extract_pdf_text(resume_path)
        cl_text     = extract_pdf_text(cl_path)

        children = []
        children.append(divider())
        children.append(h2_block("Tailored Resume"))
        children.extend(para_blocks(resume_text))
        children.append(divider())
        children.append(h2_block("Cover Letter"))
        children.extend(para_blocks(cl_text))
        children.append(divider())
        children.append(h2_block("Filling-In Log"))
        children.append(bullet_block(f"LinkedIn: {role['linkedin']}"))
        children.append(bullet_block(f"Resume generated {TODAY}"))
        children.append(bullet_block(f"Cover letter generated {TODAY}"))

        ok1 = append_blocks(role["page_id"], children)
        ok2 = update_keywords(role["page_id"], role["keywords"])

        status = "OK" if (ok1 and ok2) else "PARTIAL ERROR"
        print(f"  {status} — blocks appended: {ok1}, keywords updated: {ok2}")
        results.append((label, status))

    print("\n── Summary ──")
    for label, status in results:
        print(f"  [{status}] {label}")


if __name__ == "__main__":
    main()
