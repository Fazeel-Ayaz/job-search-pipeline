---
description: Interactive first-time setup wizard. Guides the user through resume upload, profile creation, API keys, Notion setup, and a test run — one step at a time.
allowed-tools: Read, Write, Edit, Bash, WebFetch, WebSearch, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-fetch, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-create-database, mcp__eaaf596d-8c3c-4695-93b6-6fb9915a0cdf__notion-create-pages
---

# /setup — Interactive Setup Wizard

You are guiding a new user through the complete first-time setup of this job search pipeline. Work through the phases below in strict order. At each step:
- Give the user ONE clear action to take
- Wait for their response before moving to the next step
- When you receive something (a file, a key, an ID), immediately process it and confirm what you extracted before moving on
- Keep your messages short and practical — no walls of text
- If a step fails, diagnose and fix it before continuing
- Do not skip ahead

---

## PHASE 1 — Collect Your Career Materials

### Step 1.1 — Resume

Say to the user:

> "Let's get you set up. I'll guide you through this one step at a time — just follow along and we'll have everything running by the end.
>
> **First: upload your current resume.**
> Drop it in the chat as a PDF or paste the text. If you have two versions (e.g. one lifecycle-focused, one growth-focused), upload both.
>
> If you don't have a polished resume yet, that's fine — just upload whatever you have. I'll help structure it."

Wait for the user to upload or paste their resume.

When received: Extract and internally note:
- Full name, email, phone, LinkedIn URL, location
- Each role: company name, title, dates, key bullets/accomplishments
- Skills mentioned
- Education
- Side projects (if any)

Say: "Got it — I can see your experience at [list companies in order]. One more thing before I start building your profile."

### Step 1.2 — Achievements not on the resume

Say to the user:

> "**Is there anything not on your resume that should be?**
>
> This could be:
> - A project you shipped recently that isn't documented yet
> - A metric or result that came in after your resume was last updated
> - A side project, tool, or system you built on your own time
> - Anything you'd want to mention in an interview but it's not written down anywhere
>
> If nothing comes to mind, just say 'no' and we'll move on."

Wait for response. Extract any new accomplishments and note them alongside the resume data.

### Step 1.3 — Target roles and geography

Say to the user:

> "**Two quick questions about what you're looking for:**
>
> 1. What kinds of roles are you targeting? (e.g. lifecycle marketing manager, CRM manager, growth marketing, retention — be as specific as you like)
> 2. Where are you based, and where are you open to? (e.g. based in Dubai, open to Berlin/Amsterdam/London, need visa sponsorship)
>
> Answer both in one message."

Wait for response. Note role types and geography preferences.

### Step 1.4 — Deal-breakers

Say to the user:

> "**Anything you never want to see in the results?**
>
> For example: sales roles, B2B-only companies, specific industries, specific geographies, seniority levels below a certain point.
> Just list them quickly — or say 'none' to use the defaults."

Wait for response.

---

## PHASE 2 — Build the Profile Files

Now generate both profile files from everything collected.

### Step 2.1 — Generate context/profile.md

Write `context/profile.md` using the structure in `context/profile.template.md`.

- Fill Identity section with the user's real name, email, phone, LinkedIn, location
- Write each role under Work Experience using the tagging system ([A1], [A2]... for current role; [B1], [B2]... for previous role etc.)
- Tag each accomplishment [P1] or [P2]: P1 if it has a confirmed metric or is a major ownership story, P2 if it's context/supporting detail
- Add any extra achievements from Step 1.2 as new entries with the next available tag
- Build the Resume Metrics Reference table for every P1 entry that has a confirmed number
- Include Skills section

After writing the file, say:

> "I've built your candidate profile. Here's a quick summary of what I captured:
>
> **[Current Company] ([dates]):** [2-3 key P1 entries listed]
> **[Previous Company] ([dates]):** [1-2 key entries listed]
> **Confirmed metrics for resume use:** [list tag + metric]
>
> Does this look right? Anything I got wrong, missed, or should strengthen? Say 'looks good' to continue, or tell me what to fix."

