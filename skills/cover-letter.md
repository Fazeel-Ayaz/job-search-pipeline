# Skill: Cover Letter

**Always active.** Apply every time a cover letter is written. These rules override any default cover letter behaviour.

---

## Structure

Three to four paragraphs, under one page, every paragraph earns its place.

### Paragraph 1 — Opening hook
Why this role, why now, why you noticed. Reference something specific about the company or the role — their product, a recent launch, something in the JD that stands out. Lead with the most relevant thing you bring, not a statement of intent.

**Never open with:** "I am writing to express my interest in…" / "I am excited to apply for…" / "I am a highly motivated professional…"

**Always open with:** a specific hook — something you noticed, something you've done, a direct connection to the role.

### Paragraph 2 — Why you (the match)
Two or three specific examples of how your experience maps to their requirements. Not a resume summary — pick the two strongest matches and give brief context. Use language from the job listing. Numbers are your friend; keep them concise.

### Paragraph 3 — Why this company (the fit)
Show you have done your homework. Reference their product, mission, recent news, company culture, or a specific initiative. Explain why it matters to you personally. Generic flattery does not count — "I admire your innovative approach" is invisible.

**To write this paragraph well:** before writing, look up the company — their website, LinkedIn, recent press, what they are known for. One specific, accurate detail beats three vague compliments.

### Paragraph 4 — Close
Clear, confident call to action. Not desperate. One or two sentences:
"I'd welcome the chance to discuss how my experience in [X] could support your team's work on [Y]. Happy to chat at your convenience."

---

## Tone Matching

Read the job listing and company website before writing. Calibrate tone accordingly:

| Company type | Tone | Example phrasing |
|---|---|---|
| Startup / tech | Conversational, direct | "I've spent the last 3 years building exactly this kind of thing" |
| Corporate / enterprise | Professional, measured | "My experience in X aligns closely with your stated objectives" |
| Consumer tech / marketplace | Energetic, data-grounded | "At Talabat, I owned this exact problem across 8 markets" |
| Government / public sector | Formal, criteria-driven | "I address each of the key selection criteria below" |
| Creative agency | Personality forward | "Your work on X is what made me pay attention" |
| Non-profit | Mission-aligned | "I've followed your work in X and share your commitment to Y" |
| Financial services / banking | Professional, commercial | "My track record linking CRM activity to revenue and retention maps directly to your objectives" |

---

## Format and Length

- **Under one page, always.** If it runs over, cut — never shrink the font or reduce margins.
- Same header as the resume: Name (17pt bold) + contact line (8.5pt grey) + horizontal rule.
- Date line below the rule (month year).
- Body: 8.5pt Helvetica, 12pt leading, justified, 6pt space between paragraphs.
- Closing: "Best regards," / Name + contact on next line.
- Filename: `{{FIRSTNAME}}-{{LASTNAME}}-{Company}-{RoleSlug}-Cover-Letter.pdf` — same folder as the resume PDF.
- Always verify 1 page with pypdf before logging to Notion.

---

## Common Mistakes — Never Do These

1. **Rehashing the resume.** The cover letter adds context and personality — it never repeats bullet points.
2. **Generic openings.** "I am excited to apply for…" tells the reader nothing.
3. **No company reference.** If you could send the same letter to 50 companies unchanged, it is too generic.
4. **Underselling or overselling.** State what you have done, factually. No "I'm the perfect candidate" and no "I know I don't have much experience but…"
5. **Burying the lead.** If you have a direct connection (you use the product, deep domain expertise, exact experience match), say it in the first line.
6. **Addressing gaps or weaknesses upfront without being asked.** Be honest when the gap is obvious (e.g. banking background for a banking role), but don't open with your weaknesses.

---

## Special Circumstances

**Career changers:** Lead with transferable skills, not job titles. Bridge the gap explicitly: "5 years managing growth across food delivery — now applying that to fintech."

**Employment gaps:** Do not hide them. One sentence in the cover letter is enough (caring responsibilities, study, health, travel). List any relevant activity during the gap on the resume.

**Overqualified:** Directly address "why do you want this role?" — name the actual reason (scope change, new vertical, company mission, lifestyle). Don't let the reader guess.

**Underqualified:** Focus on adjacent experience and learning velocity. Acknowledge the stretch honestly and show you've closed similar gaps before.

**Multiple Talabat roles:** Reference Talabat once with clear progression context — "I've been at Talabat since 2023, progressing from Lifecycle Marketing Specialist to User Growth Sr. Specialist across New Verticals and Membership."

---

## Pre-Write Research Checklist

Before writing paragraph 3, look up:
- Company website / About page
- Recent product launches or news
- LinkedIn company page (recent posts, headcount, offices)
- The specific team or vertical this role sits in
- Anything in the JD that signals company culture, priorities, or current challenges

One real detail beats ten generic sentences.

---

## Good vs. Bad Example

**Too generic:**
> Dear Hiring Manager, I am writing to express my interest in the Marketing Manager position. I have 5 years of marketing experience and am a strong communicator with excellent organisational skills. I believe I would be a great addition to your team.

**Right approach (the candidate, food delivery → fintech context):**
> Hi [Name],
>
> Your job listing mentioned you are rebuilding the customer lifecycle function from scratch — that is exactly the kind of challenge I've been solving at Talabat, where I built the lifecycle and CRM infrastructure for the Grocery and Retail verticals across 8 MENA markets and grew GOV per user by 7% in the first year.
>
> Two things in the listing stood out: the focus on subscription retention and the need to connect CRM activity to commercial targets. At Talabat, I own both: a tPro freemium-to-premium program that drove +5pp conversion, and a churn prediction model that reduced churn 7% and improved incremental revenue 11%. I also built the Vendor Funded Deals GTM that delivered EUR 75,000 in Q1 2026 — working directly with commercial and finance partners to build the business case.
>
> I've been following [Company]'s approach to [specific product/initiative] since [timeframe]. The problem you're solving — [specific challenge from research] — is one I find genuinely interesting because [honest, specific reason]. It's the kind of work that sits at the intersection of customer data and commercial strategy, which is where I do my best work.
>
> I'd welcome the chance to discuss how my experience in lifecycle and growth could support your team's work on retention and CLV. Happy to chat whenever suits.
>
> Best regards, {{YOUR_FULL_NAME}}

---

## Output

Always produce a PDF: `{{FIRSTNAME}}-{{LASTNAME}}-{Company}-{RoleSlug}-Cover-Letter.pdf`
Verify 1 page with pypdf. Insert the full text into the Notion page body under `## Cover Letter`.
