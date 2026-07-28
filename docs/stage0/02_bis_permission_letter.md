# STAGE 0 — BIS REPRODUCTION PERMISSION REQUEST

**Risk addressed:** §0.3 / L-03 — copyright in Indian Standards vests in BIS; reproduction
of extracts requires written permission.
**Why now:** approval takes months. It must be in flight before Stage 1 ships.
**Cost:** a letter, a form, and possibly a nominal fee.

---

## ACTION CHECKLIST

- [ ] Download the reproduction request form: **bis.gov.in → Standards → Copyright**
- [ ] Email the letter below + form to **pub@bis.gov.in**
- [ ] CC / post to: Publication Department, Bureau of Indian Standards,
      9 Bahadur Shah Zafar Marg, New Delhi – 110002 · Ph: (011) 2323 7995
- [ ] Log the date sent and any reference number in `docs/stage0/FINDINGS.md`
- [ ] Follow up by phone after 3 weeks, then monthly

**Send from a professional address** (`aarkason@<yourdomain>` once incorporated, or your
institutional ID meanwhile). A student/institutional identity *helps* here — BIS is
markedly more receptive to educational and research framing.

---

## LETTER — copy, fill the blanks, send

> To,
> The Head, Publication Department
> Bureau of Indian Standards
> 9, Bahadur Shah Zafar Marg
> New Delhi – 110002
> Email: pub@bis.gov.in
>
> **Subject: Request for permission to reproduce extracts from Indian Standards in an
> engineering computation tool**
>
> Respected Sir/Madam,
>
> I am a civil engineer working in the field of concrete technology and pavement
> engineering, with a research focus on low-carbon and geopolymer concrete systems.
>
> I am developing an engineering computation tool intended to assist practising civil
> engineers in performing concrete mix proportioning in accordance with Indian Standards.
> The purpose of the tool is to **improve correct and consistent application of Indian
> Standards** in professional practice, and to reduce computational errors in mix design.
>
> I write to seek permission to reproduce limited extracts from the following Indian
> Standards within this tool:
>
> 1. **IS 10262 : 2019** — Concrete Mix Proportioning – Guidelines
> 2. **IS 456 : 2000** — Plain and Reinforced Concrete – Code of Practice
> 3. **IS 383 : 2016** — Coarse and Fine Aggregate for Concrete – Specification
> 4. **IRC:44** / **IRC:58** *(where applicable — note these are IRC, request separately)*
>
> Specifically, the extracts required are the tabulated design parameters necessary for
> the mix proportioning procedure (for example, approximate water content, volume of coarse
> aggregate per unit volume of total aggregate, and minimum cement content / maximum
> water-cement ratio for durability).
>
> I wish to state clearly:
>
> - Every computed output will **explicitly cite the governing Indian Standard and clause
>   number**, and will direct the user to refer to the standard itself.
> - The tool will carry a prominent notice that it does **not** substitute for the Indian
>   Standard, and that the user must consult the standard and exercise independent
>   professional judgement.
> - No part of the standard's text, commentary or layout will be reproduced.
> - The tool will encourage users to procure the relevant Indian Standards from BIS.
>
> I would be grateful if you could advise me on:
>
> 1. The permission applicable to this use;
> 2. Any licence fee or royalty payable, and the procedure for the same;
> 3. The attribution format BIS requires;
> 4. Any conditions BIS wishes to impose on such use.
>
> I have enclosed the prescribed request form. I am happy to provide a demonstration of the
> tool or any further information the Bureau may require.
>
> I hold Indian Standards in the highest regard as the foundation of safe engineering
> practice in our country, and my intention is to widen their correct application among
> practising engineers. I look forward to your guidance.
>
> Yours faithfully,
>
> **[Full Name]**
> [Designation / Institution]
> [Address]
> [Phone] · [Email]
> Date: __________

---

## FALLBACK ARCHITECTURE — build as if permission never arrives

**Do not let this block Stage 1.** Design the calculator so it is lawful *without* permission,
and merely *better* with it.

| ❌ Do NOT ship | ✅ Ship instead |
|---|---|
| IS 10262 Table 2 reproduced as a lookup table | A fitted continuous function `w(a_max, slump)` — **your original work** |
| IS 10262 Table 5 reproduced verbatim | Fitted surface `V_ca(a_max, zone, w/c)` |
| IS 456 Table 5 pasted in | Computed check + *"per IS 456:2000, Table 5 — refer to the standard"* |
| Clause text quoted | Clause **cited by number** only |
| "As per IS 10262, Table 2, water = 186 kg" | "Water content: 186 kg/m³ *(IS 10262:2019, cl. 5.2 — refer to the standard)*" |

**The legal principle:** facts, procedures and numerical relationships are not copyrightable
in India; **expression is.** A fitted function that reproduces a relationship is your work.
A scanned or retyped table is theirs.

**The engineering bonus:** continuous fitted functions are *superior* to discrete table
lookups — they interpolate smoothly instead of forcing users onto tabulated steps, and the
smooth derivative is exactly what the Stage 5 optimiser needs. **The legal constraint
produces a better product.** Document each fit with its R² and residual plot in
`src/design/` so its provenance as original work is defensible.

---

## ALSO DO IN THIS BATCH (same lead-time problem)

- [ ] **IRC permission** — Indian Roads Congress, Kama Koti Marg, Sector 6, R.K. Puram,
      New Delhi – 110022. Same letter, adjusted for IRC:44 / IRC:58 / IRC:15. Needed for
      the pavement module (Stage 6) — start it now.
- [ ] **Trademark search** — ipindia.gov.in public search for "ConcApp" in **Class 9**
      (software) and **Class 42** (SaaS). ₹4,500–9,000 to file.
      ⚠️ **Do this before spending anything on branding.** "ConcApp" is a generic-sounding
      construction; if it is taken or unregistrable, better to learn it now.
- [ ] **Domain check** — concapp.in / .com availability at the same time.
