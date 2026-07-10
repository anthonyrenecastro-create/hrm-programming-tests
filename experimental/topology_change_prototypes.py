from __future__ import annotations

from hrm.mesh import SimplicialMesh


def random_flip_probe(iterations: int = 20) -> int:
    mesh = SimplicialMesh.from_regular_grid(width=5, height=5, seed=11)
    accepted = 0

    for _ in range(iterations):
        edge = mesh.select_stressed_interior_edge()
        if edge is None:
            break
        if mesh.try_edge_flip(edge).accepted:
            accepted += 1

    return accepted


if __name__ == "__main__":
    print(f"Accepted flips: {random_flip_probe()}")
