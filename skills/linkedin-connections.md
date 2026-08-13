# Skill: LinkedIn Connections Check

**Trigger:** Run for any job scoring 45+, before logging to Notion.

**If no connections found: log nothing and move on immediately. Do not spend time on this.**

---

## Step 1 — Find the archive

Glob for a directory matching `LinkedIn Data Export*` in the project root. Use the most recent one if multiple exist.

If no matching directory exists: skip this skill entirely. Do not note it in Notion.

---

## Step 2 — Quick CSV lookup

Read `Connections.csv` only. For each row, check if the company name column contains the target company name (case-insensitive substring match). Also check the parent company if relevant — e.g. if the role is at a subsidiary, search both the subsidiary name and the owning group name.

**If no rows match: stop here. Log nothing. Move on.**

---

## Step 3 — Only if matches found: draft outreach

For each matched connection, write a short direct message (4-5 sentences max):
- Name the role and company
- Mention you've applied
- Ask for a referral or internal flag
- Personalise with their title/team

**Output:** Print the list of matches and their outreach messages for the user to review. Add a one-line note to Notion Notes: `LinkedIn: [N] connections at [Company] — [Name], [Title]. Outreach drafted.`

---

## Rules

- Never read `messages.csv` — skip warmth assessment entirely
- Never generate outreach for zero matches
- If the whole check takes more than a few seconds, something is wrong — stop and move on
