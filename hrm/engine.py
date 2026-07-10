from __future__ import annotations

from dataclasses import dataclass

from hrm.chaos_stabilizer import ChaosStabilizer
from hrm.diagnostics import compute_full_invariants
from hrm.fields import evolve_fields
from hrm.mesh import SimplicialMesh
from hrm.symbolic_state import update_symbolic_state


@dataclass
class SimulationConfig:
    steps: int = 500
    base_dt: float = 0.002
    checkpoint_steps: tuple[int, ...] = (0, 1, 100, 500)
    enable_edge_flips: bool = True
    seed: int = 7


class HRMEngine:
    def __init__(self, mesh: SimplicialMesh, config: SimulationConfig):
        self.mesh = mesh
        self.config = config
        self.stabilizer = ChaosStabilizer(base_dt=config.base_dt)

        self.energy_history: list[float] = []
        self.chaos_history: list[float] = []
        self.nonmanifold_history: list[int] = []

        self.flip_attempts = 0
        self.flip_successes = 0
        self.flip_rejected_link = 0
        self.flip_rejected_duplicate = 0
        self.flip_blocked_chaos = 0

    def run(self) -> None:
        self.mesh.heal_initial_artifacts()
        self.mesh.orient_faces_consistently()
        self.mesh.validate_initial_state()

        self._record_checkpoint(0)

        for step in range(1, self.config.steps + 1):
            energy = self.mesh.free_energy()
            chaos = self.stabilizer.measure(
                energy=energy,
                field=self.mesh.fields,
                state=self.mesh.state_vector,
            )
            control = self.stabilizer.control(chaos)

            evolve_fields(
                mesh=self.mesh,
                dt=control.dt,
                damping=control.damping,
            )

            self.mesh.state_vector = update_symbolic_state(
                self.mesh.state_vector,
                self.mesh.fields,
            )

            if self.config.enable_edge_flips:
                self._attempt_safe_flip(control.surgery_allowed)

            self.energy_history.append(self.mesh.free_energy())
            self.chaos_history.append(chaos)
            self.nonmanifold_history.append(
                self.mesh.count_nonmanifold_vertices()
            )

            if step in self.config.checkpoint_steps:
                self._record_checkpoint(step)

    def _attempt_safe_flip(self, surgery_allowed: bool) -> None:
        if not surgery_allowed:
            self.flip_blocked_chaos += 1
            return

        candidate = self.mesh.select_stressed_interior_edge()
        if candidate is None:
            return

        self.flip_attempts += 1

        result = self.mesh.try_edge_flip(candidate)

        if result.accepted:
            self.flip_successes += 1
        elif result.reason == "link_condition":
            self.flip_rejected_link += 1
        elif result.reason == "duplicate_diagonal":
            self.flip_rejected_duplicate += 1

    def _record_checkpoint(self, step: int) -> None:
        invariants = compute_full_invariants(self.mesh)
        print(f"\n--- Mesh Invariants at Step {step} ---")
        print(invariants.to_text())
