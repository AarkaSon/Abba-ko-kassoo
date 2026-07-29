# SIX CONCRETE-ONLY STUDENT PROJECTS — IIT BHUBANESWAR
## Re-scoped: pure concrete technology · lab-generated data · no external agency dependency

**For:** MASTER AARKASON · **By:** ULTRON · **Date:** 2026-07-28
**Supersedes:** the disaster/imagery projects in `IITBBS-student-projects.md`

---

## 0. WHY THE PREVIOUS LIST WAS WRONG — AND YOU WERE RIGHT TO KILL IT

You identified three blockers. All three were real, and I should have caught them:

| Your objection | My assessment |
|---|---|
| *"My domain is concrete-specific"* | ✅ Correct. Projects 1, 2, 3, 5 were structural/imagery/disaster. Wrong domain. |
| *"I may not access disaster records"* | ✅ Correct, and worse than you think — OSDMA/NDMA data requires institutional MoUs that take **6–18 months**. That alone consumes the entire project window. |
| *"My professor is concrete-specific; he may not be interested"* | ✅ **This is the decisive one.** A PhD supervisor who is not invested will not give time, lab access, or authorship priority. The project dies quietly in month three. |

> **The governing rule I am now applying: a student project must live entirely inside the
> supervisor's own laboratory.** No external agency, no MoU, no data request, no permission.
> If a single email to an outside body is required before work can start, it is disqualified.

**Every project below satisfies three tests:**
1. 🧪 The data is **generated in your own concrete lab**, or is a public concrete dataset already downloadable.
2. 🎓 The subject is **squarely concrete technology** — your professor's own field.
3. ⏱️ It can genuinely finish in **6 months** with 4 B.Tech + 2 PhD.

---

## 1. THE INDUSTRY PROBLEMS THESE ADDRESS — VERIFIED

Before the projects, the documented reality of Indian concrete production:

| Finding | Source |
|---|---|
| **Plant standard deviation ranges 1.92 → 6.57 MPa** across Indian RMC plants; coefficient of variation **0.06 → 0.164** | NBM&CW RMC quality control study |
| A **fully automatic Delhi plant with imported equipment recorded the WORST σ = 6.57** — automation alone does not fix quality | *ibid.* |
| Manual batching causes **slump variation up to 20 mm** | Construction Times, Sep 2025 |
| Poor aggregates → concrete **15–20% weaker** than required | *ibid.* |
| **20–30% of construction work is redone** due to weak concrete; project cost +15% | *ibid.* |
| Only **~60% of small RMC plants** comply with BIS; audits cost ₹5–10 lakh | *ibid.* |
| Only **~20% of workers** in small plants have formal training | *ibid.* |
| Lucknow 2023: poor concrete → collapse, **~₹50 crore loss**. Mumbai 2024: **~₹10 crore** | *ibid.* |

🎯 **The single most interesting fact for a research project:** *the best-controlled plant in the study was a small semi-automatic one; the worst was fully automatic with imported equipment.* **Quality is not an equipment problem. It is an information and control problem.** That is exactly what AI addresses — and it is a defensible thesis statement.

---

# THE SIX PROJECTS

---

## 🥇 PROJECT C1 — Early-Age Strength Prediction: Breaking the 28-Day Wait

**The problem:** Every structural decision waits 28 days. Formwork stripping, post-tensioning, load application, acceptance. A 7-day result that is low creates panic; a 7-day result that is fine may still fail at 28 days. **Nobody can predict the 28-day value reliably from early data for a specific plant's materials.**

**Objective:** Physics-constrained ML predicting 28-day compressive strength from **7-day strength + mix proportions + maturity (temperature-time history) + material properties**, with a calibrated confidence interval.

