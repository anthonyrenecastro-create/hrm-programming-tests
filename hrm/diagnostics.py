from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mesh import SimplicialMesh


@dataclass
class MeshInvariants:
    vertices: int
    edges: int
    faces: int
    euler_characteristic: int
    nonmanifold_vertices: int

    def to_text(self) -> str:
        return (
            f"Vertices: {self.vertices}\n"
            f"Edges: {self.edges}\n"
            f"Faces: {self.faces}\n"
            f"Euler Characteristic: {self.euler_characteristic}\n"
            f"Nonmanifold Vertices: {self.nonmanifold_vertices}"
        )


def compute_full_invariants(mesh: "SimplicialMesh") -> MeshInvariants:
    vertices = len(mesh.vertices)
    edges = len(mesh.edges)
    faces = len(mesh.faces)
    euler = vertices - edges + faces
    nonmanifold = mesh.count_nonmanifold_vertices()
    return MeshInvariants(
        vertices=vertices,
        edges=edges,
        faces=faces,
        euler_characteristic=euler,
        nonmanifold_vertices=nonmanifold,
    )
