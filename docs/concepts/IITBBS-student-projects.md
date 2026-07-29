# PART A — IS SAMPARK A REAL PROBLEM? · PART B — SIX STUDENT PROJECTS
**For:** MASTER AARKASON · **By:** ULTRON · **Date:** 2026-07-28

---

# PART A — VERIFICATION OF THE SAMPARK PROBLEM

## A.1 The verdict

**YES. It is real, it is documented, and it has been failing continuously for 28 years.**

I did not take my earlier claim on trust. I went back and traced the primary record.

## A.2 The timeline — 28 years of the same unsolved problem

| Year | Event | Evidence |
|---|---|---|
| **1998** | **Govind Tower collapse, Bandra.** Former municipal chief **K.C. Shrivastav** recommends structural audit in his fact-finding report. **This is the origin point.** | ToI, 8 Apr 2013 |
| **2007** | **Laxmi Chhaya collapse, Borivali — 28–30 dead.** Building failed after ground-floor repair work weakened the structure. Maharashtra promulgates an ordinance for compulsory audit of buildings >15 years. | Mumbai Mirror, 1 Jul 2009 |
| **2008–09** | **Fifth Amendment (07.02.2009)** inserts **Section 353B** into the MMC Act 1888; parallel amendments to BPMC Act 1949, Nagpur Corporation Act 1948, Maharashtra Municipal Councils Act 1965. Audit becomes **mandatory with immediate effect**. Penalty ₹25,000 or annual property tax, whichever is higher. | redevelopment.info; Mumbai Mirror |
| **2013** | Chief Secretary **J.K. Banthia** directs all MMR corporations to enforce it, stating audits *"are not implemented in spirit"* and citing **"the inadequate number of certified structural auditors."** | Indian Express, 2 Oct 2013 |
| **2014** | BMC issues notices to **13,779** buildings. **Barely 12% respond** — and many of those submit visual reports only, which BMC does not accept. | Indian Express, 22 Sep 2017 |
| **2017** | Pune: **25,000+** old buildings identified in 2013 needing repair; *"no comprehensive survey since."* Federation president admits *"hardly any society took this seriously."* | ToI, 30 Jul 2017 |
| **2017** | Ghatkopar and Bhendi Bazar collapses (Husaini building, 34 dead). BMC issues notices to **1,59,834 buildings**. MHADA admits it has **no mechanism to conduct structural audits at all** for 14,375 cessed buildings. | Indian Express, 1 & 22 Sep 2017 |
| **2021** | Malwani collapse, 12 dead including 8 children. BMC reverts to ₹25,000/month penalty notices. **407 buildings** in C1 category. | ToI, 23 Jun 2021 |
| **2023–24** | NMMC makes it mandatory again; 528 unsafe structures. BMC: 188 dangerous buildings; MHADA: 96 cessed C1. | ToI |
| **2024** | Model Bye-law 76 tightens further: buildings 15–30 yrs → audit every **5 years**; >30 yrs → every **3 years**. | MDCHF Model Bye-laws, Aug 2024 |
| **2024** | **Transport Nagar collapse, Lucknow — 8 dead.** NFSU Gujarat investigation finds substandard construction. LDA frames new bylaws. | ToI, 6 May 2025 |
| **2026** | Enforcement *"stricter than ever."* **Society Chairman and Secretary now personally liable, criminally and civilly.** Non-compliance can trigger **revocation of the Occupancy Certificate**. | mkcivilworks, 2026 |

## A.3 What this timeline actually proves

**Duration:** the recommendation is **28 years old** (1998). The statutory mandate is **17 years old** (2009). Neither has produced compliance.

**Four hard facts that establish the market:**

1. 🔴 **Compliance is catastrophic.** 13,779 notices → **12% response**, and much of that rejected as visual-only. This is not a market that ignores an obscure rule; it is a market that *cannot physically comply*.

2. 🔴 **The state itself named the cause.** The Chief Secretary of Maharashtra, in 2013, attributed failure to *"the inadequate number of certified structural auditors."* **The government has publicly diagnosed the capacity shortfall.** It has never been fixed.