| | |
|---|---|
| **Data — day one** | **UCI Concrete Compressive Strength** (1,030 instances, 8 features, free). **BOxCrete open dataset (2026)** — 533 strength measurements, 123 mixes, **five curing ages (1, 3, 5, 14, 28 d)**, open-access, purpose-built for exactly this. Plus **your own lab: 40–60 mixes × 5 ages**, entirely feasible in 4 months. |
| **B.Tech 1–2** | Lab programme: cast and test 40–60 mixes across w/c ratios, SCM levels, curing temperatures. **This is standard concrete lab work your professor already supervises.** |
| **B.Tech 3–4** | Data pipeline, model training, benchmarking against Abrams' law and the maturity method (Nurse-Saul / Arrhenius) |
| **PhD 1** | **Novel contribution:** hybrid **maturity-function + Gaussian Process residual**. Physics carries the prediction; ML corrects the plant-specific bias. Works on small datasets — the key methodological claim. |
| **PhD 2** | **Uncertainty quantification + decision framework:** at what confidence should formwork be struck? Converts a prediction into an engineering decision with a stated risk level. |
| **Novelty vs. literature** | Hundreds of papers predict 28-day strength. **Almost none report calibrated uncertainty, and almost none couple ML to the codal maturity method.** A prediction of "38 MPa" is useless; "38.2 ± 4.1 MPa, 90% confidence" is a decision. |
| **6 months** | M1 datasets + baseline · M2 lab casting begins · M3 maturity model · M4 GP residual layer · M5 lab validation · M6 paper + tool |
| **Risk** | 🟢 **Very low.** Public data works even if the lab programme slips. |

**Why this is #1, SIR:** it is the most fundamental unsolved question in concrete practice, it is 100% your professor's domain, the data exists twice over, and it feeds ConcApp directly.

---

## 🥈 PROJECT C2 — Plant-Specific Quality Control: Predicting the Failing Batch

**The problem — and this is the strongest industry hook on this list:** Indian RMC plants show σ from **1.92 to 6.57 MPa**. IS 456 requires target mean strength = f_ck + 1.65σ. **A plant with σ = 6.57 must overdesign by ~10.8 MPa; a plant with σ = 1.92 needs only 3.2 MPa.** That difference is enormous cement wastage — or, if the plant underestimates its own σ, systematic non-compliance.

**Objective:** An AI quality-control system that (a) continuously estimates true plant σ, (b) flags an out-of-control batch **before** the 28-day result, and (c) recommends the minimum safe target mean strength.

| | |
|---|---|
| **Data — day one** | Published RMC plant datasets in the Indian literature (the NBM&CW study tabulates multi-grade, multi-plant strength data). **Any local Bhubaneswar/Cuttack RMC plant will share historical cube data for a free quality report** — a single plant, not a government agency. **Your own lab can simulate controlled variability.** |
| **B.Tech 1–2** | Implement CUSUM and Shewhart control charts (existing industry practice) as the baseline to beat |
| **B.Tech 3–4** | ML anomaly detection on batch records; dashboard |
| **PhD 1** | **Novel:** **Bayesian online estimation of plant σ** that updates with every cube result, replacing the static assumed σ in IS 456. Directly attacks a real codal weakness. |
| **PhD 2** | **Cement-saving quantification:** how many kg/m³ of cement does better σ estimation save at constant reliability? **Converts statistics into rupees and CO₂ — this makes the paper citable outside academia.** |
| **Novelty** | Six Sigma and CUSUM studies exist for Indian RMC. **Bayesian adaptive σ with a quantified cement-saving outcome does not.** |
| **Risk** | 🟡 Plant data access — mitigated by using published datasets + lab simulation. **One friendly plant manager is enough. No agency involved.** |

---

## 🥉 PROJECT C3 — Chloride & Carbonation Durability Prediction for Coastal Odisha

**The problem:** Bhubaneswar/Puri/Paradip is a **severe marine exposure** environment. IS 456 gives prescriptive rules (min cement, max w/c, cover) but **no way to predict actual service life** for a given mix in a given exposure. Coastal RCC in Odisha deteriorates far faster than design assumes.

**Objective:** Predict chloride diffusion coefficient and carbonation depth from mix composition, and convert these to **time-to-corrosion-initiation** for Odisha exposure conditions.

| | |
|---|---|
| **Data — day one** | **Open-access carbonation dataset** (20,000 synthetic instances from the validated Possan equation, published 2025, benchmark available online). Extensive published chloride diffusion data. **Your own lab: RCPT (ASTM C1202), accelerated carbonation, water absorption — all standard, all fast.** |
| **B.Tech 1–2** | Lab: RCPT and accelerated carbonation on 30–40 mixes with varying SCM content |
| **B.Tech 3–4** | Compile literature durability dataset; train predictive models |
| **PhD 1** | **Novel:** **Odisha-specific service-life model** — couple Fick's second law with locally measured diffusion coefficients and actual coastal temperature/humidity. **Nobody has done this for this coastline.** |
| **PhD 2** | Probabilistic service life with uncertainty — *"cover of 50 mm gives 80% probability of >50 years at Paradip"* |
| **Why it wins** | 🎯 **Geographically unique to you, but requires zero external permission** — the sea is not an agency. Highly publishable, directly relevant to Odisha PWD later. |
| **Risk** | 🟢 Low. Accelerated tests fit comfortably in 6 months. |

