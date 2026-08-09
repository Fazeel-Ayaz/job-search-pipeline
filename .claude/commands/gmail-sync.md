---
description: Sync Gmail responses to Notion tracker statuses. Updates Status, Date Applied (from confirmation email date), and Notes.
allowed-tools: Read, mcp__76387141-c378-4a16-afdc-52f4a6834bf4__search_threads, mcp__76387141-c378-4a16-afdc-52f4a6834bf4__get_thread, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-fetch, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-update-page, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-search
---

# /gmail-sync

## Context
Load before starting:
- `CLAUDE.md`
- `context/infrastructure.md`

---

Run `agents/gmail-syncer.md` with the following additions:

## Additional rule — Date Applied
When a "Confirmation Received" email is found for a role:
- Use the email's received date as the `Date Applied` value in the Notion row.
- This is the best available proxy since the user applies manually and no other apply-date signal exists.
- Only set `Date Applied` if it is currently empty — do not overwrite an existing value.

## Status mapping (from context/infrastructure.md)
Follow the Gmail status mapping table exactly. Never move a status backwards. Never mark Rejected unless the email is unambiguous.

## Ambiguous emails
Log to `working/gmail_ambiguous_$(date +%Y-%m-%d).json`. Do not guess.

## If Gmail MCP is not connected
Stop immediately. Report: "Gmail MCP is not connected. Connect it in Cowork/Claude Code settings and re-run /gmail-sync."
