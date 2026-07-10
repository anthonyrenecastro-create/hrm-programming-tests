# HRM Framework Sandbox

Helical Recursive Manifold (HRM) is a hybrid computational framework that couples:

- Continuous field dynamics
- Discrete symbolic state updates
- Topology-aware geometric adaptation

This repository is a sandbox for experimenting with bounded, self-organizing computation on an evolving simplicial manifold.

## Features

- Deterministic reference simulation via `HRMEngine`
- Edge-flip surgery with geometric validity checks
- Chaos-aware stabilizer that adapts time step and damping
- Invariant diagnostics and history logging
- Unit tests for manifold and topology constraints

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python examples/run_reference_simulation.py
```

## Repository Layout

- `hrm/`: core sandbox implementation
- `examples/`: runnable scripts
- `notebooks/`: notebook walkthroughs
- `tests/`: unit tests
- `results/`: generated artifacts and baseline output
- `experimental/`: unstable prototypes

## Citation

See `CITATION.cff`.

## Zenodo

Zenodo record: TODO (add DOI link after upload)