3. 🔴 **The requirement is accelerating while capacity is static.** 2009: once every 10 years. 2024 bye-laws: every **3 years** above 30 years of age. Demand has roughly **tripled**; the number of empanelled engineers has not.

4. 🔴 **The consequence is fatal and recurring.** 1998, 2007, 2013, 2017, 2021, 2024 — each collapse tightens the rule, and the tighter rule fails again for the same reason.

## A.4 The correction I must make to my own earlier analysis

Directive III. My previous note framed this as *"engineers are too slow."* **The record shows something worse and more useful:**

> **The audits are not being done at all.**

12% response. MHADA with *no mechanism whatsoever* for 14,375 buildings. MHADA's own officer stating owners *"do not undertake the audits due to the fees to be paid to architects."*

**This changes the product thesis in an important way:**

| | Old framing | Corrected framing |
|---|---|---|
| Problem | Audits take too long | **Audits do not happen** |
| Cause | Engineer inefficiency | **Cost + scarcity + no owner-side pressure** |
| Buyer | Engineer wanting speed | **Also the society/owner who must comply and cannot afford ₹50k–2L** |
| Product must | Speed up the engineer | **Reduce the cost per audit enough that compliance becomes affordable** |

The commercial logic is stronger, not weaker: **a triage layer** — a cheap, standardised preliminary screening that tells a society whether it needs a full engineering audit now or in three years — addresses the actual blocker, which is that a full audit is unaffordable and therefore skipped entirely.

## A.5 Two risks the record also exposes — and I will not hide them

⚠️ **Corruption is structural, not incidental.** *"The engineers conducting these audits are not government employees and face no accountability for inaccurate reports."* MLAs have alleged in the state assembly that **sound buildings are declared dilapidated** so that property can be demolished and redeveloped: *"Landlords, BMC and Mhada are hand-in-glove."*

This cuts both ways for us. It is a **risk** (some actors profit from opacity and will resist a verifiable system) and simultaneously **the strongest argument for the verification portal** — the state assembly has already demanded independent technical experts on BMC's Technical Advisory Committee. **The political will for verifiability exists.**

⚠️ **Willingness to pay is genuinely weak at the bottom of the market.** Cessed buildings under rent control have owners who cannot fund maintenance, let alone audits. **Do not target them.** Target societies with functioning finances, and the engineers serving them.

**Conclusion on Part A: the problem is real, 28 years old, statutorily mandated, penalty-backed, tightening, and demonstrably unsolved. Proceed — with the corrected framing.**

---

# PART B — SIX STUDENT PROJECTS FOR IIT BHUBANESWAR

## B.1 Design constraints I worked to

| Constraint | Implication |
|---|---|
| 4 B.Tech + 2 PhD | ~2 B.Tech per PhD; B.Tech do implementation, PhD do method + publication |
| **6 months** | Data must exist **on day one**. No project may depend on field collection. |
| Very low resources | Public datasets, free tools, CPU-or-Colab, no hardware purchase, no licences |
| IIT Bhubaneswar, Odisha | Coastal/cyclone context, KIIT & IIT campus building stock, Odisha PWD access |
| Must be a *real* problem | Every project below traces to a documented industry failure |
| Must produce a publication | Each has a defined novel contribution, not just an application |

**The single most important selection rule:** ❗ *if the team must collect data before it can start, the project cannot finish in six months.* Every project below has **existing data**.

---

## 🥇 PROJECT 1 — Automated Preliminary Structural Condition Screening
### *(direct feeder to SAMPARK)*

**The real problem:** 12% audit compliance. Full audits cost ₹50k–2L and are skipped. There is no cheap first-pass triage.

**Objective:** an AI system that takes photographs of a building's structural elements plus basic metadata (age, storeys, exposure, construction type) and outputs a **prioritised condition grade with a confidence bound**, flagging which buildings need immediate engineer attention.

