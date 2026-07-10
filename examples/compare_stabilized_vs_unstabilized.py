from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from hrm.engine import HRMEngine, SimulationConfig
from hrm.mesh import SimplicialMesh


def run_case(enable_edge_flips: bool) -> tuple[float, int]:
    mesh = SimplicialMesh.from_regular_grid(width=8, height=8, seed=7)
    config = SimulationConfig(steps=250, base_dt=0.002, enable_edge_flips=enable_edge_flips)
    engine = HRMEngine(mesh=mesh, config=config)
    engine.run()
    final_energy = engine.energy_history[-1] if engine.energy_history else float("nan")
    return final_energy, engine.flip_successes


def main() -> None:
    stabilized_energy, stabilized_flips = run_case(enable_edge_flips=True)
    baseline_energy, baseline_flips = run_case(enable_edge_flips=False)

    print("Stabilized (edge flips enabled)")
    print(f"  Final energy: {stabilized_energy:.6f}")
    print(f"  Successful flips: {stabilized_flips}")

    print("Unstabilized (edge flips disabled)")
    print(f"  Final energy: {baseline_energy:.6f}")
    print(f"  Successful flips: {baseline_flips}")


if __name__ == "__main__":
    main()
