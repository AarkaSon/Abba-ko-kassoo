# STAGE 0 — CORRIDOR DATA REQUEST PACK

**Purpose:** obtain the construction and condition records required to validate SETU
against a real pavement (Objective 6 of the proposal).
**Risk addressed:** SETU weakness — *"obtaining as-built data is politically hard; bad
data exposes bad construction."*

---

## THE GOVERNING PRINCIPLE ⚠️

> **Never frame the request as an audit. Frame it as forward-looking asset management.**

The single fastest way to be refused is to give the recipient the impression that you
intend to examine whether their pavement was built correctly. Every letter below is
written so that the reader concludes: *this person wants to help me spend my maintenance
budget better, and there is no adverse finding in it for me.*

Three rules, applied throughout:

1. **Ask for data on a corridor they are proud of**, or a new one. Never one with a
   known problem — that is precisely where the defensiveness lives.
2. **Offer the output back, free.** You are not extracting; you are exchanging. A
   residual-life study is worth real money to them and costs you only compute.
3. **Route through the institution.** A letter countersigned by your supervisor on
   department letterhead is opened. An individual email is not.

---

## ROUTE A — CONCESSIONAIRE (fastest; recommended first) 🥇

**Why first:** private entity, commercial decision-making, no tender process, and a
direct financial stake in pavement condition over a 15–30 year concession. They are the
only party who *loses money personally* when a slab fails early.

**Who to approach:** Head of O&M / Technical Head / Asset Manager at an operator of a
concrete corridor (HAM, BOT or TOT). Identify via NHAI's project pages, company
websites, or the LinkedIn search: `"O&M Head" OR "Asset Manager" + highway + India`.

### Letter A

> [Department letterhead]
>
> To,
> The Head — Operations and Maintenance
> [Concessionaire name]
> [Address]
>
> **Subject: Request for construction and condition records for a research study on
> predictive maintenance of concrete pavements — offer of a complimentary
> residual-life assessment**
>
> Respected Sir/Madam,
>
> I am a research scholar in the Department of Civil Engineering at [Institution],
> working under the supervision of [Supervisor], on the prediction of residual life and
> maintenance prioritisation for cement concrete pavements.
>
> The study develops a reliability-based extension of the cumulative fatigue damage
> framework prescribed in IRC:58. In conventional practice, the design computation is
> performed once, using single representative values for subgrade support, concrete
> strength and traffic, and is not revisited thereafter. Our work treats these
> quantities as distributions, propagates the variability through the codal damage
> model, and estimates the probability of distress and the residual life **for each
> segment of a corridor separately**, rather than for the corridor as a whole.
>
> The practical output is a ranked list indicating which segments are most likely to
> require intervention first, and the financial consequence of deferring that
> intervention. For an operator responsible for pavement condition over a concession
> period, this permits maintenance expenditure to be directed to the segments where it
> yields the greatest benefit.
>
> I write to request access to records for one corridor of your choosing. The data
> required is that which is generated in the ordinary course of construction and
> operation:
>
> 1. Subgrade and sub-base investigation data (CBR or plate load test results, by chainage)
> 2. Concrete pour register — date, chainage, mix reference
> 3. Cube and beam test results corresponding to those pours
> 4. Pavement composition — slab thickness, joint spacing, lane width, dowel and tie bar details
> 5. Traffic data — classified volume count or toll plaza classification, and growth
> 6. Any condition or distress survey carried out since opening
>
> **In return, and at no cost to your organisation, I will provide:**
>
> - A segment-wise residual-life and distress-risk assessment for the corridor;
> - A maintenance prioritisation schedule with an indicative cost of deferral;
> - A written technical report, and a presentation to your team if desired.
>
> I wish to state clearly that the purpose of the study is **prospective asset
> management and not retrospective evaluation of construction quality**. No finding
> regarding past workmanship will be drawn, reported or published. All data will be
> treated as confidential, used solely for this research, and reported in anonymised
> form. The corridor will not be identified in any publication without your express
> written consent. I am glad to execute a non-disclosure agreement in your standard form.
>
> A preliminary computational framework has already been implemented and verified, and
> I would be happy to demonstrate it at your convenience, either at your office or
> online.
>
> I would be grateful for the opportunity to discuss this briefly at a time convenient
> to you.
>
> Yours faithfully,
>
> **[Name]** · [Designation]
> Department of Civil Engineering, [Institution]
> [Phone] · [Email]
>
> *Countersigned:* **[Supervisor name]**, [Designation]

---

## ROUTE B — STATE PWD / ROAD DEVELOPMENT CORPORATION

**Why second:** large networks and real budget pressure, but slower and more
process-bound. Best approached through your institution's existing relationships.

**Adjust Letter A as follows:**

- Address to the **Chief Engineer (Roads) / Engineer-in-Chief**, and mark a copy to the
  Superintending Engineer of the relevant circle.
- Replace the commercial paragraph with a **public-interest framing:**
  > *"For a State authority responsible for allocating a constrained maintenance budget
  > across a large network, the framework provides an objective and auditable basis for
  > prioritising expenditure, in place of uniform or reactive allocation. The
  > methodology is founded entirely upon IRC:58 and is fully traceable to its
  > provisions."*
- Add: *"The study is academic and non-commercial in nature. No fee is sought."*
- Offer to present to the department, and to acknowledge their support in any publication.
- **Expect 6–12 weeks.** Follow up by telephone after three weeks, then fortnightly.

---

## ROUTE C — DESIGN CONSULTANT (easiest access, weakest data)

Consultants hold design records and often condition survey data, and are far more
accessible than owners. **Use this route to obtain a working dataset quickly** while
Routes A and B proceed in parallel.

Frame as: *"reliability-based design as a differentiated service you could offer your
clients"* — you are giving them a commercial capability, not taking their data.

---

## ROUTE D — INSTITUTIONAL FALLBACK (zero permission required) ✅

**If all three routes stall, the research is not blocked.** Sources requiring no
gatekeeper:

| Source | What it yields |
|---|---|
| Your own department's past MTech/PhD theses on rigid pavements | Real Indian mix, subgrade and traffic data, already cleared for academic use |
| Published Indian case studies and IRC/ICI journal papers | Distress records with construction context |
| **PMGSY / MoRTH published project data**, NHAI Maintenance Manual | Composition, specification and distress definitions |
| Long-Term Pavement Performance (LTPP) public database (US) | Extensive rigid pavement condition histories — **free, downloadable, ideal for method validation** even though the climate differs |
| Your own supervisor's field contacts | Usually the fastest route of all — **ask first** |

> **Strategic note, SIR:** validate the *method* on LTPP data, which is free and
> immediately available, and use that verified result as the credibility instrument for
> obtaining Indian corridor data. A working demonstration opens doors that a letter cannot.

---

## THE ONE-PAGE ATTACHMENT

Attach a single page to every letter. Nobody reads a proposal from a stranger; everybody
reads one page. It should contain:

1. **The question** — *"Which 200 m of this corridor will fail first, and what does
   waiting cost?"*
2. **The Table 8.2 result** — the 285/300/320 mm thickness spread. One table, no theory.
3. **What you need** — the six-item data list.
4. **What they get** — the free segment-wise assessment.
5. **The assurance** — forward-looking, confidential, anonymised, no audit.

Generate it from `scripts/generate_deck.py` (slide 6 works as a standalone page).

---

## TRACKER

| # | Organisation | Route | Contact | Sent | Follow-up 1 | Follow-up 2 | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |

**Target: 5 approaches, 1 dataset.** A single corridor is sufficient for Objective 6.
