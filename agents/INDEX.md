# Agent Index

## System Variables (auto-resolved)
| Variable | Value | Used in |
|----------|-------|---------|
| `{{DATE}}` | Current date, YYYY-MM-DD | All agents — output filenames, Notion dates |
| `{{COMPANY}}` | Company name | Resume Tailor, Cover Letter, Notion Logger |
| `{{COMPANY_SLUG}}` | Lowercase hyphenated company name (e.g. "delivery-hero") | Resume Tailor |
| `{{TITLE}}` | Exact role title from job posting | All agents |
| `{{ROLE_SLUG}}` | Lowercase hyphenated title slug (e.g. "lifecycle-marketing-manager") | Resume Tailor |
| `{{JOB_URL}}` | Direct URL to job posting | JD Reader, Notion Logger |
| `{{JD_TEXT}}` | Full job description text | Role Scorer, Resume Tailor, Cover Letter Writer |
| `{{JD_SIGNALS}}` | Lifecycle/CRM signals found in JD | Role Scorer, Cover Letter Writer |
| `{{JD_KEYWORDS}}` | Comma-separated keywords from JD | Resume Tailor, Notion Logger |
| `{{MISSING_KEYWORDS}}` | Critical/High keywords absent from profile | Resume Tailor |
| `{{SCORE}}` | Match score /100 | Role Scorer, Notion Logger |
| `{{RESUME_TEXT}}` | Full formatted resume text | Cover Letter Writer, Notion Logger |
| `{{COVER_LETTER_TEXT}}` | Full cover letter text | Notion Logger |
| `{{NOTION_PAGE_ID}}` | Notion page ID for this role | Notion Logger, Gmail Syncer |
| `{{NOTION_PAGE_URL}}` | Full Notion page URL | Interview Prepper |
| `{{CANDIDATES_FILE}}` | Path to working/candidates_{{DATE}}.json | Role Scorer |
| `{{INTERVIEW_TYPE}}` | screening, behavioural, technical, case, or final | Interview Prepper |
| `{{INTERVIEWER_ROLE}}` | Recruiter, Hiring Manager, Senior IC, Panel | Interview Prepper |
| `{{INTERVIEW_PREP_PAGE_URL}}` | Notion URL of the interview prep sub-page (created by Interview Prepper) | Interview Prepper |

---

## Agents

| Agent | File | Invoke When |
|-------|------|-------------|
| Job Discovery | `agents/job-discovery.md` | `/job-search` command — scan all APIs, pre-filter, return candidate list |
| JD Reader | `agents/jd-reader.md` | Need to fetch and parse a full JD from a URL; also called by Job Discovery for ambiguous snippets |
| Role Scorer | `agents/role-scorer.md` | After Job Discovery returns candidates — score each against the 100-pt rubric, keep top 15 |
| Resume Tailor | `agents/resume-tailor.md` | After scoring, for each role with score 60+ — generate tailored 1-page PDF |
| Cover Letter Writer | `agents/cover-letter-writer.md` | After Resume Tailor — write tailored cover letter for the same role |
| Notion Logger | `agents/notion-logger.md` | After Resume Tailor + Cover Letter Writer — log to Notion tracker, set Status = To Apply, Approved? = false |
| Gmail Syncer | `agents/gmail-syncer.md` | `/gmail-sync` command — check inbox for company emails, update Notion statuses |
| Interview Prepper | `agents/interview-prepper.md` | `/interview-prep [notion-url]` command — generate structured prep sheet for a scheduled interview |
| LinkedIn Enricher | `agents/linkedin-enricher.md` | Run once when LinkedIn archive is downloaded — indexes all connections by company, enriches CLAUDE.md, flags recruiter DMs |

---

## Command → Agent Mapping

| Command | Agents invoked (in order) |
|---------|--------------------------|
| `/job-search` | Job Discovery → Role Scorer → Resume Tailor → Cover Letter Writer → Notion Logger |
| `/filling-in` | query_approved.py → Resume Tailor → Cover Letter Writer → Notion Logger |
| `/gmail-sync` | Gmail Syncer |
| `/interview-prep [notion-url]` | Interview Prepper |

---

## Working Files Convention

| File | Created by | Used by |
|------|-----------|---------|
| `working/candidates_{{DATE}}.json` | Job Discovery | Role Scorer |
| `working/shortlist_{{DATE}}.json` | Role Scorer | Resume Tailor |
| `working/jd_{{COMPANY}}_{{SLUG}}.json` | JD Reader | Role Scorer, Resume Tailor |
| `working/notion_failed_{{DATE}}.json` | Notion Logger (on failure) | Manual review |
| `working/gmail_ambiguous_{{DATE}}.json` | Gmail Syncer | Manual review |
| `working/interview_prep_{{COMPANY}}_{{DATE}}.md` | Interview Prepper | User |
| `resumes/gen_{{COMPANY_SLUG}}_{{ROLE_SLUG}}_resume.py` | Resume Tailor | User (re-run if needed) |
| `resumes/{{FIRSTNAME}}-{{LASTNAME}}-{{COMPANY}}-{{ROLE_SLUG}}.pdf` | Resume Tailor | User uploads manually to ATS |
| `scanned_history.json` | Job Discovery | Job Discovery (dedup) |