---

## PROJECT C4 — SCM Substitution Optimiser (Fly Ash / GGBS / Silica Fume)

**The problem:** Every plant must reduce cement for cost and carbon. But SCM replacement affects strength gain rate, workability, durability and setting time **simultaneously and non-linearly** — and fly ash quality varies by source. Engineers use rules of thumb (30% fly ash, 50% GGBS) that are frequently far from optimal.

**Objective:** Multi-objective optimiser returning Pareto-optimal SCM combinations for **strength ⟷ cost ⟷ CO₂ ⟷ durability**.

| | |
|---|---|
| **Data** | UCI dataset **already contains blast furnace slag and fly ash as explicit variables**. BOxCrete has systematic SCM replacement levels. Lab: 30–40 ternary blends. |
| **B.Tech 1–2** | Lab programme on ternary blends (OPC + fly ash + GGBS) |
| **B.Tech 3–4** | Property prediction models + cost/CO₂ database for Odisha suppliers |
| **PhD 1** | **Novel:** NSGA-II multi-objective optimisation with **precursor chemistry vectorisation** — encode SiO₂/Al₂O₃/CaO/fineness rather than the material *name*, so the model generalises to any new SCM source. *(This directly addresses the fly-ash depletion risk documented in `concapp-deep-risk-register.md` §0.2 — India is at ~96% fly ash utilisation.)* |
| **PhD 2** | Regional cost & carbon accounting — *"is low-carbon concrete actually cheaper in Odisha?"* The literature spread is **−40% to +300%**; nobody has answered it locally. |
| **Why it wins** | Feeds ConcApp directly; strong sustainability angle for funding; pure materials science |
| **Risk** | 🟡 Ternary blend lab work is time-consuming → **restrict to 3 SCM levels × 3 w/c ratios**, not a full factorial. |

---

## PROJECT C5 — Computer Vision for Fresh Concrete Workability

**The problem:** The slump test is **destructive of time, subjective, and measures one instant**. IS 1199 slump is the universal acceptance test yet correlates poorly with actual pumpability and placeability. Rejections at site over slump disputes are routine and expensive.

**Objective:** Estimate slump and flow from a **smartphone video** of the concrete discharge or slump cone collapse.

| | |
|---|---|
| **Data** | 🟢 **Entirely self-generated — the strongest data position on this list.** Every slump test your lab performs = one labelled video. 200–300 samples in 3 months is easily achievable. |
| **B.Tech 1–2** | Video capture protocol; slump cone collapse dynamics extraction |
| **B.Tech 3–4** | CNN/video model; correlate with measured slump and flow |
| **PhD 1** | **Novel:** relate **collapse kinematics** (rate and shape of deformation, not just final height) to **rheological parameters** — yield stress and plastic viscosity. This is a genuine research contribution linking vision to rheology. |
| **PhD 2** | Field robustness: lighting, camera angle, mix colour variation. Uncertainty bounds. |
| **Why it wins** | ✅ **Zero data dependency whatsoever.** Visually impressive for demonstrations. Immediately deployable at any site. |
| **Risk** | 🟡 Video ML needs more compute than tabular → **use a small model on extracted features, not raw video frames.** Colab free tier suffices. |

---

## PROJECT C6 — Aggregate Gradation & Shape Analysis by Image

**The problem:** *"Using poor-quality aggregates often results in concrete 15–20% weaker than required."* Sieve analysis (IS 383/IS 2386) takes hours per sample, so plants test infrequently and **aggregate variation goes undetected** — a direct cause of the strength scatter measured in Indian plants.

**Objective:** Instant gradation curve, flakiness and elongation indices from a photograph of an aggregate sample.

| | |
|---|---|
| **Data** | 🟢 **Self-generated.** Photograph a sample, then sieve it. Photograph = input, sieve result = label. **100–200 samples is a few weeks of routine lab work.** |
| **B.Tech 1–2** | Imaging rig (a phone, a tray, controlled light — total cost near zero); particle segmentation |
| **B.Tech 3–4** | Size distribution estimation, calibration against IS 383 sieve results |
| **PhD 1** | **Novel:** correcting the **2D-to-3D bias** — image analysis sees projected area, sieving measures passage through a square aperture. Rigorous treatment of this is a real methodological gap. |
| **PhD 2** | Link measured shape/gradation to **fresh and hardened concrete properties** — closing the loop from aggregate image to concrete performance |
| **Why it wins** | Cheapest possible setup; solves a documented cause of Indian strength scatter; deployable in any plant |
| **Risk** | 🟡 Overlapping particles are the classic hard case → **impose a single-layer spreading protocol** in the imaging procedure. Design the constraint out. |

