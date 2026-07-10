from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from hrm.engine import HRMEngine, SimulationConfig
from hrm.mesh import SimplicialMesh
from hrm.visualization import (
    plot_flagged_boundary_vertices,
    plot_history,
    plot_mesh,
)


def main() -> None:
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    mesh = SimplicialMesh.from_regular_grid(width=8, height=8, seed=7)
    config = SimulationConfig(steps=500, base_dt=0.002)
    engine = HRMEngine(mesh=mesh, config=config)
    engine.run()

    energy_path, _ = plot_history(engine, results_dir)
    final_path = plot_mesh(mesh, results_dir / "final_manifold_state.png", title="Final Manifold State")
    boundary_path = plot_flagged_boundary_vertices(
        mesh,
        results_dir / "flagged_boundary_vertices.png",
    )

    payload = {
        "steps": config.steps,
        "seed": config.seed,
        "energy_final": engine.energy_history[-1] if engine.energy_history else None,
        "chaos_final": engine.chaos_history[-1] if engine.chaos_history else None,
        "flip_attempts": engine.flip_attempts,
        "flip_successes": engine.flip_successes,
        "flip_rejected_link": engine.flip_rejected_link,
        "flip_rejected_duplicate": engine.flip_rejected_duplicate,
        "flip_blocked_chaos": engine.flip_blocked_chaos,
        "artifacts": {
            "energy_plot": str(energy_path),
            "final_state_plot": str(final_path),
            "boundary_plot": str(boundary_path),
        },
    }

    with (results_dir / "reference_run.json").open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


if __name__ == "__main__":
    main()
