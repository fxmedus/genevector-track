<p align="center">
  <strong>GeneVector Thesis Track</strong><br>
  <em>A Four-Paper Framework for Computational Drug Discovery Evaluation and Translational Gap Resolution</em>
</p>

<p align="center">
  <a href="https://github.com/fxmedus/genevector-track/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="License"></a>
  <a href="https://orcid.org/0009-0001-9929-3135"><img src="https://img.shields.io/badge/ORCID-0009--0001--9929--3135-a6ce39?style=flat-square&logo=orcid&logoColor=white" alt="ORCID"></a>
  <a href="https://doi.org/10.2139/ssrn.6796779"><img src="https://img.shields.io/badge/SSRN-P1%20TCDR-154360?style=flat-square" alt="SSRN P1"></a>
  <a href="https://doi.org/10.2139/ssrn.6796818"><img src="https://img.shields.io/badge/SSRN-P3%20Case%20Series-154360?style=flat-square" alt="SSRN P3"></a>
  <a href="https://doi.org/10.2139/ssrn.6796898"><img src="https://img.shields.io/badge/SSRN-P4%20ERI-154360?style=flat-square" alt="SSRN P4"></a>
  <img src="https://img.shields.io/badge/Papers-4%2F4%20Complete-success?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
</p>

---

## Overview

This repository contains the complete research artifacts for the GeneVector thesis track: a four-paper series establishing a standards-based framework for evaluating therapeutic candidates in computational drug discovery and quantifying translational readiness.

The framework introduces two standards (TCDR, ERI) and validates them against a 20-candidate mitochondrial disease portfolio, providing a reproducible methodology for identifying and resolving evidence gaps that separate computational predictions from clinical translation.

