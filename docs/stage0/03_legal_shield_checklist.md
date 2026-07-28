# STAGE 0.5 — LEGAL SHIELD CHECKLIST

**Risks addressed:** L-01 (professional liability), L-04 / §0.4 (DPDP Act), F-02 (GST),
L-07 (IP), L-05 (tender eligibility clock).
**Rule:** the shield goes up **before the first paying customer**, not after.

---

## PART 1 — INCORPORATION 🛡️

### Why this is non-negotiable
As a sole proprietor, your **personal assets** answer for a structural claim. A single
cracked slab attributed to a ConcApp recommendation could take your house. Incorporation
puts a legal wall between the venture and Master personally. **This is the cheapest
insurance you will ever buy.**

### Which structure

| Form | Cost | Compliance | Verdict |
|---|---|---|---|
| Sole proprietorship | ₹0 | minimal | ❌ **No liability shield. Never trade under this.** |
| **OPC (One Person Company)** | ₹6–10k | moderate | ✅ **Recommended now** — solo founder, full limited liability |
| **Pvt Ltd** | ₹8–15k | higher | ✅ Best if a co-founder joins or you ever raise |
| LLP | ₹7–12k | moderate | ⚠️ Partner-friendly but investors dislike it |

**ULTRON's recommendation: OPC now** (you are solo, it is the cheapest true shield), with
**conversion to Pvt Ltd** when a co-founder or first investor appears. Conversion is routine.

> ⏰ **Second reason to do it now:** tender eligibility (L-05) demands **3 years of audited
> turnover**. That clock only starts at incorporation. Incorporating today makes you
> tender-eligible in 2029 instead of 2032. Public infrastructure is the largest buyer in
> this market — do not delay the clock.

### Checklist
- [ ] DSC (Digital Signature Certificate) — ₹1,000–2,000
- [ ] DIN (Director Identification Number)
- [ ] Name reservation via **SPICe+ Part A** on mca.gov.in — keep 2–3 alternatives ready
- [ ] File SPICe+ Part B (MoA, AoA, PAN, TAN, EPFO/ESIC, bank account — one form)
- [ ] Open current account
- [ ] **Engage a CA** (~₹15–25k/yr) — do not self-file; the time cost exceeds the fee
- [ ] Object clause in MoA must cover: *software development, engineering consultancy,
      research and data services*

---

## PART 2 — DPDP ACT COMPLIANCE ⚖️

**Deadline: 13 May 2027. Board live since Nov 2025. Penalties to ₹250 crore.
No size exemption.**

### The strategy: minimise, don't manage
> **You cannot breach data you never collected.** Every field you decline to collect is a
> permanent reduction in legal exposure. Architect for this in Stage 1 — it is ~2 days of
> work now versus weeks of retrofit later.

### Data architecture rules (bake into the schema from the first migration)

| Rule | Implementation |
|---|---|
| **Two physically separate stores** | `users` (personal) and `mixes` (commercial). Never join them in analytics. |
| **Collect only** | email, organisation name, password hash. **That's it.** |
| **Never collect** | phone, address, location, DOB, ID numbers, photos of people |
| **Mix/test data is commercial, not personal** | Keeps the bulk of your data outside DPDP scope entirely — **this is the key architectural insight** |
| **Anonymise for training** | Strip org identity at the ETL boundary; train only on chemistry + results |
| **Retention** | Auto-purge inactive free accounts after 24 months |
| **Host in India** | Also a latency and trust win with government-adjacent clients |

### Compliance checklist
- [ ] Privacy notice — plain language, states purpose, retention, rights
- [ ] Consent checkbox at signup — **unticked by default**, specific, free, informed
      *(no "legitimate interest" basis exists under DPDP — consent or nothing)*
- [ ] Withdraw-consent mechanism, as easy as giving it
- [ ] **Data deletion endpoint — must complete within 7 days**
- [ ] **Breach response runbook — DPBI notification within 72 hours**
- [ ] Grievance officer named with contact (can be Master initially)
- [ ] Cookie notice if any analytics used — prefer a privacy-first analytics tool
- [ ] Vendor DPAs with hosting/email providers
- [ ] **No under-18 users** — DPDP sets the age at 18 with no exception; state it in ToS
      *(relevant: students will use the free calculator — handle explicitly)*

---

## PART 3 — TERMS OF SERVICE: THE LIABILITY CLAUSES 📜

**Have a lawyer review before first revenue (₹10–25k). Draft the substance yourself first —
that is what makes the lawyer's hour affordable.**

### Non-negotiable clauses

**1. Nature of service — decision support, not design**
> ConcApp provides computational assistance and predictive estimates for concrete mix
> proportioning. It does **not** constitute engineering design, professional advice, or
> certification. All outputs are advisory and must be independently verified and approved
> by a qualified, licensed engineer before use in any construction activity.

