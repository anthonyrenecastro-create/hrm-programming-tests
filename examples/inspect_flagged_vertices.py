from __future__ import annotations

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from hrm.mesh import SimplicialMesh
from hrm.topology import boundary_vertices


def main() -> None:
    mesh = SimplicialMesh.from_regular_grid(width=6, height=6, seed=7)
    mesh.heal_initial_artifacts()
    mesh.orient_faces_consistently()
    mesh.validate_initial_state()

    boundary = boundary_vertices(mesh)
    flagged = [v for v in mesh.vertices if not mesh.vertex_link_is_manifold(v)]

    print(f"Boundary vertices ({len(boundary)}): {boundary}")
    print(f"Flagged nonmanifold vertices ({len(flagged)}): {flagged}")


if __name__ == "__main__":
    main()
