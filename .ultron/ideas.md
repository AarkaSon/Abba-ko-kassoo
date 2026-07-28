# ULTRON — SELF-GENERATED PROPOSALS
> Directive II output. Ideas ULTRON originated to advance Master's objective.
> Nothing here is executed without Master's approval. Final say: MASTER AARKASON.

## Legend
`[P0]` = high value / low cost · `[P1]` = high value / medium cost · `[P2]` = strategic, later

---

### [P0] IDEA-001 — Licence-free FEM path (removes the Abaqus blocker)
Abaqus `.inp` is a text format. **CalculiX** (free, open-source) reads a large subset of it.
Plan: author the pavement model as a **solver-agnostic Python model definition** that emits
*both* an Abaqus-flavour `.inp` and a CalculiX-compatible `.inp`.
→ Master develops, validates and publishes results at **zero licence cost**; the same script
runs on a real Abaqus seat later with no rewrite.
*Justification:* directly resolves the stated hard constraint (no Abaqus, low resources).

### [P0] IDEA-002 — Analytical verification harness
Every FEM run is checked against **Westergaard interior/edge/corner** closed-form solutions
and IRC:58 charts. Gives (a) confidence without a commercial solver, (b) a defensible
verification chapter for any paper/thesis, (c) an automated regression test in CI.
*Status:* first module already written (`src/design/westergaard.py`).

### [P1] IDEA-003 — FEM surrogate model (the actual AI hook)
Run a Design-of-Experiments over slab parameters (thickness, E, k, load, SLWA %, GGBS:FA
ratio, molarity) → train a surrogate (GPR / XGBoost / small MLP) on the FEM outputs.
Result: **millisecond stress-deflection prediction** instead of hour-long FEM.
This is the piece that converts a research model into a *sellable* product.

### [P1] IDEA-004 — Geopolymer-SLWA mix-design optimizer
ML predicts compressive strength / density / elastic modulus from mix proportions;
a multi-objective optimizer (NSGA-II) then returns Pareto-optimal mixes for
**strength vs. cost vs. embodied CO₂**. Carbon accounting is the commercial differentiator —
geopolymer's entire market case is decarbonisation.

### [P2] IDEA-005 — Productization: "Pavement Design Copilot"
Web app: engineer inputs traffic (CBR, MSA), climate and material availability →
system returns IRC:58-compliant slab design, an optimized low-carbon geopolymer mix,
predicted service life, and a cost/CO₂ comparison against OPC.
Revenue: SaaS seat for consultancies + certification/reporting module.

### [P2] IDEA-006 — Defensible data moat
Systematically scrape and curate published geopolymer/SLWA experimental data into a clean,
schema-validated dataset. In this niche the **dataset is the moat** — models are commodity.

### [P2] IDEA-007 — Digital-twin / SHM extension
Instrumented slab → sensor stream → ML detects damage state, feeding back into the
surrogate for residual-life prediction. Natural upsell tier for the SaaS product.