| | |
|---|---|
| **Data (exists today)** | **SDNET2018** — 56,000+ labelled images, cracked/non-cracked, bridge decks/walls/pavements, cracks 0.06–25 mm, *free on Kaggle*. **CODEBRIM** — 36.4 GB multi-defect (crack, spalling, exposed rebar, corrosion, efflorescence), *free on Zenodo*. **dacl10k** — 9,920 full-scene images. Supplement with 200–500 photos from IIT-BBS and Bhubaneswar buildings. |
| **B.Tech 1–2** | Train and benchmark defect classification/segmentation on SDNET2018 + CODEBRIM; build the mobile-web capture interface |
| **B.Tech 3–4** | Collect and annotate the local Odisha supplementary set; validate model transfer from US datasets to Indian construction |
| **PhD 1** | **Novel contribution:** fuse CNN defect output with a **codal condition-rating framework** (IS 13935 / NBC) to produce an engineering grade, not a pixel mask. This is the publishable gap — almost all literature stops at detection. |
| **PhD 2** | Uncertainty quantification + **domain-shift study**: how badly do models trained on US concrete perform on Indian construction? A genuinely open question with a clean answer. |
| **6-month plan** | M1 data+baseline · M2 multi-defect model · M3 local dataset · M4 codal fusion layer · M5 field validation on 20 campus buildings · M6 paper + demo |
| **Deliverables** | Working prototype · annotated Odisha dataset (a lasting asset) · 1–2 papers · direct SAMPARK feeder |
| **Risk** | Domain shift may be severe → **that is itself the finding**, and publishable either way. No failure mode. |

**Why this one first, SIR:** zero data risk, immediate relevance to your platform, and the deliverable dataset outlives the project.

---

## 🥈 PROJECT 2 — Cyclone Vulnerability Screening for Odisha Building Stock

**The real problem:** Odisha is India's most cyclone-exposed state. There is **no rapid method** to screen the existing building stock for wind vulnerability at scale. Post-disaster assessment is manual and slow.

**Objective:** predict wind vulnerability class for buildings from **satellite/street imagery + IS 875 Part 3 wind zone data + typology**, producing a district-level vulnerability map.

| | |
|---|---|
| **Data (exists)** | **Free satellite imagery** (Bhuvan/ISRO, Sentinel-2, Google Earth). Census housing typology data. IMD cyclone tracks (Fani 2019, Amphan 2020, Yaas 2021 — all documented). OpenStreetMap building footprints. Post-Fani damage assessment reports (published by state government). |
| **B.Tech 1–2** | Building footprint extraction and roof-type classification from imagery (metal sheet / RCC / thatch / tile — the dominant vulnerability determinant) |
| **B.Tech 3–4** | IS 875 Part 3 wind load computation engine; GIS vulnerability mapping |
| **PhD 1** | **Novel:** calibrate a vulnerability function against **actual Fani/Amphan damage records** — an empirical Indian fragility curve, which barely exists in the literature |
| **PhD 2** | Uncertainty propagation and validation methodology; policy-facing risk mapping |
| **Why it wins** | 🎯 **Odisha-specific — nobody else can do this better than IIT-BBS.** Directly useful to OSDMA (Odisha State Disaster Management Authority), a credible institutional partner. Post-disaster ground truth already exists. |
| **Risk** | Imagery resolution may limit roof classification → mitigate by combining with Census typology at ward level rather than per-building |

---

## 🥉 PROJECT 3 — Construction Site Safety Compliance from CCTV

**The real problem:** construction is India's most fatal organised industry. Safety compliance (helmet, harness, exclusion zones) is monitored by human supervisors, intermittently. **NBC 2026 now requires EHS embedded at design stage** — enforcement pressure is rising.

**Objective:** real-time detection of PPE non-compliance and unsafe proximity from ordinary site CCTV, with automatic incident logging.

