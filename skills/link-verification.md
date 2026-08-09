# Skill: Link Verification

**Always active.** Apply whenever a job URL is encountered — before scoring, before logging, before applying.

---

## Rules

1. **Prefer direct company career pages** over aggregators. A URL at `careers.company.com`, `company.greenhouse.io`, or `jobs.lever.co/company` is more reliable than an aggregator link.

2. **Flag these aggregator domains** — they frequently list expired or duplicate postings:
   - startuplist.de
   - talentify.io
   - startup.jobs
   - arbeitnow.com (reliable API but confirm direct URL when applying)
   - jobicy.com
   - remotive.com
   - themuse.com

3. **Verify live before logging.** Before adding a role to Notion, confirm the page loads and contains an active job posting. If using web_fetch returns empty → try Claude in Chrome. If both fail or return 404/403 → mark as dead.

4. **If a link is dead:**
   - If role is already in Notion → set Status = "Link 404" immediately
   - If role hasn't been logged yet → skip it, add to `scanned_history.json` to prevent re-surfacing
   - Do not generate a resume or cover letter for a dead link

5. **Prefer Greenhouse/Lever/Ashby direct links** for application. These platforms have stable URLs and reliable form-filling. If the aggregator URL redirects to one of these → use the ATS URL directly.

---

## Output
```
Link Check: {{URL}}
  Status: LIVE | DEAD | REDIRECT
  Final URL: {{FINAL_URL}} (if redirected)
  Platform: Greenhouse | Lever | Ashby | Workday | LinkedIn | Direct | Aggregator
  Action: Proceed | Skip | Mark Link 404
```
