# Resume Format Rules
> Loaded by: Resume Tailor only
> Do NOT load for any other agent — this is resume-generation context only

---

## Content Rules (CRITICAL — apply to every resume)

1. **No em dashes** — never use `—` anywhere in the resume or cover letter; use `:`, `;`, or commas instead
2. **Always use the correct parent company name** — verify the owning group for every company reference. Never guess or reuse a group name from a different employer.
3. **Stats from metrics reference only** — use only numbers from the Resume Metrics Reference in `context/profile.md`. Do not fabricate or round up. Work experience descriptions are intentionally high-level — never copy them verbatim into a resume bullet.

---

## Bullet Writing — XYZ Format (CRITICAL — apply to every experience bullet)

Source: [Simplify Jobs — How to use the XYZ resume format](https://simplify.jobs/blog/how-to-use-the-xyz-resume-format)

**Formula:** "Accomplished [X] as measured by [Y] by doing [Z]"
- **X (Achievement)** — start with a strong action verb describing the outcome
- **Y (Metric / Context)** — quantify with a hard number, percentage, currency, scope, or team size
- **Z (Action)** — name the specific lever, tactic, framework, or tool used

### Rules

1. **Always lead with the action verb, never with a prepositional phrase.** ("Drove 7% GMV uplift by…" not "By implementing X, drove 7% GMV uplift…")
2. **Past tense for prior roles, present tense for current role.** Never mix within the same bullet.
3. **Every bullet must contain a number.** If a hard metric isn't available, quantify by scope (markets, team size, budget, audience size, channels owned).
4. **Don't repeat action verbs within the same role block.** Rotate across: Owned, Built, Drove, Designed, Led, Launched, Scaled, Deployed, Orchestrated, Re-engineered, Integrated, Reduced, Improved, Increased, Co-developed.
5. **Inject JD keywords naturally into the Z (action) clause** — never bolted on as a list. If the JD says "always-on triggered programmes", write "built always-on triggered programmes via Braze" rather than "managed CRM (always-on, triggered)".
6. **No hedging.** Cut "helped", "supported", "contributed to", "assisted with", "up to X%". Own the number or state the floor.
7. **No prose intros or paragraph context inside a bullet.** Italic tagline under the role title carries the context — bullets carry the proof.

### Recommended Verbs by Bullet Type

| Bullet type | Verbs |
|---|---|
| Ownership / strategy | Owned, Led, Shaped, Drove, Directed |
| Build / launch | Built, Designed, Launched, Deployed, Scaled, Re-engineered |
| Analysis / insight | Analysed, Diagnosed, Identified, Modelled, Forecasted |
| Optimisation | Improved, Reduced, Increased, Optimised, Decontaminated |
| Cross-functional | Co-developed, Partnered, Orchestrated, Aligned |

### Good vs Bad Examples

| ❌ Weak | ✅ XYZ-formatted |
|---|---|
| "Worked on CRM campaigns across email and push" | "Built always-on triggered lifecycle programmes across email, push, in-app, and SMS via Braze; drove **7% GMV uplift per user** and **3% CVR uplift**" |
| "Helped reduce churn through behavioural targeting" | "Built churn prediction model identifying at-risk cohorts: **7% churn reduction** and **11% incremental GMV uplift**" |
| "Contributed to tPro membership growth" | "Drove freemium-to-premium activation for tPro: **+5pp conversion uplift** via cross-sell lifecycle campaigns" |
| "Ran A/B tests to improve cost efficiency up to 20%" | "Designed holdout-group experimentation framework; improved cost per incremental GMV by **20%**" |

### Bracket Tags

Wrap each bullet's category in `[Bold Bracket Tags]` to group by theme within a role. The tag is the bullet's "type" (e.g. `[Lifecycle Strategy]`, `[CRM Automation]`, `[Cross-Functional]`). Tags should match the JD's language where possible.

---

## Format Rules (CRITICAL)

All tailored resumes must:

1. Be **exactly 1 page** — verify with pypdf before returning
2. **Fill the full page.** The resume must use all available vertical space; do not leave visible whitespace at the bottom. After the initial draft, visually inspect the PDF. If whitespace remains, pull additional P1/P2 pointers from the Resume Metrics Reference to add bullets to existing role blocks, expand compressed roles (Foodpanda, Dawaai) with a second bullet, or add more side project entries. Keep pulling until the content reaches the bottom margin. Every added bullet must follow the same XYZ format and single-focus tailoring rule.
3. Follow the **exact same structure** as the Lifecycle or Growth/Retention resume templates in the root folder
4. Use the reportlab generation workflow (write `resumes/gen_[company]_[role]_resume.py`, run it, verify)
5. **PDF spec:** A4 page, Helvetica font, margins: 0.44in top/bottom, 0.37in left, 0.30in right

---

## Resume Structure

1. **Name** — large bold, top center-left
2. **Contact line** — city | phone | email | LinkedIn (smaller, below name)
3. **Summary** — 2–3 lines, tailored to the role using primary archetype's summary angle
4. **Work Experience** — reverse chronological
   - Company | Role Title (bold) + date right-aligned
   - Italic tagline/context line under the title (scope-setting — see Seniority Framing skill)
   - Bullet points using ● with **[bold bracket tags]** for category grouping
   - Sub-bullets numbered (1), (2), (3) for grouped items within a category
   - Key metrics and outcomes in **bold**
5. **Side Projects** — condensed, 1–2 lines each
6. **Education** — 1 line
7. **Additional Skills** — bold category labels + tools listed after

---

## Which Base Resume to Use

Archetype detection (run first — see `skills/archetypes.md`) determines the framing. Base template controls layout:

- Archetype `CRM-STRAT` or `LOYALTY-PROG` → use **Lifecycle** base (your Lifecycle resume PDF in the project root)
- Archetype `LIFECYCLE-EXP` or `GROWTH-LIFECYCLE` → use **Growth/Retention** base (your Growth/Retention resume PDF in the project root)
- Hybrid (tied signals) → use primary archetype's mapping. When in doubt → Growth/Retention.

---

## Resume Generation Sub-Workflow (Step 4.5 — triggered after Approved? = true)

For each `Approved? = true` Notion row without a generated resume:

**a. Fetch JD** — pull the full JD from the Notion page body (user pastes JD there if the career site blocks WebFetch)

**b. Run job-application-resume skill (analysis only)** — invoke `Skill(skill: "anthropic-skills:job-application-resume")` to produce:
- **Match scorecard** (Step 2): match score /100, candidate years vs JD required years, industry fit, top 5 missing JD keywords tagged Critical/High/Medium, 3 red flags a hiring manager spots in <10 seconds
- **ATS Skip Zone audit** (Step 3): bullet-by-bullet Read/Skim/Skip classification of draft bullets, with rewrites for every Skim and Skip
- **IGNORE the skill's Step 4 PDF spec** — do NOT use the skill's default PDF layout. Its output here is analytical input only.

**c. Choose resume base** — Lifecycle (CRM/lifecycle/retention/engagement roles) vs Growth/Retention (PMM/growth/acquisition/experimentation roles)

**d. Generate PDF** — write `resumes/gen_[company]_[role]_resume.py` modelled on existing scripts (`gen_neko_london_resume.py`, `gen_ebay_crm_resume.py`, `gen_hellofresh_virality_resume.py`). Apply format rules above and feed in the ATS-audited bullets from step (b). Save to `resumes/[Your-Name]-[Company]-[RoleSlug].pdf`.

**e. Inject keywords** — every Critical and High missing keyword from step (b)'s scorecard into the resume, either in a bullet or in the Additional Skills row, never as filler.

**f. Write cover letter** — invoke `skills/cover-letter.md`. Research company before writing paragraph 3. Follow the 4-paragraph structure: opening hook (specific, never generic) → match (two strongest proof points with numbers) → company fit (researched detail) → close (specific CTA). Generate cover letter PDF: `resumes/[Your-Name]-[Company]-[RoleSlug]-Cover-Letter.pdf`. Verify 1 page.

**g. Insert into Notion** — formatted resume text + cover letter into Notion page body under `## Tailored Resume` and `## Cover Letter` headings; update `Keywords` field with the actual JD keywords used.

**h. Verify** — PDF is exactly 1 page with pypdf; every bullet starts with an action verb; every bullet contains a number or hard scope; no em dashes; Talabat written as "Talabat (Delivery Hero)".