**Author:** Julian Yin Vieira Borges, MD, MS
**Affiliation:** Independent Research Laboratory (FxMEDUS LLC). MSHI Candidate, Department of Computer Science, Boston University.
**Contact:** jyborges@bu.edu
**ORCID:** [0009-0001-9929-3135](https://orcid.org/0009-0001-9929-3135)

---

## Thesis Arc

| Paper | Title | Core Contribution |
|:---:|-------|-------------------|
| **P1** | The Therapeutic Candidate Decision Record (TCDR) | A representation standard (58 fields, 9 groups) for structured therapeutic candidate documentation. |
| **P2** | The TCDR Engine | Computational architecture for reproducible multi-criteria evaluation. 6 components, MAE = 0.010. |
| **P3** | MitoCoreX Case Series | Pipeline validation: 20 candidates, 7 dimensions, Pareto frontier of 6 identified. |
| **P4** | The Evidence Readiness Index (ERI) | Budget-constrained optimization for translational gap resolution. |

### Dependency Chain

```
P1 (TCDR Standard)     P2 (TCDR Engine)     P3 (Case Series)      P4 (ERI)
┌─────────────────┐    ┌────────────────┐    ┌──────────────────┐   ┌──────────────────┐
│ 58 fields        │───>│ 6 components   │───>│ 20 candidates    │──>│ 8 evidence gaps  │
│ 9 groups         │    │ MAE = 0.010    │    │ 7 dimensions     │   │ budget optimizer │
│ 12/12 validation │    │ 15/15 tests    │    │ Pareto 6         │   │ $250K inflection │
│ TCDR-MI checklist│    │ reproducible   │    │ 18/18 tests      │   │ 15/15 tests      │
└─────────────────┘    └────────────────┘    └──────────────────┘   └──────────────────┘
     defines                computes              identifies             resolves
     language               scores                gaps                   gaps optimally
```

---

## Key Findings

**D4 Evidence Gap:** 0.54-point disparity between novel (0.22) and approved (0.76) candidates on evidence maturity, identifying experimental validation as the critical translational bottleneck.

**Dependency Cost Inversion:** The evidence gap with highest standalone ROI is not optimal at constrained budgets when inter-gap dependency costs are modeled.

**$250K Inflection Point:** Minimum investment to transition a computational portfolio from prediction-only to experimentally validated status, producing a 5.3-fold jump in portfolio evidence value.

**77% Value Capture at $500K:** Resolving 4 of 8 evidence gaps captures 77% of maximum achievable portfolio improvement.

---

## Repository Structure

```
genevector-track/
├── paper1-tcdr-standards/            # P1: TCDR representation standard
│   └── PAPER_GV1_TCDR_STANDARDS_v3.2_FINAL.docx
├── paper2-tcdr-engine/               # P2: Computational scoring engine
│   └── PAPER_GV2_TCDR_ENGINE_R3_FINAL.docx
├── paper3-mitocorex-case-series/     # P3: 20-candidate validation
│   └── PAPER_GV3_MITOCOREX_CASE_SERIES_R3_FINAL.docx
├── paper4-evidence-readiness-index/  # P4: Budget optimization framework
│   ├── PAPER_GV4_ERI_FRAMEWORK_R2_FINAL.docx
│   ├── gap_registry.yaml             #   8 evidence gaps formalized
│   ├── cost_benchmarks.yaml          #   CRO/facility cost estimates
│   └── eri_engine.py                 #   ERI computation engine
├── schemas/
│   ├── tcdr_schema_v1.0.yaml         #   TCDR representation schema
│   └── tcdr_mi_v1.0.yaml             #   TCDR Minimum Information checklist
├── CITATION.cff                      #   Machine-readable citation
├── LICENSE                           #   Apache 2.0
└── README.md
```

---

## Preprint Status

| Paper | Preprint | Status |
|:---:|----------|--------|
| P1 — TCDR Standard | [SSRN 6796779](https://doi.org/10.2139/ssrn.6796779) | Available |
| P2 — TCDR Engine | Pending (IP review) | In preparation |
| P3 — MitoCoreX Case Series | [SSRN 6796818](https://doi.org/10.2139/ssrn.6796818) | Available |
| P4 — Evidence Readiness Index | [SSRN 6796898](https://doi.org/10.2139/ssrn.6796898) | Available |

---

## Standards

### TCDR (Therapeutic Candidate Decision Record)

A structured representation standard for therapeutic candidates in computational drug discovery. 58 fields, 9 groups, with a Minimum Information (TCDR-MI) checklist for completeness and reproducibility.

**Schema:** [`schemas/tcdr_schema_v1.0.yaml`](schemas/tcdr_schema_v1.0.yaml) · **MI Checklist:** [`schemas/tcdr_mi_v1.0.yaml`](schemas/tcdr_mi_v1.0.yaml)

### ERI (Evidence Readiness Index)

A quantitative framework for measuring translational readiness and optimizing evidence-generation investment under budget constraints.

**Engine:** [`paper4-evidence-readiness-index/eri_engine.py`](paper4-evidence-readiness-index/eri_engine.py) · **Gap Registry:** [`paper4-evidence-readiness-index/gap_registry.yaml`](paper4-evidence-readiness-index/gap_registry.yaml)

---

## Related Work

| Resource | Link |
|----------|------|
| AIDD-GOV Open Governance Standard | [github.com/fxmedus/aidd-gov](https://github.com/fxmedus/aidd-gov) |
| Harvard Dataverse | [10.7910/DVN/WGHUWM](https://doi.org/10.7910/DVN/WGHUWM) |
| US Provisional Patent | 64/018,624 (filed 2026-03-27) |

---

## Intellectual Property

Released under Apache 2.0. The TCDR and ERI frameworks are part of US Provisional Patent Application 64/018,624. Research use is permitted and encouraged. Scoring weights, reward functions, and proprietary compound data are excluded from this repository.

---

## Citation

```bibtex
@misc{borges2026genevector,
  author       = {Borges, Julian Yin Vieira},
  title        = {GeneVector Thesis Track: A Four-Paper Framework for Computational
                  Drug Discovery Evaluation and Translational Gap Resolution},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/fxmedus/genevector-track},
  note         = {TCDR Standard (SSRN 6796779), MitoCoreX Case Series (SSRN 6796818),
                  Evidence Readiness Index (SSRN 6796898)}
}
```

---

<p align="center">
  <a href="https://julian-borges-md.github.io/frontier-lab/"><img src="https://img.shields.io/badge/Lab-Frontier%20Translational%20Research-002244?style=flat-square" alt="Lab"></a>
  <a href="https://www.bu.edu/cs/"><img src="https://img.shields.io/badge/BU-Computer%20Science-cc0000?style=flat-square" alt="BU CS"></a>
  <a href="https://ghsm.hms.harvard.edu/education/global-clinical-scholars-research-training"><img src="https://img.shields.io/badge/HMS-GCSRT%20Alumni-a51c30?style=flat-square" alt="HMS"></a>
  <a href="https://orcid.org/0009-0001-9929-3135"><img src="https://img.shields.io/badge/ORCID-0009--0001--9929--3135-a6ce39?style=flat-square&logo=orcid&logoColor=white" alt="ORCID"></a>
</p>

<p align="center"><em>Julian Yin Vieira Borges, MD, MS · jyborges@bu.edu</em></p>