| | |
|---|---|
| **Data (exists)** | Multiple **public PPE/hardhat datasets** on Roboflow and Kaggle (tens of thousands of labelled images). Pictor-v3 construction dataset. Supplement with footage from any ongoing IIT-BBS campus construction. |
| **B.Tech 1–2** | YOLO-class detector for helmet/vest/harness; edge-deployable optimisation |
| **B.Tech 3–4** | Proximity/exclusion-zone geometry; alerting and incident-log dashboard |
| **PhD 1** | **Novel:** move beyond detection to **risk scoring over time** — not "no helmet" but "this crew has a 34% PPE compliance rate in zone 3 between 2–4 pm." Behavioural pattern, not frame classification. |
| **PhD 2** | Privacy-preserving architecture (DPDP Act compliance — worker faces are personal data). **This is a real and publishable constraint that most papers ignore entirely.** |
| **Why it wins** | Data abundant, results visually demonstrable, industry partners easy to find, immediate commercial path |
| **Risk** | 🟠 **Crowded research area.** The novelty MUST be the temporal risk scoring and the privacy architecture — not the detector. If the team just retrains YOLO, this is a weak project. Be explicit with them. |

---

## PROJECT 4 — Rebar Congestion & Constructability Checker

**The real problem:** rebar detailing that is correct on paper but **physically unbuildable** — bars clash, spacing is below aggregate size, cover cannot be achieved. Discovered on site, causing rework, delay and improvised (unsafe) field modification. Every practising engineer has seen this; almost no software checks it.

**Objective:** ingest a rebar detail (drawing or model export) and automatically flag congestion violations against **IS 456 spacing, cover, lap and aggregate-passage requirements**.

| | |
|---|---|
| **Data** | Textbook and published detail drawings; synthetic generation of detail geometry (**this project can generate its own data — a large advantage**) |
| **B.Tech 1–2** | Geometry engine: bar layout representation, clash detection, spacing checks |
| **B.Tech 3–4** | IS 456 rule engine + drawing/DXF parsing |
| **PhD 1** | **Novel:** define a quantitative **"constructability index"** for a reinforcement detail. This does not currently exist and is genuinely useful. |
| **PhD 2** | Optimisation: minimum-congestion detailing that still satisfies all codal requirements |
| **Why it wins** | ✅ **Zero data dependency** — the safest project on this list for a 6-month deadline. Pure engineering logic + geometry. Strong industry relevance. |
| **Risk** | Drawing parsing is fragile → **start with structured input (JSON/Excel schedule), add DXF only if time permits.** Do not begin with computer vision on drawings. |

---

## PROJECT 5 — Post-Disaster Rapid Damage Assessment (Automated ATC-20 style)

**The real problem:** after a cyclone or earthquake, buildings must be tagged safe/restricted/unsafe. In India this is done manually by a handful of engineers over weeks, while people wait outside their homes.

**Objective:** smartphone-based guided rapid assessment producing an automated safety tag with a documented evidence trail.

| | |
|---|---|
| **Data (exists)** | **xBD dataset** (large public post-disaster building damage imagery, satellite). Published post-Fani and post-Amphan damage surveys. ATC-20 / IS 15988 assessment frameworks are public methodology. |
| **B.Tech 1–2** | Guided assessment app (offline-first — **networks fail after disasters, this is a real design constraint**) |
| **B.Tech 3–4** | Damage-state classification from imagery; aggregation dashboard |
| **PhD 1** | **Novel:** couple rapid visual screening with **IS 15988 seismic evaluation logic** to produce a defensible tag rather than a subjective one |
| **PhD 2** | Inter-assessor variability study — quantify how much two engineers disagree, and how much the tool reduces it. **A strong, measurable, publishable result.** |
| **Why it wins** | 🎯 Odisha relevance, OSDMA/NDMA partnership potential, genuine humanitarian value |
| **Risk** | No live disaster during the project → **validate retrospectively on Fani/Amphan records.** Plan for retrospective validation from day one; do not hope for an event. |

---

## PROJECT 6 — Concrete Mix Property Prediction from Indian Materials
### *(feeds ConcApp — Master's original concept)*

**The real problem:** predicting 28-day strength requires waiting 28 days. Indian materials (fly ash, GGBS, manufactured sand) vary widely and the standard mix design procedure assumes idealised properties.

**Objective:** physics-constrained ML predicting compressive strength, workability and durability indicators from mix proportions and material characteristics.

