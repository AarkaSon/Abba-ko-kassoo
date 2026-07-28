# Deferred Setup Register

Items postponed by **MASTER AARKASON** or blocked by the current environment.
ULTRON tracks these so nothing is silently lost. Nothing here blocks present progress.

---

## D-01 · Abaqus availability — **BLOCKED (no licence, low resources)**

| | |
|---|---|
| **Impact** | Cannot execute FEM runs locally. |
| **Does it stop work?** | **No.** Model definition, `.inp` authoring and post-processing are all developed and unit-tested without the solver. |

**Mitigation ladder (cheapest first):**

1. **Analytical baseline — DONE.** `src/design/westergaard.py` gives verified
   closed-form stress/deflection with zero dependencies. Already covers linear-elastic
   slab-on-Winkler behaviour.
2. **CalculiX (`ccx`) — recommended next.** Free, open-source, reads a large subset of
   the Abaqus `.inp` keyword format. Handles static, nonlinear-material and dynamic
   analyses. Runs on a modest CPU. → Lets you produce *real FEM results* at zero cost.
   Install: `apt install calculix-ccx` (Debian/Ubuntu) or a prebuilt Windows binary.
3. **Student/academic Abaqus.** Abaqus Student Edition is free but node-limited
   (~1000 nodes) — adequate for a coarse verification slab, not for a fatigue study.
   Full academic licence usually available through a university.
4. **Cloud burst.** Only if 1–3 prove insufficient; incurs cost. Ask Master first.

**Design consequence already adopted:** the FEM layer will be *solver-agnostic* — one
Python model definition emitting both Abaqus- and CalculiX-flavour input decks. No
rewrite is needed when an Abaqus seat becomes available.

---

## D-02 · Analysis type — **DEFERRED by Master ("later stage")**

Options held open; the scaffold does not force a choice:

| Option | Cost | What it buys |
|---|---|---|
| Static linear-elastic | Low | Stress/deflection, direct Westergaard verification |
| Static nonlinear (Concrete Damaged Plasticity) | Medium | Cracking, damage evolution, ultimate capacity |
| Cyclic / fatigue | High | Repeated axle loads, service-life prediction |
| Dynamic / moving load | High | Impact, vehicle–pavement interaction |

**ULTRON's recommendation when Master is ready:** stage them — linear-elastic first
(verifies mesh + boundary conditions against closed-form), then CDP on the validated
mesh. Attempting CDP on an unverified mesh is where most such studies fail.

---

## D-03 · Material property data — **AWAITING MASTER'S PDF**

Placeholders currently in use (`E = 30 GPa`, `mu = 0.15`) are generic OPC values and
**must** be replaced with geopolymer-SLWA values from the literature/experiments Master
supplies. Every placeholder is flagged in-code.

Required parameter set for the FEM model:

| Parameter | Symbol | Status |
|---|---|---|
| Compressive strength | f_ck | pending |
| Flexural strength / modulus of rupture | f_cr | pending |
| Elastic modulus | E | placeholder |
| Poisson's ratio | mu | assumed 0.15 |
| Density (SLWA-reduced) | rho | pending |
| Tensile softening / fracture energy | G_f | pending (needed for CDP) |
| Coefficient of thermal expansion | alpha | pending (needed for warping) |
| Modulus of subgrade reaction | k | project-specific |

---

## D-04 · ML stack — not yet installed

Deliberate. `numpy/pandas/scikit-learn` are listed in `requirements.txt` but nothing is
installed until the surrogate-modelling stage is actually reached, to respect the
low-resource constraint.
