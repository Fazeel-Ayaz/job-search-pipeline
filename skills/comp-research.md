# Skill: Compensation Research

**Trigger:** Run after a role scores 60+ and before the resume is generated. Never skip. Output must appear in the Notion Notes field and be stated to the user before applying.

The goal is to walk into every application knowing the market rate — so the user is never anchored low in a negotiation and never wastes time on a role that's structurally underpaid.

---

## Step 1: Extract Role Parameters

From the JD, extract:
- **Job title** (exact string from the posting)
- **Seniority level** (Senior, Lead, Manager, etc.)
- **Location** (city + country; remote vs hybrid vs onsite)
- **Industry / company type** (startup, scale-up, corporate, marketplace, fintech, etc.)
- **Company size** (headcount or stage if available)
- **Function** (CRM, Growth, Lifecycle, Loyalty, Performance)

---

## Step 2: Run Market Research

Search the following sources with the role title + location. Use `web_search` or `web_fetch`:

| Source | What to look up |
|--------|----------------|
| Glassdoor | `site:glassdoor.com "[role title]" "[city]" salary` |
| LinkedIn Salary | `site:linkedin.com/salary "[role title]" "[location]"` |
| Levels.fyi | Only if tech company — check for marketing comp benchmarks |
| Payscale | `site:payscale.com "[role title]" salary "[country]"` |
| Indeed Salaries | `site:indeed.com salaries "[role title]" "[location]"` |
| EU-specific | For Europe: check Gehalt.de (Germany), Glassdoor.nl (Netherlands), Emolument.com |
| UAE-specific | For UAE: Bayt salary reports, Glassdoor AE, GulfTalent salary guide |

If the JD includes a salary range: note it, then benchmark whether it's at, above, or below market.

---

## Step 3: Build the Comp Model

Produce a structured comp estimate:

```
Role:        [Title] @ [Company], [Location]
─────────────────────────────────────────────
Base salary:     [Low] – [High] [currency/year]
Bonus (typical): [X]% of base (estimated [Low]–[High])
Equity:          [None / ESOP / RSU — note if tech scale-up]
Total comp:      [Low] – [High] [currency/year] estimated

Market position:
  P25 (floor):   [amount]
  P50 (median):  [amount]
  P75 (ceiling): [amount]

Posted range (if stated): [range from JD, or "not stated"]
JD range vs market: [At market / Below market / Above market / Not stated]

Negotiation anchor:  [P60–P75 of the market range — this is the opening ask]
Walk-away floor:     [P40 — do not accept below this]
```

---

## Step 4: Flag Comp Red Flags

Raise a flag (and note in Notion) if:
- Stated salary is >15% below market P50 for the role and location
- Role is "Manager" or "Lead" title but comp is Specialist-level
- Startup equity not mentioned for a Series B+ company (implies weak offer)
- Contract/freelance framing at a full-time ask (high scope, no benefits)
- "Competitive salary" with no range stated — add to Questions for Recruiter list

---

## Step 5: Prepare Salary Negotiation Talking Points

For every role that proceeds to application, prepare 2–3 lines the user can use if asked "what are your salary expectations?":

```
Negotiation script (adapt to context):
"Based on my research for [role] in [location], and given 5 years of experience with a clear track record of driving [X, Y, Z outcomes], I'm targeting [P60–P75 anchor]. That said, I'm open to discussing the full package — base, bonus structure, and any equity component — to understand the total value."
```

---

## Step 6: Log to Notion

Add to the `Notes` field of the Notion entry:

```
Comp research ([date]):
  Market range: [Low]–[High] [currency]
  Posted range: [stated range or "not stated"]
  Market position: [at / below / above]
  Negotiation anchor: [amount]
  Walk-away floor: [amount]
```

---

## Location-Specific Notes

**UAE (Dubai):**
- No income tax — gross = net
- Benchmark against MENA and global roles; local UAE market often lags EU/UK by 15–25%
- Factor in housing allowance, flight allowance, health insurance if offered separately
- EUR/USD equivalent: compute at spot rate

**Netherlands:**
- 30% ruling applies if relocating (reduces taxable base for 5 years) — factor into net take-home
- Holiday allowance: 8% of gross salary added annually
- Common to negotiate based on monthly gross, not annual

**Germany:**
- Social contributions ~20% on top of income tax — effective tax rate 35–45%
- Salary negotiations typically in annual gross
- Job titles vary widely — "Lead" in a German company may mean IC with mentoring scope, not people manager

**UK:**
- NI + income tax ~33–42% effective rate above £50k
- London premium exists: add 10–15% vs rest of UK
- Bonus culture varies: fintech/tech higher, traditional corporate lower
