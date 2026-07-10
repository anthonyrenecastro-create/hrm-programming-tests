from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

from .topology import boundary_vertices

if TYPE_CHECKING:
    from .engine import HRMEngine
    from .mesh import SimplicialMesh


def plot_history(engine: "HRMEngine", output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    energy_path = output / "free_energy_history.png"
    chaos_path = output / "chaos_history.png"

    plt.figure(figsize=(8, 4))
    plt.plot(engine.energy_history)
    plt.title("Free Energy History")
    plt.xlabel("Step")
    plt.ylabel("Energy")
    plt.tight_layout()
    plt.savefig(energy_path)
    plt.close()

    plt.figure(figsize=(8, 4))
    plt.plot(engine.chaos_history)
    plt.title("Chaos Signal History")
    plt.xlabel("Step")
    plt.ylabel("Chaos")
    plt.tight_layout()
    plt.savefig(chaos_path)
    plt.close()

    return energy_path, chaos_path


def plot_mesh(mesh: "SimplicialMesh", path: str | Path, title: str = "Mesh") -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(6, 6))
    for i, j, k in mesh.faces:
        pts = [mesh.vertices[i], mesh.vertices[j], mesh.vertices[k], mesh.vertices[i]]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        plt.plot(xs, ys, "k-", linewidth=0.8)

    vx = [mesh.vertices[v][0] for v in mesh.vertices]
    vy = [mesh.vertices[v][1] for v in mesh.vertices]
    plt.scatter(vx, vy, s=20)
    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out


def plot_flagged_boundary_vertices(
    mesh: "SimplicialMesh",
    path: str | Path,
) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    boundary = set(boundary_vertices(mesh))

    plt.figure(figsize=(6, 6))
    for i, j, k in mesh.faces:
        pts = [mesh.vertices[i], mesh.vertices[j], mesh.vertices[k], mesh.vertices[i]]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        plt.plot(xs, ys, "#9ca3af", linewidth=0.8)

    for vertex, (x, y) in mesh.vertices.items():
        if vertex in boundary:
            plt.scatter([x], [y], c="red", s=36)
        else:
            plt.scatter([x], [y], c="black", s=16)

    plt.title("Flagged Boundary Vertices")
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    return out
