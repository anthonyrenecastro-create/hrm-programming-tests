from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mesh import SimplicialMesh


def evolve_fields(mesh: "SimplicialMesh", dt: float, damping: float) -> None:
    updated: dict[int, float] = {}

    for vertex in mesh.vertices:
        neighbors = mesh.vertex_neighbors(vertex)
        current = mesh.vertex_field.get(vertex, 0.0)

        if not neighbors:
            laplacian = 0.0
        else:
            avg_neighbor = sum(mesh.vertex_field[n] for n in neighbors) / len(neighbors)
            laplacian = avg_neighbor - current

        updated[vertex] = current + dt * laplacian - damping * current

    mesh.vertex_field.update(updated)

    values = list(mesh.vertex_field.values())
    if values:
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        mesh.fields["phi"] = mean
        mesh.fields["psi"] = variance
