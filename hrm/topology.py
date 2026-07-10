from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mesh import SimplicialMesh


def euler_characteristic(mesh: "SimplicialMesh") -> int:
    return len(mesh.vertices) - len(mesh.edges) + len(mesh.faces)


def boundary_vertices(mesh: "SimplicialMesh") -> list[int]:
    return [v for v in mesh.vertices if mesh.is_boundary_vertex(v)]


def manifold_vertices(mesh: "SimplicialMesh") -> list[int]:
    return [v for v in mesh.vertices if mesh.vertex_link_is_manifold(v)]
