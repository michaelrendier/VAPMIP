# j2_involution — every J_2 calculation, application, and design spec on record

Copied from `VAPMIP/`, `Ainulindale/`, and `ValaQuenta/`, 2026-09-21, per
the author's explicit instruction: this paper's §9.5 states only the
exact, checkable claim (`J_2`, not `J_N`, is the crossing's real
symmetry) and keeps this project's wider framework out of its own prose
— a desk-rejection judgment about what a first CS preprint should say,
not a restriction on the code. Everything the project has on `J_2` is
included here in full.

- **`e09_j2_involution.py`** — the engine. Calculations, not narrative.
- **`51_j2_involution_riemann_fermat.md`** — design specification,
  Ainulindale wiki 51: the formal `J_2` definition this paper's §9.5
  cites.
- **`60_heart_j2_involution.md`** — design specification, Ainulindale
  wiki 60: `J_2` at the heart of the wider framework.
- **`14_heart_j2_involution.ipynb`** — application notebook,
  `ValaQuenta/notebooks/core/`.
- **`method2_j2_involution_t256.ipynb`** — application notebook,
  `ValaQuenta/notebooks/udeo_crypto/`: `J_2` used as one of five
  compared methods in a cryptographic context. Included for
  completeness as an application of the same maths; not part of this
  paper's own claim and not endorsed or exercised by anything this
  paper ships.