**2. Mandatory trial verification**
> All predicted properties are statistical estimates carrying inherent uncertainty. The
> User **shall conduct physical trial batches and laboratory verification** in accordance
> with applicable standards before any production use. ConcApp does not eliminate the
> requirement for trial mixes.

**3. Liability cap**
> ConcApp's aggregate liability shall not exceed the fees paid by the User in the twelve
> months preceding the claim. ConcApp shall not be liable for indirect, consequential or
> special damages, including structural failure, project delay, rework or loss of profit.

**4. Material variability disclaimer** *(specific to our technical risk T-02)*
> Cementitious and aluminosilicate materials exhibit significant variability between
> sources and batches. Predictions are conditioned on the material characteristics provided
> by the User. Inaccurate or incomplete material data will produce inaccurate predictions.

**5. Safety — alkaline activators** *(risk T-07)*
> Alkaline activators are corrosive and hazardous. The User is solely responsible for
> safe handling, PPE, storage and disposal in accordance with applicable safety
> regulations. **Log the user's acknowledgement of the safety sheet — that record is the shield.**

**6. Data rights** *(risk D-05 — settle this now, it becomes a diligence item later)*
> The User retains ownership of data uploaded. The User grants ConcApp a non-exclusive,
> perpetual licence to use **aggregated and anonymised** derivatives for model improvement.
> An opt-out ("no-training") tier is available.

**7. Codal compliance**
> Design parameters reference Indian Standards. The User is responsible for confirming
> that the applicable standard and its current revision are correctly applied. *(Ties to
> the BIS fallback architecture.)*

### ⚠️ The critical warning
Disclaimers alone are **weak** in Indian consumer and contract law, especially against a
claim of negligence. The ToS is only the **fourth** layer of the five-layer shield (L-01).
What actually protects you is the **architecture**: an interface that visibly makes the
licensed engineer the decision-maker, records his approval, shows every assumption, and
preserves an immutable audit trail. **Build the shield into the product, not just the PDF.**

---

## PART 4 — INSURANCE 🏥

- [ ] **Professional Indemnity / Tech E&O** — from first revenue. ₹40–90k/yr for ₹1–2 cr cover.
      Indian providers: ICICI Lombard, Tata AIG, HDFC Ergo, Bajaj Allianz.
- [ ] Disclose accurately that outputs are advisory and trial-verified — **misrepresentation
      voids the policy**, which is worse than having none.
- [ ] Revisit cover limits at every 5× revenue step.

---

## PART 5 — IP & FINANCIAL HYGIENE

- [ ] **Trademark** "ConcApp" — Class 9 + Class 42 (₹4,500–9,000). **Search first at
      ipindia.gov.in.** Do this before any branding spend.
- [ ] **Software copyright registration** — source + object code, India. Cheap, fast,
      useful evidence of ownership.
- [ ] **No patents** — algorithms are hard to patent in India, disclosure aids competitors,
      and the cost is better spent elsewhere. **Trade secret + execution speed.**
- [ ] **GST registration** — mandatory past ₹20 lakh (services); register earlier anyway,
      corporate buyers need the input credit to buy from you.
- [ ] **Separate business bank account** from day one. Never commingle. This is what
      preserves the corporate veil in practice.
- [ ] **Advance/annual billing with a discount** (risk F-03 — construction pays in 90–180 days).
      Never extend credit to a contractor.

---

## COST SUMMARY

| Item | One-time | Annual |
|---|---|---|
| OPC incorporation + DSC | ₹8,000–12,000 | — |
| CA retainer | — | ₹15,000–25,000 |
| Trademark (2 classes) | ₹9,000 | — |
| Software copyright | ₹2,000 | — |
| Lawyer — ToS/privacy review | ₹10,000–25,000 | — |
| Professional indemnity | — | ₹40,000–90,000 *(defer to first revenue)* |
| **Total before first revenue** | **≈ ₹30,000–48,000** | **≈ ₹15,000–25,000** |

**Sequencing under a tight budget (Master's constraint F-01):**
1. **Now, ~₹12k:** incorporation + DSC. *(Starts the tender clock; enables the bank account.)*
2. **Now, ~₹0:** trademark **search**, domain check, DPDP-minimal schema design, ToS draft.
3. **Before Stage 1 launch, ~₹0:** privacy notice + consent + deletion endpoint in code.
4. **Before first customer, ~₹25k:** lawyer review + trademark filing.
5. **At first revenue:** professional indemnity insurance.

> **Total to be legally safe through Stage 3 ≈ ₹12,000.** The rest is deferrable to the
> point where revenue funds it. There is no excuse to skip the shield.
