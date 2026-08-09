# Skill: Score Rubric

**Always active.** Apply whenever scoring a role. Every role must be scored before being logged to Notion. Only roles scoring 60+ proceed to resume tailoring.

---

## Scoring Dimensions (100 points total)

### 1. Industry / Vertical Match (20 pts)
| Score | Criteria |
|-------|---------|
| 20 | Consumer tech marketplace, food delivery, grocery/retail, fintech with consumer focus |
| 14 | E-commerce, healthtech, mobility, travel, media/streaming |
| 8 | B2B SaaS with consumer-adjacent product (e.g. SMB payments, HR tools with consumer UX) |
| 0 | Pure B2B, enterprise software, industrial, no consumer product |

### 2. JD Role Signal Density (20 pts)
Count signals from the JD Filter skill's include list — either lifecycle/CRM signals OR growth strategy/analytics signals (see jd-filter.md). Both signal types count equally toward this score.

| Score | Signals found |
|-------|--------------|
| 20 | 5+ distinct signals |
| 14 | 3–4 signals |
| 7 | 1–2 signals |
| 0 | 0 signals (should have been excluded) |

> Note: A role can qualify via lifecycle/CRM signals (Braze, email, lifecycle stages, retention) OR via growth strategy/analytics signals (P&L, experimentation roadmap, commercial analytics, SQL + growth context, cross-functional commercial programs). Both paths are valid and score equally. Roles that mix both paths (e.g. growth with experimentation AND lifecycle component) may count signals from both lists.

### 3. Required Experience Met (15 pts)
| Score | Criteria |
|-------|---------|
| 15 | Years required ≤ the candidate's years in comparable role (4+ years lifecycle/growth) |
| 10 | 1 year gap (e.g. JD requires 5 years, the candidate has 4) |
| 5 | 2 year gap |
| 0 | 3+ year gap or requires domain expertise the candidate doesn't have |

### 4. JD Keywords Present in Profile (15 pts)
| Score | Match rate |
|-------|-----------|
| 15 | >80% of JD's key terms appear in the candidate's profile/skills |
| 10 | 60–80% |
| 6 | 40–60% |
| 0 | <40% |

### 5. Seniority Signals Match (15 pts)
| Score | JD seniority |
|-------|-------------|
| 15 | Senior Specialist, Senior Manager, Lead, Manager — direct match to the candidate's current level |
| 12 | Specialist, Analyst (stretch down but acceptable) |
| 8 | Director, Head of (stretch up — flag but still score) |
| 5 | Associate, Junior (too junior — low priority) |
| 0 | VP, C-level (out of range) |

### 6. Location / Visa Sponsorship (15 pts)
| Score | Criteria |
|-------|---------|
| 15 | UAE role, OR EU role with explicit visa sponsorship for international candidates |
| 10 | EU role with no explicit mention of visa (common in DE/NL — assume possible unless stated otherwise) |
| 5 | EU role with "right to work in EU required" stated — deprioritise but still log |
| 0 | No-relocation role, requires US work auth, or location not accessible |

---

## Decision Thresholds
- **60+ → Proceed** to resume tailoring + Notion logging
- **45–59 → Log only** (To Apply, no resume generated, flag for manual review)
- **<45 → Skip** (add to scanned_history.json, do not log to Notion)

---

## Score Output Format
```
Score: 74/100
  Industry:    16/20  (consumer tech marketplace — food delivery adjacent)
  JD Signals:  20/20  (retention, lifecycle, A/B testing, Braze, cohort — 5 signals)
  Experience:  15/15  (4 years required, the candidate has 4+ in comparable roles)
  Keywords:    10/15  (73% match — missing: LTV modelling, CleverTap)
  Seniority:   8/15   (role is "Manager" — the candidate is at "Sr. Specialist", slight stretch up)
  Location:    5/15   (EU role, no visa mention, "EU work authorisation preferred")

Qualify: YES
Missing keywords to inject: LTV modelling (Critical), CleverTap (High)
Red flags: Visa sponsorship not confirmed
```
