# Job Search Pipeline — Onboarding Guide

This guide walks you through setting up and using the pipeline from scratch, including a dry run with dummy data so you know what to expect before using real job listings.

Estimated setup time: 30–45 minutes. After that, a full `/job-search` run takes about 15–20 minutes.

---

## Part 1: Prerequisites

You need four things installed before anything else:

**1. Claude Code CLI**
```bash
# Check if already installed
claude --version

# If not, install from:
# https://claude.ai/code
```

**2. Python 3.9+**
```bash
python3 --version
# Must be 3.9 or higher
```

**3. Claude Code CLI or Cowork** (either works — Cowork is the desktop app, Claude Code is the terminal)
- Claude Code: [claude.ai/code](https://claude.ai/code)
- Cowork: available in the Claude desktop app

**4. A Notion account** (free tier is fine)
- Sign up at [notion.so](https://notion.so) if you don't have one

---

## Part 2: Clone and Run Setup

```bash
git clone <repo-url>
cd job-search-pipeline
chmod +x setup.sh
./setup.sh
```

The setup script creates four files from templates:
- `claude-job-profile.json` — your API keys, Notion IDs, personal details
- `CLAUDE.md` — the pipeline's instruction file for Claude Code
- `context/profile.md` — your candidate profile (experience, metrics)
- `context/preferences.md` — your job search preferences

It also creates three empty directories: `working/`, `scripts/`, `resumes/`.

You'll see output like:
```
✓ Copied profile template to claude-job-profile.json
✓ Created CLAUDE.md from template
✓ Created context/profile.md from template
✓ Created context/preferences.md from template
✓ working/ folder ready
✓ scripts/ folder ready
✓ resumes/ folder ready
```

---

## Part 3: Get Your API Keys

You need four API keys. All have free tiers — no payment required to start.

### 3a. Adzuna (primary job source — ~8 countries)

1. Go to [developer.adzuna.com](https://developer.adzuna.com)
2. Click **Sign Up** → create a free account
3. After confirming email, go to **Dashboard** → **Your Apps**
4. Click **Create App** → give it any name (e.g. "job-pipeline")
5. Copy the **App ID** and **App Key**
6. Add to `claude-job-profile.json`:
   ```json
   "apis": {
     "adzuna_app_id": "a1b2c3d4",
     "adzuna_app_key": "e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
   }
   ```

Free tier: 250 requests/day — enough for daily runs.

### 3b. RapidAPI (covers JSearch + Indeed Scraper)

1. Go to [rapidapi.com](https://rapidapi.com) → create a free account
2. Search for **"JSearch"** → click Subscribe → select **Basic (free)** tier
3. Search for **"Indeed Job Search"** → click Subscribe → select **Basic (free)** tier
4. Go to **My Apps** → **default-application** → copy your **API Key**
5. Add to `claude-job-profile.json`:
   ```json
   "apis": {
     "rapidapi_key": "your_rapidapi_key_here"
   }
   ```

Both JSearch and Indeed Scraper use the same RapidAPI key.

### 3c. Notion Internal Integration Token

This is what lets the pipeline write to your Notion tracker. Takes about 2 minutes.

1. Go to [notion.so/profile/integrations](https://notion.so/profile/integrations)
2. Click **New integration**
3. Name it anything (e.g. "Job Search Pipeline")
4. Make sure your workspace is selected
5. Under **Capabilities**, keep the defaults (Read/Update/Insert content)
6. Click **Save**
7. Copy the **Internal Integration Token** — it starts with `secret_`
8. Add to `claude-job-profile.json`:
   ```json
   "apis": {
     "notion_token": "secret_abc123..."
   }
   ```

---

## Part 4: Set Up Notion

### 4a. Create the tracker database

1. Open Notion → create a new page (call it "Job Search" or similar)
2. Inside that page, type `/database` → select **Database - Full page**
3. Name it **"Job Application Tracker"**
4. Add these columns (click the `+` at the top right of the table):

| Column Name | Column Type |
|-------------|------------|
| Role Title | Title (already exists) |
| Company | Text |
| Location | Text |
| Status | Select |
| Match Score | Number |
| Job URL | URL |
| Approved? | Checkbox |
| Keywords | Text |
| Archetypes | Text |
| Date Found | Date |
| Date Applied | Date |
| Notes | Text |

5. For the **Status** column, add these options (in this order):
   - To Apply
   - Applied
   - Confirmation Received
   - Interview Scheduled
   - Round 2
   - Round 3+
   - Offer
   - Rejected
   - Withdrawn
   - Link 404

### 4b. Connect your integration to the database

1. Open your Job Application Tracker database
2. Click the `...` button (top right) → **Connections** → **Add connection**
3. Search for and select the integration you created in Step 3c
4. Confirm the connection

### 4c. Copy your Notion IDs

You need three IDs from Notion:

**Database ID:**
- Open your Job Application Tracker in Notion
- Look at the URL: `https://www.notion.so/yourworkspace/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...`
- The 32-character hex string (before the `?v=`) is your **database ID**
- Add to `claude-job-profile.json` under `notion.database_id`

**Parent Page ID:**
- Go to the page that contains your tracker database
- The 32-character hex string in its URL is your **parent page ID**
- Add under `notion.parent_page_id`

**Data Source ID (optional — for Notion MCP queries):**
- This is visible in the database URL when you're in the database view as a collection ID
- Format: `collection://XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
- Add under `notion.data_source_id` (leave as-is from the template if you can't find it — it's only used by one MCP tool)

---

## Part 5: Fill In Your Profile

Open `context/profile.md` — this is your candidate profile. It has two sections:

### Identity
Replace the placeholder values with your real name, email, phone, LinkedIn URL, etc.

### Work Experience
Write your experience as high-level descriptions — these are context for Claude, not resume copy. Use the tagging system:
- Each accomplishment gets a unique tag: `[A1]`, `[A2]`, `[A3]`... for your current role; `[B1]`, `[B2]`... for your previous role
- Mark priority: `[P1]` = proven, quantified win; `[P2]` = supporting context

Example:
```markdown
**Acme Corp | Growth Marketing Manager** — Jan 2023 – Present
- [A1] [P1] Led subscription lifecycle redesign — rebuilt fragmented onboarding into segmented, trigger-based flows
- [A2] [P1] Ran A/B holdout experiments on incentive sequencing — drove measurable CPA reduction
- [A3] [P2] Built churn prediction model to identify at-risk cohorts 30 days before expected lapse
```

### Resume Metrics Reference

This is the most important section to get right. Add a table row for every `[A1]`, `[B2]` etc. that has a confirmed, verified number:

```markdown
| Tag | Metric | Context |
|-----|--------|---------|
| [A1] | +5pp freemium-to-premium conversion | Grocery cross-sell lifecycle campaigns, Q2 2024 |
| [A2] | 20% CPA reduction | Incentive sequencing A/B test, 3-month run |
```

**Rule:** if the number isn't confirmed and verified, don't add it. The pipeline never fabricates metrics — it only uses what's in this table.

---

## Part 6: Fill In Your Preferences

Open `context/preferences.md`. Key sections to fill in:

**Target Role Archetypes** — adjust the example archetypes to match your background. Delete rows that don't apply.

**Domain Priority** — list your preferred industries in order (e.g. 1. Consumer fintech, 2. Travel tech...)

**Geography** — your current city, where you're open to relocating, visa/relocation needs.

**Deal-breakers** — roles you never want to see (e.g. Sales, B2B SaaS without lifecycle component).

**Recently Applied** — keep this updated after each run to avoid re-applying to the same roles.

---

## Part 7: Add Your Resume Files

Place your base resume PDFs in the project root:
- Your primary resume (CRM/lifecycle-focused version) — e.g. `Your-Name-Lifecycle-Marketing.pdf`
- Your secondary resume (growth/experimentation-focused version) — e.g. `Your-Name-Growth-Retention.pdf`

Then open `context/resume-format.md` and update the "Which Base Resume to Use" section to reference your actual filenames.

PDFs are gitignored so they stay local.

---

## Part 8: Install the Browser Extension

1. Open **Google Chrome** (must be Chrome, not Arc or Firefox)
2. Go to [chromewebstore.google.com/detail/claude-in-chrome](https://chromewebstore.google.com/detail/claude-in-chrome)
3. Click **Add to Chrome**
4. Sign in to the extension with your Anthropic account

---

## Part 9: Dry Run with Dummy Data

Before running a real job search, do this dry run to make sure everything is connected.

### Step 1: Open Claude Code in your project folder

```bash
cd /path/to/job-search-pipeline
claude
```

You should see the Claude Code interface. It will load `CLAUDE.md` automatically.

### Step 2: Test the Notion connection

Type this in Claude Code:
```
Run: python3 scripts/query_approved.py --debug
```

Expected output:
```
[query_approved] database=YOUR_DATABASE_ID
[query_approved] filter: Approved=true · Status=To Apply · Date Found >= 2026-XX-XX
[query_approved] 0 rows matched filter
[]
[query_approved] Done: 0 eligible rows
```

If you see an error about `notion_token`, go back to Part 3c and make sure you added the token to `claude-job-profile.json`.

If you see a `403` error from Notion, go back to Part 4b — the database isn't shared with your integration yet.

### Step 3: Manually create a dummy Notion row

In Notion, open your Job Application Tracker database and create a test row:
- **Role Title:** Test Role
- **Company:** Test Company
- **Status:** To Apply
- **Date Found:** today
- **Approved?:** checked (✓)

### Step 4: Run query_approved again

```
Run: python3 scripts/query_approved.py --debug
```

Now you should see your test row in the output:
```json
[
  {
    "page_id": "...",
    "page_url": "https://notion.so/...",
    "title": "Test Role",
    "company": "Test Company",
    "date_found": "2026-06-23",
    "has_resume": false,
    "has_cover_letter": false
  }
]
[query_approved] Done: 1 eligible rows
  Test Company — Test Role | ✗ no resume | ✗ no CL
```

The Notion connection is working. Delete the test row.

### Step 5: Test the job scanner

Type in Claude Code:
```
Run: python3 job_scanner.py --debug 2>&1 | head -30
```

Expected: You'll see it reading your API keys and starting to scan. It may return 0 results if your search terms are very narrow — that's fine for the dry run.

### Step 6: Run a scoped job search

Instead of the full 15-source scan, test with a narrower query:
```
/job-scope
```

This runs discovery and scoring without generating resumes. It will ask you what to search for — reply with something like:

> "Search for lifecycle marketing manager roles in Berlin, remote EU, or Dubai. Focus on Adzuna only for now. Show me the top 5 results with scores."

Claude Code will run the scanner, score candidates, and show you a shortlist. No resume is generated yet, nothing is written to Notion. This is safe to run repeatedly to tune your preferences.

### Step 7: Approve a result and run /filling-in

If `/job-scope` found any real roles above 60:
1. Run `/job-search` to do the full pipeline for those roles — it creates Notion rows with full JD, resume, and cover letter
2. Open Notion → review the row → check **Approved?**
3. Run `/filling-in` — it will pick up the approved row and confirm resume + cover letter exist

If no roles scored 60+, that's expected for a narrow test run. Broaden your preferences or try `/job-search` which scans all 15 sources.

---

## Part 10: The Normal Workflow

Once setup is complete, this is the rhythm:

```
Monday/Wednesday/Friday:   /job-search
  → Pipeline runs (~15 min), logs up to 15 new Notion rows with Status = "To Apply"
  → You review each row in Notion: read the full JD, check the resume, review the cover letter
  → Check Approved? for roles you want to pursue

Same day or next day:   /filling-in
  → Picks up any approved rows from the last 3 days that still need a resume or cover letter
  → Generates missing content, updates Notion

Apply manually:
  → Open the job URL from Notion
  → Paste the resume and cover letter from the Notion page
  → Submit the application
  → Update Status to "Applied" and set Date Applied in Notion

Every 2-3 days:   /gmail-sync
  → Checks your inbox for responses from applied companies
  → Updates Notion statuses: Interview Scheduled, Rejected, Offer, etc.

When you get an interview:   /interview-prep [notion-url]
  → Pass the Notion page URL for the role
  → Generates structured prep: company research, STAR stories, likely questions, talking points
```

---

## Common Issues

**Scanner returns 0 results**
- Check your API keys in `claude-job-profile.json` — copy-paste them exactly, no leading/trailing spaces
- Run `python3 job_scanner.py --debug` in your terminal and read the output
- Broaden your role search terms in `context/preferences.md`

**query_approved.py fails with 401 or token error**
- Your `notion_token` in `claude-job-profile.json` is wrong or expired
- Regenerate it at [notion.so/profile/integrations](https://www.notion.so/profile/integrations)
- Make sure the token starts with `secret_`

**query_approved.py fails with 404 on the database**
- Your `notion.database_id` is wrong — re-copy it from the Notion URL
- The database ID should be 32 hex characters with no hyphens

**Resume is more than 1 page**
- The pipeline halts automatically and asks you to shorten bullets
- Reply with: "Shorten bullets to fit 1 page — prioritise P1 metrics, cut P2 context"
- Never adjust margins (PDF spec is fixed)

**"Background command failed" in Claude Code**
- This is a Claude Code display artefact for commands that return empty results
- It does NOT mean the scanner crashed — it just found 0 roles
- Run the scanner directly in Terminal to see the actual output

---

## File Reference

| File | What it is | Edit? |
|------|-----------|-------|
| `claude-job-profile.json` | Your API keys, Notion IDs, personal info | Yes — fill this in completely before first run |
| `CLAUDE.md` | Pipeline rules and agent map for Claude Code | Minor tweaks only (company-specific rules) |
| `context/profile.md` | Your experience, verified metrics, skills | Yes — add new wins after each major project |
| `context/preferences.md` | Role targets, geography, recently applied | Yes — update "Recently Applied" after every run |
| `context/infrastructure.md` | Notion schema, workflow rules | No — framework file |
| `context/resume-format.md` | Resume structure, PDF spec, bullet rules | Update the base resume filenames to yours |
| `job_scanner.py` | Multi-source job scanner | No — don't edit unless adding new sources |
| `scripts/query_approved.py` | Notion query for /filling-in | No |
| `agents/` | Step-by-step agent prompts | No — framework files |
| `skills/` | Inline skill prompts | No — framework files |
| `.claude/commands/` | Slash command definitions | No — don't edit |