Wait for confirmation or corrections. Apply any fixes before continuing.

### Step 2.2 — Generate context/preferences.md

Write `context/preferences.md` using the structure in `context/preferences.template.md`.

Populate from:
- Target role archetypes from Step 1.3
- Geography from Step 1.3
- Deal-breakers from Step 1.4
- Leave Recently Applied empty (will populate after first /job-search run)

Say: "Preferences file created. One more file to generate, then we move to API keys."

### Step 2.3 — Generate context/personal-questions.md

Write `context/personal-questions.md`. This file contains first-person answers to the classic personal/screening interview questions. The Interview Prepper loads it for every screening round — without it, that round will fail.

Use everything collected in Phase 1 to populate the answers. Keep each answer grounded in real experience from the profile — nothing invented.

Structure the file with these four parts:

**Part 1 — Identity & Motivation**
- "Tell me about yourself" — 3-4 sentence career narrative: what connects the roles, what the pattern of impact is, what they're moving toward
- "Why should we hire you?" — one proof point that maps directly to the kind of role they're targeting
- "Why are you leaving your current role?" — honest, forward-looking, company-agnostic
- "Where do you see yourself in 5 years?" — directional but concrete; scope they want, not just a title

**Part 2 — Strengths & Work Style**
- "What's your greatest strength?" — one thing with a specific proof point from their work history
- "What's your greatest weakness?" — a real one, not a thinly disguised strength; must include what they're actively doing about it
- "Describe how you work best" — environment, collaboration style, how they handle ambiguity

**Part 3 — Logistics**
- "Are you open to relocation?" — use `personal.relocation_targets` from the profile
- "What are your salary expectations?" — soft deflect: "Open to market rate — happy to discuss once I know more about the scope"
- "What's your notice period / when can you start?"
- "Do you have the right to work in [country]?" — use `personal.work_authorization` and `personal.visa_sponsorship_required`

Add a header at the top of the file:
```
# Personal Questions Library
First-person answers to classic personal/screening interview questions.
Company-agnostic — refine these over time as real interviews come in.
Source: context/profile.md and context/preferences.md
```

After writing the file, say:

> "Done — I've written your personal questions file with starter answers based on your profile. These will get sharper as you use them in real interviews.
>
> Moving on to API keys now."

---

## PHASE 3 — API Keys

### Step 3.1 — Adzuna (main job source)

Say to the user:

> "**Get your Adzuna API key** — this is the main job source (covers UK, US, DE, NL, AU and more).
>
> 1. Go to **developer.adzuna.com**
> 2. Sign up for a free account
> 3. Confirm your email
> 4. Go to **Dashboard → Your Apps → Create App** (name it anything)
> 5. Copy the **App ID** (short, looks like `a1b2c3d4`) and **App Key** (long string)
>
> Paste both here when you have them."

Wait for the user to paste the App ID and App Key.

When received: Update `claude-job-profile.json` — set `apis.adzuna_app_id` and `apis.adzuna_app_key`.

Say: "Adzuna saved. Next one."

### Step 3.2 — RapidAPI

Say to the user:

> "**Get your RapidAPI key** — this covers JSearch and Indeed job listings.
>
> 1. Go to **rapidapi.com** → sign up free
> 2. Search for **JSearch** → click Subscribe → choose **Basic (free)** tier
> 3. Search for **Indeed Job Search** → click Subscribe → choose **Basic (free)** tier
> 4. Go to **My Apps → default-application** → copy your **API Key**
>
> Both APIs use the same key. Paste it here."

Wait for the key.

When received: Update `claude-job-profile.json` — set `apis.rapidapi_key`.

Say: "RapidAPI saved. Now for Notion — this is the most important one, and takes a few more steps. I'll walk you through it."

---

## PHASE 4 — Notion Setup