---

# RANKING FOR YOUR SITUATION

| # | Project | Data risk | Lab burden | Novelty | Professor fit | ConcApp link | Verdict |
|---|---|---|---|---|---|---|---|
| **C1** | Early-age strength | 🟢 **None** (2 public datasets) | 🟡 Medium | 🟢 High | 🟢 **Perfect** | 🟢 **Direct** | 🥇 **Build this** |
| **C5** | Vision workability | 🟢 **Self-generated** | 🟢 Low | 🟢 High | 🟢 Strong | 🟡 Indirect | 🥇 **Safest** |
| **C3** | Coastal durability | 🟢 Low | 🟡 Medium | 🟢 High | 🟢 Strong | 🟡 Indirect | 🥈 Best local angle |
| **C2** | Plant QC | 🟡 One plant needed | 🟢 Low | 🟢 High | 🟢 Strong | 🟢 Direct | 🥈 Best industry hook |
| **C4** | SCM optimiser | 🟢 Low | 🔴 **Heavy** | 🟡 Moderate | 🟢 Perfect | 🟢 **Direct** | 🥉 Lab-time risk |
| **C6** | Aggregate imaging | 🟢 **Self-generated** | 🟢 Low | 🟡 Moderate | 🟡 Moderate | 🟡 Indirect | 🥉 Good, less novel |

## 🎯 ULTRON'S RECOMMENDATION: RUN **C1 + C5** IN PARALLEL

**C1 (Early-age strength)** — the flagship.
- Two public datasets mean **work starts on day one**, before a single cube is cast
- Squarely your professor's discipline; he will want authorship
- Feeds ConcApp
- The hybrid maturity+GP method is the publishable core

**C5 (Vision workability)** — the insurance policy.
- **Generates 100% of its own data** from tests the lab already performs
- Cannot be blocked by anyone
- Visually striking for a demo or presentation
- If C1's lab programme slips, C5 still delivers a complete result

**Team split:** PhD 1 + 2 B.Tech on C1 · PhD 2 + 2 B.Tech on C5. They share the same lab sessions — **the same concrete batch that produces a cube for C1 produces a slump video for C5.** One lab programme, two projects, two papers.

> 💡 **That shared-batch design is the key efficiency, SIR.** It halves the lab burden and makes the six-month deadline comfortable rather than tight.

---

# HOW TO PITCH C1 TO YOUR PROFESSOR

Not as an AI project. **As a concrete technology project that happens to use AI.**

> *"Sir, we know the maturity method under-predicts for mixes with high SCM content, and IS 516 gives us no way to account for plant-specific material variability. I want to test whether a maturity function calibrated with a small correction model can predict 28-day strength from 7-day data with a stated confidence interval — so that formwork stripping becomes a decision with a known risk level rather than a rule of thumb. We can validate it on two public datasets immediately and on our own mixes over the semester."*

**Why this framing works:**
- ✅ Opens with a **concrete technology gap**, not a technology
- ✅ Cites **IS 516** and the **maturity method** — his vocabulary, not a computer scientist's
- ✅ Proposes a **testable hypothesis**, not a tool
- ✅ Says data exists **immediately** — removes his main risk
- ✅ Ends in a **practical decision** (formwork stripping) that every site engineer cares about
- ❌ The words "artificial intelligence" appear nowhere

> If he is a concrete man, he does not want an AI project. **He wants a concrete problem solved, with whatever tool works.** Lead with the concrete.

---

# NON-NEGOTIABLES FOR THE TEAM

1. **Week 1: download UCI and BOxCrete, reproduce a published baseline.** Before any lab work. This proves the pipeline works and de-risks everything downstream.
2. **A written baseline metric before modelling.** The #1 documented cause of AI project failure is having no baseline to beat.
3. **Leave-one-mix-out validation**, never random splits. Random splits on concrete data leak information between curing ages of the same mix and produce fictional R² values. **This single error invalidates a large fraction of published concrete-ML papers — avoiding it is itself a contribution.**
4. **Report uncertainty always.** A point prediction is not an engineering output.
5. **Git from hour one.** Not month three.
6. **Log every mix in a fixed schema** from the first batch. Retro-fitting a data schema after 40 mixes have been cast is the most common practical disaster in lab-based ML projects.