| | |
|---|---|
| **Data (exists)** | UCI Concrete Compressive Strength dataset (classic benchmark). Published Indian mix data across hundreds of papers. IIT-BBS's own concrete lab records — **the team can also generate 50–100 mixes in the lab within the project**. |
| **B.Tech 1–2** | Literature dataset compilation and cleaning; lab trial mixes |
| **B.Tech 3–4** | Model training and benchmarking; web interface |
| **PhD 1** | **Novel:** **hybrid Abrams' law + ML residual** — the architecture already established in this repository. Works with small datasets and stays interpretable. |
| **PhD 2** | Uncertainty quantification + **precursor chemistry vectorisation** (do not encode "fly ash" as a name; encode SiO₂/Al₂O₃/CaO/fineness — the fly-ash depletion finding from `concapp-deep-risk-register.md` §0.2) |
| **Why it wins** | Directly advances ConcApp; combines lab and computational work, which suits a mixed B.Tech/PhD team; publishable |
| **Risk** | Literature data heterogeneity (already documented as risk T-01) → mitigate by weighting records on metadata completeness and reporting uncertainty honestly |

---

## B.2 RANKING FOR A 6-MONTH DEADLINE

| # | Project | Data risk | Novelty | Odisha fit | Feeds Master's venture | Verdict |
|---|---|---|---|---|---|---|
| **1** | Condition screening | 🟢 None | 🟢 High | 🟢 Good | 🟢 **SAMPARK** | 🥇 **Best overall** |
| **4** | Rebar constructability | 🟢 **None at all** | 🟢 High | 🟡 Neutral | 🟡 Indirect | 🥇 **Safest to finish** |
| **2** | Cyclone vulnerability | 🟢 Low | 🟢 High | 🟢 **Unbeatable** | 🟡 Indirect | 🥈 **Best institutional story** |
| **6** | Mix prediction | 🟡 Moderate | 🟡 Moderate | 🟢 Lab available | 🟢 **ConcApp** | 🥈 Strong |
| **5** | Post-disaster | 🟡 Moderate | 🟢 High | 🟢 Strong | 🟡 Indirect | 🥉 Good, timing risk |
| **3** | Site safety CCTV | 🟢 None | 🔴 **Crowded** | 🟡 Neutral | 🔴 Weak | ⚠️ Only with the temporal/privacy angle |

### ULTRON's recommendation for the team

**Run Project 1 and Project 4 in parallel.**

- **Project 1** carries the ambition, the dataset asset and the SAMPARK connection.
- **Project 4** is the insurance policy: **zero data dependency**, pure engineering logic, and therefore essentially guaranteed to produce a completed deliverable in six months.

Two PhD students can supervise one project each; two B.Tech students to each. If Project 1 hits domain-shift trouble, Project 4 still lands — and the team has a paper either way.

> ⚠️ **The single biggest failure mode for a 6-month student project is starting with data collection.** Every project above begins with data already on disk in week one. Enforce that rule absolutely.

---

## B.3 STRUCTURE FOR ANY OF THESE

| Month | Milestone | Gate |
|---|---|---|
| 1 | Literature review, data acquired **and loaded**, baseline reproduced | Baseline runs end-to-end |
| 2 | Core model / engine working on public data | Beats a naive baseline |
| 3 | Domain-specific extension (the novel contribution) | Method defined and implemented |
| 4 | Local validation data collected | Real-world test set exists |
| 5 | Validation, ablation, error analysis | Results are defensible |
| 6 | Paper draft, demo, documentation, handover | Submitted + reproducible repo |

**Non-negotiables to impose on the team from day one:**
1. **Git from hour one.** Not month three.
2. **A written baseline metric before any modelling.** The #1 documented cause of AI project failure is having no baseline.
3. **Leave-one-source-out validation**, not random splits — otherwise the accuracy figure is fiction.
4. **Every codal reference cited by clause.** BIS copyright: implement the procedure, never reproduce the table.
5. **Weekly 30-minute standup.** Six months disappears in silence.