### Step 4.1 — Create the Notion database

Say to the user:

> "**Set up your Notion tracker:**
>
> 1. Open Notion → create a new page (call it "Job Search" or similar)
> 2. Inside that page, type `/database` → select **Database - Full page**
> 3. Name it **Job Application Tracker**
> 4. Add these columns (click `+` at the top right of the table):
>
> | Column | Type |
> |--------|------|
> | Company | Text |
> | Location | Text |
> | Status | Select |
> | Match Score | Number |
> | Job URL | URL |
> | Approved? | Checkbox |
> | Keywords | Text |
> | Archetypes | Text |
> | Date Found | Date |
> | Date Applied | Date |
> | Notes | Text |
>
> 5. For the **Status** column, add these options in this order:
>    To Apply, Applied, Confirmation Received, Interview Scheduled, Round 2, Round 3+, Offer, Rejected, Withdrawn, Link 404
>
> Tell me when the database is created."

Wait for confirmation.

### Step 4.2 — Create the Notion integration

Say to the user:

> "**Create your Notion integration** (this is what lets me write to your tracker):
>
> 1. Go to **notion.so/profile/integrations**
> 2. Click **New integration**
> 3. Name it **Job Search Pipeline** (or anything)
> 4. Make sure your workspace is selected
> 5. Click **Save**
> 6. Copy the **Internal Integration Token** — it starts with `secret_`
>
> Paste the token here."

Wait for the token.

When received: Update `claude-job-profile.json` — set `apis.notion_token`.

Say: "Token saved. Now connect it to your database."

### Step 4.3 — Connect integration to database

Say to the user:

> "**Share your tracker database with the integration:**
>
> 1. Open your **Job Application Tracker** database in Notion
> 2. Click `...` (top right) → **Connections** → **Add connection**
> 3. Find and select **Job Search Pipeline** (the integration you just created)
> 4. Confirm
>
> Done? Tell me yes."

Wait for confirmation.

### Step 4.4 — Get the Notion IDs

Say to the user:

> "**Copy your Notion IDs:**
>
> **Database ID:**
> - Open your Job Application Tracker in Notion
> - Look at the URL in your browser: `https://www.notion.so/yourworkspace/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...`
> - The 32-character string before `?v=` is your database ID
>
> **Parent Page ID:**
> - Go to the page that *contains* your tracker (the "Job Search" page you created)
> - Its URL has a similar 32-character string at the end — that's the parent page ID
>
> Paste both IDs here. Format: `database: [id]` and `parent: [id]`"

Wait for both IDs.

When received: Update `claude-job-profile.json`:
- Set `notion.database_id`
- Set `notion.parent_page_id`
- Set `notion.tracker_database_url` to `https://www.notion.so/[database_id]`
- Set `notion.job_search_page_url` to `https://www.notion.so/[parent_page_id]`

### Step 4.5 — Test the Notion connection

Run:
```bash
python3 scripts/query_approved.py --debug
```

If it returns `[]` with no errors: connection is working.

If it returns a 401 error: the token is wrong. Ask the user to re-paste it.
If it returns a 403 or 404 error: the database isn't shared with the integration. Repeat Step 4.3.
If it returns a config error: the database_id is wrong. Repeat Step 4.4.

When the test passes, say: "Notion is connected and working. ✓"

---

## PHASE 5 — LinkedIn Archive (Optional but Recommended)

Say to the user:

> "**Optional: LinkedIn data export**
>
> If you upload your LinkedIn connections archive, I can automatically check whether you have 1st-degree connections at any company you're applying to — and draft outreach messages for them. This runs silently on every job scoring 45+.
>
> To request your archive:
> 1. Go to LinkedIn → Me → Settings & Privacy → Data Privacy → Get a copy of your data
> 2. Select **Connections** (just this one — you don't need the full archive)
> 3. Click **Request archive** — LinkedIn usually emails it within 10 minutes
>
> Once downloaded, upload the `Connections.csv` file here.
>
> Or say **'skip'** to move on — you can do this later."

Wait for the upload or 'skip'.

If uploaded: Run `agents/linkedin-enricher.md` to index connections and save to `working/linkedin_connections.json`.
If skipped: Note it and continue.

---

## PHASE 6 — Upload Resume PDFs

Say to the user:

> "**Upload your resume PDF(s)**
>
> The pipeline generates tailored resumes by adapting a base template. Upload your current best resume(s) as PDF(s) so the pipeline can use them as the formatting baseline.
>
> - If you have one version: upload it
> - If you have two versions (e.g. one for CRM/lifecycle roles, one for growth/experimentation roles): upload both
>
> Name them clearly — e.g. `Your-Name-Lifecycle.pdf` and `Your-Name-Growth.pdf`
>
> Drop them here and I'll save them to the project root."

Wait for upload(s).

When received: Save each PDF to the project root. Then open `context/resume-format.md` and update the "Which Base Resume to Use" section to reference the actual filenames.

Say: "Resume files saved and referenced in the format rules."

---

## PHASE 7 — Fill In Personal Details

Update `claude-job-profile.json`:
- `personal.name`, `personal.email`, `personal.phone`, `personal.location`, `personal.linkedin`
- `personal.willing_to_relocate`, `personal.relocation_targets`, `personal.visa_sponsorship_required`
- `gmail.address`
- `target_roles` (from Step 1.3)

---

## PHASE 8 — Dry Run

Say to the user:

> "**Setup is complete. Let's do a quick test to make sure everything works end to end.**
>
> I'm going to create a dummy row in your Notion tracker, verify the query script picks it up, then delete it.
>
> Creating test row now..."

1. Use the Notion MCP to create a test row in the database:
   - Role Title: "Test Role"
   - Company: "Test Company"
   - Status: "To Apply"
   - Date Found: today's date
   - Approved?: true

2. Run `python3 scripts/query_approved.py --debug`

3. Confirm the test row appears in the JSON output.

4. Delete the test row via Notion.

Say:

> "✓ Test passed — the pipeline found your test row and the Notion connection is fully working.
>
> Now try a real scan. Run: `/job-scope`
>
> This does discovery and scoring without generating any resumes — it's safe to run to see what kinds of roles show up. Tell me what to search for (target role + location) and I'll kick it off."

---

## PHASE 9 — First Real Run

When the user runs `/job-scope` and gets results back:

Say:

> "Here's what came back. For each role scoring 60+, I'll generate a tailored resume and cover letter and log it to Notion. Want me to proceed with the full `/job-search` pipeline for these? Say yes, or tell me which ones to include/exclude."

Wait for confirmation, then let them proceed to `/job-search` naturally.

---

## Setup Complete

When all phases are done, say:

> "You're fully set up. Here's your command reference:
>
> | Command | When to run |
> |---------|-------------|
> | `/job-search` | Every 2-3 days — discovers, scores, tailors, logs to Notion |
> | `/job-scope` | When you want to preview results before committing to full tailoring |
> | `/filling-in` | After approving rows in Notion — generates any missing resume/CL |
> | `/gmail-sync` | Every few days — pulls interview invites and rejections into Notion |
> | `/interview-prep [notion-url]` | When an interview is scheduled — full structured prep |
>
> **Normal rhythm:**
> Run `/job-search` → review in Notion → check Approved? → run `/filling-in` → apply manually → run `/gmail-sync`
>
> **One optional extra — Gmail sync:**
> `/gmail-sync` needs the Gmail MCP connected to work. In Cowork: go to Settings → Plugins and install the Gmail plugin. In Claude Code: add the Gmail MCP server to your `.claude/settings.json`. Once connected, `/gmail-sync` will pull interview invites and rejections directly into your Notion tracker.
>
> Ready to go. Run `/job-search` whenever you're ready for your first full scan."
