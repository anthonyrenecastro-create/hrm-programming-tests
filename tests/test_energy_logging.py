from hrm.engine import HRMEngine, SimulationConfig
from hrm.mesh import SimplicialMesh


def test_energy_and_chaos_histories_are_logged() -> None:
    mesh = SimplicialMesh.from_regular_grid(width=5, height=5, seed=7)
    engine = HRMEngine(mesh, SimulationConfig(steps=12, enable_edge_flips=False))
    engine.run()

    assert len(engine.energy_history) == 12
    assert len(engine.chaos_history) == 12
    assert len(engine.nonmanifold_history) == 12
    assert all(value >= 0.0 for value in engine.energy_history)
