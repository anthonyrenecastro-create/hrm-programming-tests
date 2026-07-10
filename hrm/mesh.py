from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import math
import random
from typing import Iterable


def canonical_edge(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


@dataclass(frozen=True)
class FlipResult:
    accepted: bool
    reason: str


class Face:
    def __init__(self, i: int, j: int, k: int):
        self.vertices = (i, j, k)

    @property
    def key(self) -> tuple[int, int, int]:
        return tuple(sorted(self.vertices))


class LinkGraph:
    def __init__(self) -> None:
        self.nodes: set[int] = set()
        self._adj: dict[int, set[int]] = defaultdict(set)

    def add_edge(self, a: int, b: int) -> None:
        self.nodes.add(a)
        self.nodes.add(b)
        self._adj[a].add(b)
        self._adj[b].add(a)

    def degree(self, node: int) -> int:
        return len(self._adj.get(node, set()))

    def is_connected(self) -> bool:
        if not self.nodes:
            return False
        start = next(iter(self.nodes))
        seen = {start}
        stack = [start]
        while stack:
            node = stack.pop()
            for nxt in self._adj.get(node, set()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen == self.nodes


class SimplicialMesh:
    def __init__(
        self,
        vertices: dict[int, tuple[float, float]],
        faces: Iterable[tuple[int, int, int]],
        seed: int = 7,
    ):
        self.vertices = vertices
        self.faces = [tuple(face) for face in faces]
        self.seed = seed
        self._rng = random.Random(seed)

        self.fields: dict[str, float] = {"phi": 0.1, "psi": 0.2}
        self.vertex_field: dict[int, float] = {
            v: self._rng.uniform(-0.05, 0.05) for v in self.vertices
        }
        self.state_vector: tuple[float, float, float] = (0.0, 0.0, 0.0)

        self.edges: set[tuple[int, int]] = set()
        self.edge_to_faces: dict[tuple[int, int], list[tuple[int, int, int]]] = {}
        self.vertex_to_faces: dict[int, list[tuple[int, int, int]]] = {}
        self.rebuild_topology()

    @classmethod
    def from_regular_grid(
        cls,
        width: int = 3,
        height: int = 3,
        seed: int = 7,
    ) -> "SimplicialMesh":
        vertices: dict[int, tuple[float, float]] = {}
        for y in range(height):
            for x in range(width):
                idx = y * width + x
                vertices[idx] = (float(x), float(y))

        faces: list[tuple[int, int, int]] = []
        for y in range(height - 1):
            for x in range(width - 1):
                a = y * width + x
                b = a + 1
                c = a + width
                d = c + 1
                faces.append((a, b, d))
                faces.append((a, d, c))

        return cls(vertices=vertices, faces=faces, seed=seed)

    def _face_area2(self, face: tuple[int, int, int]) -> float:
        i, j, k = face
        xi, yi = self.vertices[i]
        xj, yj = self.vertices[j]
        xk, yk = self.vertices[k]
        return (xj - xi) * (yk - yi) - (yj - yi) * (xk - xi)

    def _face_edges(self, face: tuple[int, int, int]) -> tuple[tuple[int, int], ...]:
        i, j, k = face
        return (
            canonical_edge(i, j),
            canonical_edge(j, k),
            canonical_edge(k, i),
        )

    def rebuild_topology(self) -> None:
        edge_to_faces: dict[tuple[int, int], list[tuple[int, int, int]]] = defaultdict(list)
        vertex_to_faces: dict[int, list[tuple[int, int, int]]] = defaultdict(list)

        for face in self.faces:
            for v in face:
                vertex_to_faces[v].append(face)
            for edge in self._face_edges(face):
                edge_to_faces[edge].append(face)

        self.edge_to_faces = dict(edge_to_faces)
        self.vertex_to_faces = dict(vertex_to_faces)
        self.edges = set(self.edge_to_faces)

    def heal_initial_artifacts(self) -> None:
        unique = {}
        for face in self.faces:
            if len(set(face)) != 3:
                continue
            unique[tuple(sorted(face))] = face
        self.faces = list(unique.values())
        self.rebuild_topology()

    def orient_faces_consistently(self) -> None:
        oriented: list[tuple[int, int, int]] = []
        for face in self.faces:
            if self._face_area2(face) < 0:
                i, j, k = face
                oriented.append((i, k, j))
            else:
                oriented.append(face)
        self.faces = oriented
        self.rebuild_topology()

    def validate_initial_state(self) -> None:
        if not self.faces:
            raise ValueError("mesh has no faces")

        for face in self.faces:
            if abs(self._face_area2(face)) < 1e-12:
                raise ValueError("degenerate face detected")

        self.rebuild_topology()

        for edge, incident in self.edge_to_faces.items():
            if len(incident) > 2:
                raise ValueError(f"nonmanifold edge detected: {edge}")

    def is_boundary_vertex(self, vertex: int) -> bool:
        for edge in self.edges:
            if vertex not in edge:
                continue
            if len(self.edge_to_faces.get(edge, [])) == 1:
                return True
        return False

    def vertex_neighbors(self, vertex: int) -> set[int]:
        neighbors: set[int] = set()
        for edge in self.edges:
            if vertex not in edge:
                continue
            a, b = edge
            neighbors.add(b if a == vertex else a)
        return neighbors

    def build_vertex_link_graph(self, vertex: int) -> LinkGraph:
        return self._build_vertex_link_graph_in_faces(vertex, self.faces)

    def _build_vertex_link_graph_in_faces(
        self,
        vertex: int,
        faces: list[tuple[int, int, int]],
    ) -> LinkGraph:
        link_graph = LinkGraph()
        for face in faces:
            if vertex not in face:
                continue
            others = [v for v in face if v != vertex]
            link_graph.add_edge(others[0], others[1])
        return link_graph

    def _is_boundary_vertex_in_faces(
        self,
        vertex: int,
        faces: list[tuple[int, int, int]],
    ) -> bool:
        edge_counts: dict[tuple[int, int], int] = defaultdict(int)
        for face in faces:
            for edge in self._face_edges(face):
                edge_counts[edge] += 1

        for edge, count in edge_counts.items():
            if vertex in edge and count == 1:
                return True
        return False

    def vertex_link_is_manifold(self, vertex: int) -> bool:
        return self._vertex_link_is_manifold_in_faces(vertex, self.faces)

    def _vertex_link_is_manifold_in_faces(
        self,
        vertex: int,
        faces: list[tuple[int, int, int]],
    ) -> bool:
        link_graph = self._build_vertex_link_graph_in_faces(vertex, faces)

        if not link_graph.is_connected():
            return False

        degrees = [link_graph.degree(node) for node in link_graph.nodes]

        if self._is_boundary_vertex_in_faces(vertex, faces):
            # Boundary vertex link must be one path.
            endpoints = sum(degree == 1 for degree in degrees)
            internal = all(degree in (1, 2) for degree in degrees)
            return endpoints == 2 and internal

        # Interior vertex link must be one cycle.
        return all(degree == 2 for degree in degrees)

    def count_nonmanifold_vertices(self) -> int:
        return sum(
            not self.vertex_link_is_manifold(vertex) for vertex in self.vertices
        )

    def free_energy(self) -> float:
        field_energy = self.fields["phi"] ** 2 + self.fields["psi"] ** 2
        geometric_energy = 0.0
        for a, b in self.edges:
            xa, ya = self.vertices[a]
            xb, yb = self.vertices[b]
            geometric_energy += math.dist((xa, ya), (xb, yb))
        vertex_variation = sum(abs(v) for v in self.vertex_field.values())
        return field_energy + 0.01 * geometric_energy + 0.1 * vertex_variation

    def _edge_stress(self, edge: tuple[int, int]) -> float:
        a, b = edge
        va = self.vertex_field.get(a, 0.0)
        vb = self.vertex_field.get(b, 0.0)
        xa, ya = self.vertices[a]
        xb, yb = self.vertices[b]
        length = math.dist((xa, ya), (xb, yb))
        return abs(va - vb) + 0.1 * length

    def select_stressed_interior_edge(self) -> tuple[int, int] | None:
        interior_edges = [
            edge for edge, faces in self.edge_to_faces.items() if len(faces) == 2
        ]
        if not interior_edges:
            return None
        return max(interior_edges, key=self._edge_stress)

    def link_condition_holds(
        self,
        u: int,
        v: int,
        opposite_a: int,
        opposite_b: int,
    ) -> bool:
        shared = self.vertex_neighbors(u) & self.vertex_neighbors(v)
        return shared == {opposite_a, opposite_b}

    def preview_flipped_faces(
        self,
        edge: tuple[int, int],
        opposite_a: int,
        opposite_b: int,
    ) -> list[tuple[int, int, int]]:
        incident_faces = self.edge_to_faces.get(edge, [])
        if len(incident_faces) != 2:
            return []

        u, v = edge
        return [
            (opposite_a, opposite_b, u),
            (opposite_b, opposite_a, v),
        ]

    def local_orientation_is_consistent(
        self,
        candidate_faces: list[tuple[int, int, int]],
    ) -> bool:
        return all(abs(self._face_area2(face)) > 1e-12 for face in candidate_faces)

    def local_vertex_links_are_manifold(
        self,
        candidate_faces: list[tuple[int, int, int]],
    ) -> bool:
        counts = Counter(v for face in candidate_faces for v in face)
        old_vertices = [v for v, c in counts.items() if c == 1]
        if len(old_vertices) != 2:
            return False

        old_edge = canonical_edge(old_vertices[0], old_vertices[1])
        incident_faces = self.edge_to_faces.get(old_edge, [])
        if len(incident_faces) != 2:
            return False

        trial_faces = [f for f in self.faces if f not in incident_faces]
        trial_faces.extend(candidate_faces)

        local_vertices = set(v for face in incident_faces for v in face)
        local_vertices.update(v for face in candidate_faces for v in face)

        return all(
            self._vertex_link_is_manifold_in_faces(vertex, trial_faces)
            for vertex in local_vertices
        )

    def apply_edge_flip(
        self,
        edge: tuple[int, int],
        opposite_a: int,
        opposite_b: int,
    ) -> None:
        incident_faces = self.edge_to_faces.get(edge, [])
        if len(incident_faces) != 2:
            return

        candidate_faces = self.preview_flipped_faces(
            edge=edge,
            opposite_a=opposite_a,
            opposite_b=opposite_b,
        )

        self.faces = [f for f in self.faces if f not in incident_faces]
        self.faces.extend(candidate_faces)
        self.rebuild_topology()

    def try_edge_flip(self, edge: tuple[int, int]) -> FlipResult:
        incident_faces = self.edge_to_faces.get(edge, [])

        if len(incident_faces) != 2:
            return FlipResult(False, "boundary_or_nonmanifold_edge")

        face_a, face_b = incident_faces
        u, v = edge

        opposite_a = next(vertex for vertex in face_a if vertex not in edge)
        opposite_b = next(vertex for vertex in face_b if vertex not in edge)

        new_diagonal = canonical_edge(opposite_a, opposite_b)

        if new_diagonal in self.edges:
            return FlipResult(False, "duplicate_diagonal")

        if not self.link_condition_holds(
            u,
            v,
            opposite_a,
            opposite_b,
        ):
            return FlipResult(False, "link_condition")

        candidate_faces = self.preview_flipped_faces(
            edge=edge,
            opposite_a=opposite_a,
            opposite_b=opposite_b,
        )

        if not self.local_orientation_is_consistent(candidate_faces):
            return FlipResult(False, "orientation")

        if not self.local_vertex_links_are_manifold(candidate_faces):
            return FlipResult(False, "vertex_link")

        self.apply_edge_flip(
            edge=edge,
            opposite_a=opposite_a,
            opposite_b=opposite_b,
        )

        return FlipResult(True, "accepted")
