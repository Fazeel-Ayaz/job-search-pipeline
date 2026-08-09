---
description: For all approved Notion rows without a resume, run LinkedIn check, generate resume + cover letter, and update Notion. Flags partial rows for manual attention.
allowed-tools: Read, Write, Bash, WebFetch, WebSearch, mcp__Claude_in_Chrome__navigate, mcp__Claude_in_Chrome__get_page_text, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-fetch, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page
---

# /filling-in

## Context
Load before starting:
- `CLAUDE.md`
- `context/profile.md`
- `context/resume-format.md`
- `context/infrastructure.md`

---

## Step 1 — Find eligible rows
Run the query script to get approved rows from Notion directly via the REST API:

```bash
python3 scripts/query_approved.py --days 3
```

This uses `POST /v1/databases/{id}/query` with a compound filter (`Approved? = true` AND `Status = "To Apply"` AND `Date Found >= 3 days ago`) and returns a JSON array to stdout. The Notion MCP search tool cannot filter by checkbox property — do not attempt `notion-search` as a fallback.

**If the script fails with a token error:**
Stop and tell the user:
> "query_approved.py needs a Notion internal integration token. Create one at https://www.notion.so/profile/integrations (takes ~2 min), then add it to `claude-job-profile.json` under `apis.notion_token`. Also add your database ID under `notion.database_id`. Then share the 'Job Application Tracker' database with the integration from the database's Connection settings."

**If the script returns an empty array `[]`:**
Stop and report: "No eligible rows found — no approved 'To Apply' roles from the last 3 days."

**Parse the JSON output.** Each element is:
```json
{
  "page_id": "...",
  "page_url": "...",
  "title": "Role Title",
  "company": "Company Name",
  "date_found": "2026-06-14",
  "has_resume": false,
  "has_cover_letter": false
}
```

The `has_resume` and `has_cover_letter` flags are already detected by the script (it checks for `## Tailored Resume` and `## Cover Letter` headings in the page body). Use them directly — do not re-fetch the page.

For each matching row, check:

| Condition | Action |
|-----------|--------|
| Resume exists AND cover letter exists | Skip silently — already complete. |
| Resume exists but NO cover letter | ⚠ Flag to user: "**[Company] — [Role]:** has a resume but no cover letter. Review manually." Skip this row. |
| Cover letter exists but NO resume | ⚠ Flag to user: "**[Company] — [Role]:** has a cover letter but no resume. Review manually." Skip this row. |
| Neither resume nor cover letter | Proceed with full filling-in workflow. |

Print all flags before doing any work. If any rows need manual attention, list them clearly at the top of the output.

## Step 2 — LinkedIn Connections check
For each row proceeding to full workflow:
Run `skills/linkedin-connections.md` — check for 1st-degree connections at the company (and parent company if applicable). Generate a personalised outreach message for any connections found.
Hold the result as text: "LinkedIn: [name, title, warmth] — [outreach message draft]" or "LinkedIn: No 1st-degree connections found." It gets written to the page body in Step 5 — do not fetch or update Notion yet.

## Step 3 — Resume
Run `agents/resume-tailor.md` for this role.

**Important:** Archetype and comp range are already in the Notion row from /job-search or /job-scope.
Use `notion-fetch` on the `page_url` from Step 1 to read the `## Archetype Detection` and `## Comp Research` sections — do not re-run archetype detection or comp research.
Pass the existing archetype and comp data into the Resume Tailor as context.

Output: 1-page PDF at `resumes/[Your-Name]-[Company]-[RoleSlug].pdf`. Verify with pypdf.

## Step 4 — Cover Letter
Run `agents/cover-letter-writer.md` for this role.
Output: PDF at `resumes/[Your-Name]-[Company]-[RoleSlug]-Cover-Letter.pdf`. Verify 1 page.

## Step 5 — Update Notion
Update the existing Notion page (do not create a new row). Do this in two calls, neither of which requires fetching the existing page:

1. `insert_content` (position: end) — append everything in ONE call:
   ```
   ## Tailored Resume
   [Full formatted resume text]

   ## Cover Letter
   [Full cover letter text]

   ## Filling-In Log
   - [LinkedIn result from Step 2]
   - Resume generated [date]
   - Cover letter generated [date]
   ```
2. `update_properties` — set `Keywords` to the actual JD keywords injected into the resume.

Do NOT touch the `Notes` property in this workflow — `Notes` is /job-scope's research output. The `## Filling-In Log` block above is the home for filling-in-specific tracking info.

---

## Stop here
Print a summary of what was completed, what was flagged, and what was skipped.
You review the resume and cover letter in Notion, then apply manually.
