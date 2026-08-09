# Skill: Resume Rules

**Always active.** Apply to every resume and cover letter generated in this pipeline. These rules are non-negotiable and override any default formatting behaviour.

---

## Step 0: Archetype Detection (runs before everything else)

Before keyword analysis, before writing a single bullet, before choosing a base template:
1. Load `skills/archetypes.md`
2. Run the detection workflow against the JD
3. Output the archetype call (primary + secondary + framing sentence)
4. Apply the archetype's summary angle, lead experience order, and bracket tags
5. Then proceed to keyword injection (Step 1 below)

The archetype system overrides the binary base template selection below. Use the primary archetype's framing to set which experience leads — the base template just controls layout.

---

## Content Rules

1. **No em dashes.** Never use `—` anywhere. Use `:`, `;`, or a comma instead.
2. **Talabat = Delivery Hero.** Always write "Talabat (Delivery Hero)". Never "DoorDash Group". Never "Delivery Hero Group". Never just "Talabat". Note: Wolt is part of DoorDash, not Delivery Hero — never conflate them.
3. **Stats from profile only.** Use only metrics from the Candidate Profile in CLAUDE.md. Never fabricate, estimate, or round up numbers.
4. **Exactly 1 page.** Verify with pypdf before considering the resume complete. If > 1 page, cut content — never adjust margins or font size below spec.

---

## ATS Parsability Rules

These ensure the resume is readable by every major ATS (Greenhouse, Lever, Workday, Ashby, Rippling):

1. **Single-column layout only.** No tables, text boxes, columns, or multi-panel layouts. ATS parsers read left-to-right, top-to-bottom linearly — anything else scrambles the output.
2. **No graphics, icons, charts, or unusual symbols.** Standard bullet characters (●) are fine. Decorative dividers, profile photos, rating bars, or skill meters are not.
3. **Standard section headings only.** Use: Summary, Professional Experience, Side Projects, Education, Additional Skills. Do not invent unconventional headings.
4. **Fonts and encoding.** Helvetica only (in PDF generation). No ligatures or special Unicode characters that may not survive ATS parsing.
5. **No headers or footers** containing critical information — ATS systems often skip them entirely.

---

## Keyword Integration Rules

1. **Analyse the JD for core hard skills, tools, and methodologies** before writing a single bullet. Build a keyword list: required tools (Braze, Amplitude, SQL), methodologies (A/B testing, incrementality, cohort analysis), and role-specific language (lifecycle stages, channel names).
2. **Inject keywords naturally into the Z clause** of each XYZ bullet — never bolted on at the end, never in a keyword dump. If the JD says "always-on triggered programmes", write "built always-on triggered programmes via Braze" not "managed CRM (always-on, triggered, Braze)".
3. **Mirror the JD's exact phrasing where possible.** If the JD says "retention marketing" not "user retention", use "retention marketing". ATS keyword matching is often exact-string, not semantic.
4. **Every Critical and High missing keyword** from the ATS audit (Resume Tailor agent Step 1) must appear somewhere in the resume — either in a bullet or in the Additional Skills row. Medium keywords: inject if it fits naturally, skip if it doesn't.
5. **The Summary must contain the role's 2-3 most important keywords** in the first sentence. ATS systems weight the top of the document more heavily.

---

## XYZ Bullet Format (apply to every experience bullet)

**Formula:** "Accomplished [X] as measured by [Y] by doing [Z]"

The critical rule: **lead with the result, not the action.** The outcome (X) comes first. The metric (Y) proves it. The tool/tactic/method (Z) explains how — and this is where JD keywords are injected naturally.

| Part | What it is | Example |
|------|-----------|---------|
| **X** — Outcome | Strong action verb + what changed | "Reduced Customer Acquisition Cost" |
| **Y** — Measure | Hard number, %, currency, scope, team size | "by 25% across 8 MENA markets" |
| **Z** — Method | Specific lever, tool, framework, tactic | "by restructuring Braze campaign logic and deploying holdout-group experimentation" |

**The order matters. Wrong order = incomplete sentence that fails ATS and reads weak:**

| ❌ Wrong order (action first) | ✅ Correct order (outcome first) |
|------------------------------|----------------------------------|
| "Managed a $50k monthly ad budget on Meta and Google Ads, which resulted in a 25% reduction in CAC over six months." | "Reduced Customer Acquisition Cost by 25% across regional paid channels by restructuring Meta and Google Ads campaign architecture and deploying automated bidding strategies." |
| "Worked on the company blog and improved organic search rankings." | "Boosted organic traffic by 40% within 4 months by executing a technical SEO audit and deploying a programmatic internal linking framework." |
| "Ran A/B tests to improve cost efficiency up to 20%." | "Improved cost per incremental GMV by 20% by designing a holdout-group experimentation framework for incentive architecture — reducing contamination 4x." |

**Completeness rule — a bullet is only finished when it has all three parts:**
- Missing Z = incomplete ("Reduced churn by 7%" — how? what did you do?)
- Missing Y = vague ("Built a churn model that reduced churn" — by how much?)
- Missing X or wrong order = weak ("Managed lifecycle campaigns via Braze" — so what happened?)

