# Job Search Pipeline

An automated job search, resume tailoring, and application tracking system built on Claude Code and Cowork.

## What it does

1. **Discovers** relevant roles across 15 job sources (Adzuna, Reed, Greenhouse, Lever, SmartRecruiters, Remotive, Jobicy, Arbeitnow, Landing.jobs, Relocate.me, JSearch, Indeed, The Muse, aijobs.net, Google Jobs via Serper)
2. **Scores** each role against your profile using a 100-point rubric — keeps only roles scoring 60+
3. **Tailors** a 1-page ATS-safe resume and cover letter for each qualifying role
4. **Logs** everything to a Notion tracker: company, role, score, full JD, resume, cover letter, comp research, archetypes, status
5. **Awaits approval** — you review in Notion, check `Approved?` for roles you want to pursue
6. **Fills in** resumes/cover letters for approved rows you haven't acted on yet
7. **Tracks** email responses and updates Notion status through the interview pipeline

## Requirements

- [Claude Code CLI](https://claude.ai/code) or [Cowork](https://claude.ai) (desktop app)
- A Notion workspace with the job tracker database (schema below)
- API keys: Adzuna, RapidAPI (JSearch + Indeed), Notion integration token

## Setup

```bash
git clone <this-repo>
cd job-search-pipeline
chmod +x setup.sh
./setup.sh
```

The setup script:
- Copies `claude-job-profile.template.json` → `claude-job-profile.json` (project root, gitignored)
- Copies `CLAUDE.template.md` → `CLAUDE.md` (gitignored)
- Copies `context/profile.template.md` → `context/profile.md` (gitignored)
- Copies `context/preferences.template.md` → `context/preferences.md` (gitignored)
- Creates `working/`, `scripts/`, and `resumes/` directories

Then run `/setup` inside Claude Code or Cowork for a guided interactive walkthrough of the rest.

**After running setup.sh, you must fill in three files before running any commands:**

### 1. `claude-job-profile.json`

Fill in your personal details, API keys, and Notion IDs. The file structure is documented in `claude-job-profile.template.json`.

**Getting API keys:**

| Key | Where to get it | Cost |
|-----|----------------|------|
| `apis.adzuna_app_id` + `apis.adzuna_app_key` | [developer.adzuna.com](https://developer.adzuna.com) | Free, 250 req/day |
| `apis.reed_api_key` | [reed.co.uk/developers](https://www.reed.co.uk/developers) | Free |
| `apis.rapidapi_key` | [rapidapi.com](https://rapidapi.com) — subscribe to JSearch and Indeed Scraper | Free tier |
| `apis.notion_token` | [notion.so/profile/integrations](https://www.notion.so/profile/integrations) — create Internal Integration | Free |

### 2. `context/profile.md`

Your candidate profile — work experience (with accomplishment tags), verified metrics for resume generation, and skills. This is the source of truth for every resume generated. See `context/profile.template.md` for the structure.

> The metrics reference section is private (gitignored). Never fabricate or round up numbers — only include confirmed, verified metrics here.

### 3. `context/preferences.md`

Your job search preferences — target roles, domain priorities, JD signals to include/exclude, geography, deal-breakers, and recently applied list. See `context/preferences.template.md` for the structure.

## Notion Setup

### Database schema

Create a Notion database with these columns:

| Column | Type | Notes |
|--------|------|-------|
| Role Title | Title | |
| Company | Text | |
| Location | Text | |
| Status | Select | To Apply → Applied → Confirmation Received → Interview Scheduled → Round 2 → Round 3+ → Offer / Rejected / Withdrawn / Link 404 |
| Match Score | Number | 0–100 |
| Job URL | URL | |
| Approved? | Checkbox | **Only apply to rows where this is checked** |
| Resume | File | Tailored resume PDF (optional — text version lives in page body) |
| Cover Letter | File | Cover letter PDF (optional) |
| Keywords | Text | JD keywords injected into tailored resume |
| Archetypes | Text | Primary + secondary resume archetype detected for this role |
| Date Found | Date | |
| Date Applied | Date | |
| Last Updated | Last Edited Time | Auto |
| Notes | Text | Match rationale, comp range, ATS info, flags |

### Connect your Notion integration

1. Create an Internal Integration at [notion.so/profile/integrations](https://www.notion.so/profile/integrations)
2. Copy the `secret_...` token into `claude-job-profile.json` under `apis.notion_token`
3. Open your Notion database, click `...` (top right) → **Connections** → **Add connection** → select your integration
4. Copy the database ID from the database URL into `claude-job-profile.json` under `notion.database_id`
   - The URL looks like: `https://www.notion.so/workspace/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...`
   - The 32-character hex string is the database ID

## Context Modules

The pipeline uses scoped context loading — agents only read the files they need. This keeps context windows lean.

| File | Purpose | Gitignored? |
|------|---------|------------|
| `context/profile.md` | Your experience, metrics, skills | Yes — private |
| `context/preferences.md` | Target roles, geography, deal-breakers, recently applied | Yes — private |
| `context/resume-format.md` | Resume structure, XYZ bullet rules, PDF spec | No — framework |
| `context/infrastructure.md` | Notion schema, storage rules, Gmail status mapping | No — framework |

## Commands

Open Claude Code in this folder (`claude`), then use these commands:

| Command | What it does |
|---------|-------------|
| `/job-search` | Full pipeline: discover → score → tailor → log. Scans 15 sources, keeps top 15 roles scoring 60+. Stops at "To Apply" status — waits for your Notion approval before anything is submitted. |
| `/job-scope` | Quick scan without resume generation: find and score roles, show you the top candidates, ask which ones to proceed with. Use when you want to review the shortlist before committing to full tailoring. |
| `/filling-in` | For Notion rows you've already approved (`Approved? = true`, `Status = To Apply`, found in the last 3 days) that are missing a resume or cover letter. Runs resume + cover letter generation for those gaps. |
| `/gmail-sync` | Check Gmail for responses from applied companies and update Notion statuses accordingly. |
| `/interview-prep [notion-url]` | Structured interview prep for a scheduled interview. Pass the Notion page URL for the role. |

## Typical Workflow

```
1. /job-search          → pipeline runs, logs up to 15 rows in Notion with Status = "To Apply"
2. Review in Notion     → read each JD, resume, and cover letter; check Approved? for roles you want
3. /filling-in          → generates missing resume/CL for any approved rows that need it
4. Apply manually       → open the ATS link, copy resume + cover letter from Notion, submit
5. Update Notion        → set Status = "Applied" and Date Applied yourself after submitting
6. /gmail-sync          → run every few days to pull in interview invites and rejections
7. /interview-prep      → when an interview is scheduled, pass the Notion URL for structured prep
```

## File Structure

```
.
├── CLAUDE.template.md          # Claude Code context template (copy to CLAUDE.md)
├── claude-job-profile.template.json  # Profile template (copy to claude-job-profile.json)
├── setup.sh                    # One-time setup script
├── README.md                   # This file
├── job_scanner.py              # Multi-source job scanner (reads from claude-job-profile.json)
├── portals.yml                 # Portal configuration for Greenhouse/Lever/SmartRecruiters
│
├── context/
│   ├── profile.template.md     # Candidate profile template → copy to profile.md
│   ├── preferences.template.md # Preferences template → copy to preferences.md
│   ├── resume-format.md        # Resume structure and PDF spec
│   └── infrastructure.md       # Notion schema and workflow rules
│
├── agents/                     # Agent prompt templates
│   ├── INDEX.md                # Variable reference for all agents
│   ├── job-discovery.md
│   ├── jd-reader.md
│   ├── role-scorer.md
│   ├── resume-tailor.md
│   ├── cover-letter-writer.md
│   ├── notion-logger.md
│   ├── gmail-syncer.md
│   ├── interview-prepper.md
│   └── linkedin-enricher.md
│
├── skills/                     # Inline skill prompts (applied at specific pipeline steps)
│   ├── jd-filter.md
│   ├── ats-scanner.md
│   ├── legitimacy-check.md
│   ├── score-rubric.md
│   ├── archetypes.md
│   ├── comp-research.md
│   ├── resume-rules.md
│   ├── seniority-framing.md
│   ├── cover-letter.md
│   ├── link-verification.md
│   ├── linkedin-connections.md
│   └── star-library.md
│
├── scripts/
│   └── query_approved.py       # Notion REST API query for /filling-in
│
│   # These are gitignored — create from templates:
├── CLAUDE.md                   # Your filled-in Claude Code context
├── claude-job-profile.json     # Your API keys, Notion IDs, preferences
├── context/profile.md          # Your private candidate profile
├── context/preferences.md      # Your private job search preferences
├── working/                    # Intermediate outputs (candidate lists, shortlists)
└── resumes/                    # Temp PDFs (deleted after submission)
```

## How resume tailoring works

- Reads your experience from `context/profile.md`
- Detects the primary and secondary archetype for the role (e.g. "Retention Builder + Lifecycle Architect")
- Picks the right base template (Lifecycle vs Growth/Retention) based on archetype
- Rewrites bullets using Google XYZ formula, injecting JD keywords without fabricating metrics
- Generates a clean 1-page ATS-safe PDF using reportlab
- Stores full resume + cover letter text in the Notion page body
- Logs comp research (market range + negotiation anchor) to Notion Notes
- PDF is generated on-demand for ATS upload, then deleted

## Pipeline rules

Key rules that the pipeline enforces automatically:

- **Never apply without `Approved? = true`** — you always review in Notion first
- **Score ≥ 60 to proceed** — roles below threshold are dropped, never tailored
- **No fabricated metrics** — every number comes from your verified profile metrics only
- **1-page resumes only** — pypdf verifies length; generation halts if > 1 page
- **Full JD logged** — every Notion page body contains the complete, unabridged JD text
- **ATS scan before scoring** — dead postings are marked "Link 404" immediately
- **Ghost job check** — postings 90+ days old without ATS confirmation are flagged
- **Applications are always manual** — the pipeline never submits on your behalf

## Credits

Built with [Claude Code](https://claude.ai/code) / [Cowork](https://claude.ai) + [Notion MCP](https://notion.so)
