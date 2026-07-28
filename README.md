# Abba-ko-kassoo
**AI-augmented structural analysis of geopolymer rigid pavement slabs using Sintered Lightweight Aggregate (SLWA).**

> Long-term objective: a commercially viable platform integrating **Artificial Intelligence**
> with **Civil / Pavement Engineering**. This repository is the technical seed of that venture.
> Every artifact here is built to production standards, not as throwaway academic code.

---

## 1. Problem Statement

Conventional OPC rigid pavements are carbon-intensive (~0.9 t CO₂ per t of clinker) and heavy.
**Geopolymer concrete** (fly ash / GGBS activated by alkaline solution) with **SLWA** offers:

| Lever | Effect |
|---|---|
| Clinker elimination | 40–80 % reduction in embodied CO₂ |
| Sintered lightweight aggregate | 20–30 % lower self-weight → lower slab stresses |
| Industrial by-product reuse | Fly ash / GGBS / sintered ash valorisation |

**The gap:** geopolymer-SLWA has no mature design framework for rigid pavements, and FEM
validation is slow and licence-bound. **This project closes that gap with a hybrid
FEM + machine-learning pipeline.**

## 2. Approach

```
  Literature & experimental data
              │
              ▼
   [1] Material characterisation  ──►  ML models: fck, E, ρ, ft, CO₂, cost
              │
              ▼
   [2] Analytical design (IRC:58 / Westergaard)   ◄── verification baseline
              │
              ▼
   [3] FEM slab model (solver-agnostic .inp: Abaqus | CalculiX)
              │
              ▼
   [4] DoE sweep  ──►  Surrogate model (ms-scale stress/deflection prediction)
              │
              ▼
   [5] Multi-objective optimisation: strength ⟷ cost ⟷ CO₂
              │
              ▼
   [6] Product layer: Pavement Design Copilot
```

## 3. Repository Layout

```
.ultron/            ULTRON assistant memory: master profile, worklog, idea backlog
docs/
  references/       Source PDFs, papers, codes supplied by the Master  (+ INDEX.md)
  notes/            Distilled notes / extracted text from each reference
data/
  raw/              Immutable source data (git-ignored)
  processed/        Cleaned, schema-validated datasets
  external/         Third-party datasets (git-ignored)
src/
  materials/        Geopolymer + SLWA constitutive & mix-design models
  design/           Code-based design: IRC:58, Westergaard, AASHTO
  fem/abaqus/       Abaqus scripting (.inp authoring, CAE kernel, ODB post-processing)
  fem/calculix/     Free-solver fallback path
  ml/               Datasets, surrogates, optimisers
notebooks/          Exploration
results/            Figures & tables (regenerable, git-ignored)
tests/              Verification against closed-form solutions
scripts/            Utilities (PDF ingestion, batch runs)
```

## 4. Environment Status

| Component | Status |
|---|---|
| Python 3.11 | ✅ available |
| Analytical design modules | ✅ implemented, zero dependencies |
| **Abaqus** | ⛔ **NOT AVAILABLE — SETUP DEFERRED.** Models are authored as text `.inp` decks + Python scripts, executable later on any Abaqus seat. |
| CalculiX (free `.inp`-compatible solver) | 🔜 planned fallback so development is never licence-blocked |
| ML stack | 🔜 CPU-only, minimal dependencies |

**Design principle adopted because of this constraint:** the FEM layer is *solver-agnostic*.
The model is defined once in Python and emitted to whichever solver is available.

## 5. Quick Start

```bash
python3 -m pip install -r requirements.txt      # optional; core modules are dependency-free

# Analytical rigid-pavement check (no solver needed)
python3 src/design/westergaard.py

# File a reference PDF into the repository and extract its text
python3 scripts/ingest_pdf.py /path/to/paper.pdf --tag geopolymer
```

## 6. Roadmap

- [x] Project skeleton, memory layer, ignore rules
- [x] Analytical Westergaard / IRC:58 baseline
- [ ] Ingest Master's supplied literature
- [ ] Geopolymer-SLWA material property model
- [ ] Solver-agnostic slab `.inp` generator
- [ ] CalculiX verification run
- [ ] DoE + surrogate model
- [ ] Multi-objective mix optimiser
- [ ] Product layer

## 7. License
See [LICENSE](LICENSE).