**Rules:**
1. **Lead with the outcome verb.** Never start with "By doing X…", "Responsible for…", "Worked on…", "Helped with…"
2. **Past tense for prior roles, present tense for current role.** Never mix within a role block.
3. **Every bullet must have a number.** If no hard metric exists: quantify scope (8 markets, 4 verticals, 2M users, 40 events, 100+ properties, EUR 75k).
4. **Never repeat action verbs within the same role block.** Rotate: Reduced, Drove, Built, Designed, Led, Launched, Scaled, Deployed, Orchestrated, Re-engineered, Integrated, Improved, Increased, Co-developed, Analysed, Forecasted, Partnered, Owned.
5. **Inject JD keywords naturally into the Z clause** — never bolted on at the end as a list. If the JD says "always-on triggered programmes", write "by building always-on triggered programmes via Braze" not "managed CRM (always-on, triggered, Braze)".
6. **No hedging.** Cut "helped", "supported", "contributed to", "assisted with", "up to X%". Own the number or own the floor.
7. **No prose intros inside bullets.** Context belongs in the italic tagline under the role title — bullets carry only proof.

**Good vs bad examples (the candidate's actual bullets):**

| ❌ Weak / incomplete | ✅ XYZ — outcome first, all three parts |
|---|---|
| "Worked on CRM campaigns across email and push" | "Drove **7% GMV uplift per user** and **3% CVR uplift** across 8 MENA markets by building always-on triggered lifecycle programmes via Braze (Email, Push, In-App, SMS)" |
| "Helped reduce churn through behavioural targeting" | "Reduced churn by **7%** and grew incremental GMV by **11%** by building a behavioural churn prediction model to identify at-risk cohorts and deploy precision-timed win-back programmes" |
| "Contributed to tPro membership growth" | "Increased freemium-to-premium conversion by **+5pp** for tPro by designing cross-sell lifecycle campaigns into the Grocery ordering journey" |
| "Ran A/B tests to improve cost efficiency up to 20%" | "Improved cost per incremental GMV by **20%** by designing a holdout-group experimentation framework for incentive architecture — reducing contamination 4x vs prior approach" |
| "Liaised with data team on experimentation frameworks" | "Increased reactivation efficiency by **24%** by building a behavioural prediction model targeting lapsed-user cohorts with precision-timed incentive offers" |

**Bracket tags:**
Wrap each bullet's category in `[Bold Bracket Tags]` to group by theme. Tags must match JD language where possible:
- `[Lifecycle Strategy]`, `[Experimentation]`, `[CRM & Automation]`, `[Cross-Functional]`, `[Data & Modelling]`

---

## Structure

Use standard, unambiguous headings in this exact order:

1. **Name** — large bold, top center-left
2. **Contact line** — [FROM_PROFILE: personal.location] | {{YOUR_PHONE}} | {{YOUR_EMAIL}} | {{YOUR_LINKEDIN_URL}} | {{YOUR_GITHUB_URL}}
3. **Summary** — 2–3 lines, tailored to the role. Must contain the top 2-3 JD keywords in the first sentence. Use AARRR/lifecycle/CRM language from the JD. No generic openers ("results-driven marketer").
4. **Professional Experience** — reverse chronological
   - Company | Role Title (bold) + date right-aligned
   - Italic tagline/context line under the title (carries role context so bullets carry only proof)
   - Bullet points using ● with **[Bold Bracket Tags]**
   - Sub-bullets numbered (1), (2), (3) for grouped items within a category
   - Key metrics and outcomes in **bold**
5. **Side Projects** — condensed, 1–2 lines each
6. **Education** — 1 line
7. **Additional Skills** — bold category labels + tools listed after (inject any remaining Critical/High keywords here)

---

## Base Template Selection
The archetype (Step 0 above) governs what leads and how experience is framed. Base template controls layout only:
- Archetype `CRM-STRAT` or `LOYALTY-PROG` → **Lifecycle** base
- Archetype `LIFECYCLE-EXP` or `GROWTH-LIFECYCLE` → **Growth/Retention** base
- Hybrid (equal primary/secondary split) → use the primary archetype's mapping
- When in doubt → Growth/Retention

---

## Cover Letter PDF

Every resume generation script must also produce a cover letter PDF in the same `resumes/` folder:
- Filename: `{{FIRSTNAME}}-{{LASTNAME}}-{Company}-{RoleSlug}-Cover-Letter.pdf`
- Format: A4, same margins (LM=RM=0.44in, TM=0.37in, BM=0.30in), Helvetica
- Header: Name (17pt bold) + contact line (8.5pt grey) + horizontal rule
- Date line: "June 2026" (or current month/year), left-aligned, 8.5pt grey
- Body: paragraphs at 8.5pt, 12pt leading, justified, with 6pt space between paragraphs
- Closing: "Best regards," followed by name on next line
- Verify exactly 1 page with pypdf (trim to fit if needed)
- Generate both PDFs in the same script run — never one without the other

## Pre-submission Checklist
- [ ] Archetype detected and stated (primary + secondary + framing sentence)
- [ ] Summary angle matches primary archetype
- [ ] Lead bullets match primary archetype's "lead experience" list
- [ ] No `—` anywhere
- [ ] "Talabat (Delivery Hero)" — correct
- [ ] Single-column layout, no tables or graphics
- [ ] Standard section headings only
- [ ] Every bullet starts with a capital action verb
- [ ] Every bullet has a number or hard scope qualifier
- [ ] No repeated action verbs within a single role block
- [ ] JD keywords injected naturally (not as a dump)
- [ ] All Critical and High missing keywords from ATS audit are present
- [ ] Summary contains top 2-3 JD keywords in sentence 1
- [ ] PDF is exactly 1 page (pypdf verified)
- [ ] Summary is tailored to THIS role, not generic
- [ ] Archetype logged to Notion Notes field: `Archetypes: [PRIMARY] (primary) + [SECONDARY] (secondary). [Framing sentence].`
