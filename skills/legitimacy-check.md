# Skill: Posting Legitimacy Assessment

**Trigger:** Run on every new job posting before scoring or applying. Takes 2 minutes and filters out ghost jobs, fake postings, and roles not worth applying to. Run after the ATS scan — if ATS confirms closed, skip this entirely.

Output: a legitimacy verdict (Proceed / Caution / Skip) with the specific signals found.

---

## What This Skill Catches

1. **Ghost jobs** — postings that exist but the company has no intent to hire (used to build pipelines, collect market data, or satisfy HR process requirements)
2. **Scam postings** — fake roles designed to collect personal data or CVs
3. **Zombie postings** — roles that were filled months ago but never removed from job boards
4. **Misleading roles** — title says "Manager" but the JD describes Specialist work, or vice versa

---

## Legitimacy Signals Checklist

Run through every signal. Count greens and reds.

### Green Flags (each adds confidence)
- [ ] Posted < 30 days ago
- [ ] ATS-hosted (Greenhouse, Lever, Ashby, Workday, SmartRecruiters) — not email-only
- [ ] Named hiring manager or specific team in JD
- [ ] Specific tech stack mentioned (Braze, Amplitude, SQL, etc.)
- [ ] Specific team context: "you'll report to the Head of CRM", "this role is part of the Growth squad"
- [ ] Company LinkedIn page has >100 followers and recent posts (last 30 days)
- [ ] Company headcount on LinkedIn is consistent with the seniority being hired
- [ ] Role has appeared on multiple platforms (company site + LinkedIn + one job board) — consistent across all
- [ ] Salary range stated
- [ ] Application goes to company domain email or ATS (not gmail/yahoo/hotmail)
- [ ] Job ID or requisition number in URL

### Red Flags (each reduces confidence)
- [ ] Posted 90+ days ago with no updates
- [ ] "Apply via email" to a gmail / yahoo / hotmail address
- [ ] Asks for payment, training fee, or equipment deposit
- [ ] Salary range is wildly inconsistent with role level (e.g. "Manager" at €25k or "Specialist" at €150k)
- [ ] JD is vague: no tools, no team context, no specific requirements — just buzzwords
- [ ] JD text matches a different company's posting verbatim (copy-paste ghost)
- [ ] Company has no LinkedIn presence, no website, or a website created recently (check domain age if suspicious)
- [ ] Job title on the posting differs significantly from JD content
- [ ] "Multiple positions available" with no further context — often a CV harvesting post
- [ ] The recruiter's LinkedIn profile was created recently (<6 months) with <50 connections
- [ ] No company name in the posting ("our client…") and recruiter won't disclose it upfront
- [ ] Requests personal financial information, passport copy, or bank details before interview

---

## Verdict Logic

Count signals from the checklist:

```
Greens: [count]
Reds:   [count]

Verdict:
  0 reds, 3+ greens       → ✅ Proceed
  1 red, 2+ greens        → ✅ Proceed (note the flag)
  2 reds, any greens      → ⚠️ Caution — verify before applying
  3+ reds, any greens     → ⚠️ Caution — manual check required
  Any payment/data red    → 🚫 Skip — scam indicator
  90+ days + <2 greens    → 🚫 Skip — ghost posting
  5+ reds                 → 🚫 Skip — too many issues
```

---

## Step-by-Step Workflow

### 1. Check the posting date
- LinkedIn shows time since posting. Note: LinkedIn adds 30-day extensions, so "30 days ago" on LinkedIn may mean 0–30 days actual.
- For ATS-hosted roles: use the `createdAt` / `updated_at` from the ATS scan.

### 2. Check company presence
Run `web_search` for: `[Company name] LinkedIn` and check:
- Employee headcount (LinkedIn company page)
- Recent posts/activity
- Follower count
- Whether the company is real and active

For unknown companies: also check Crunchbase, Companies House (UK), KvK (Netherlands), or similar registry.

### 3. Check JD specificity
A legitimate JD should include:
- At least 2 specific tools (not just "marketing automation platforms")
- A reporting line or team context
- A defined set of responsibilities (not a copy-paste of a generic marketing manager JD)

### 4. Check the recruiter (if visible)
If the posting includes a recruiter name:
- Search LinkedIn for the recruiter
- Check: profile age, connection count, endorsements, activity
- A newly created profile posting senior roles is a red flag

### 5. Cross-reference across platforms
If a role appears on LinkedIn, Indeed, and the company's own site — and the details are consistent across all three — it's more likely to be real. Discrepancies in title, location, or salary across platforms are a flag.

---

## Ghost Job Specific Checks

Ghost jobs are the most common time-waster. Key ghost job indicators:

1. **Long-posted with no closures:** Role has been up 60–90+ days. If the company has no open roles around it, and this one won't close, it's a ghost.
2. **"Always hiring" roles:** Some companies permanently post certain role types as pipeline-builders. Common in consulting, staffing agencies, and fast-scaling ops teams.
3. **No ATS progression:** If you apply and never receive an auto-confirmation email from an ATS, the posting may not be connected to a real hiring workflow.
4. **LinkedIn "Easy Apply" with no ATS:** LinkedIn Easy Apply with no follow-up ATS link is a common ghost pattern — the application goes nowhere trackable.

---

## Output Format

State the result before scoring begins:

```
Legitimacy Check:
  Posted:      18 days ago (Greenhouse API: 2026-05-20)
  Green flags: 5 (ATS-hosted, named team, specific tools, company verified, salary stated)
  Red flags:   0
  Verdict:     ✅ Proceed

  Notes: HelloFresh LinkedIn: 4,200 employees, active posts, HQ Berlin. Role matches headcount stage.
```

Or for a caution case:
```
Legitimacy Check:
  Posted:      94 days ago (LinkedIn — no ATS date available)
  Green flags: 2 (company verified, ATS-hosted)
  Red flags:   2 (90+ days old, no updates, no named hiring manager)
  Verdict:     ⚠️ Caution

  Notes: Role has been live since March. Company LinkedIn shows no other open roles in this function.
         Likely ghost posting or role on hold. Recommend confirming with the poster before applying.
```

---

## Log to Notion

Add legitimacy verdict to Notion Notes field:
```
Legitimacy: ✅ Proceed — 5 green / 0 red [date]
```
Or:
```
Legitimacy: ⚠️ Caution — 94 days old, no named HM [date]
```
