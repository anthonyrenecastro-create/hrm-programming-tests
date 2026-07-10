from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mesh import FlipResult, SimplicialMesh


@dataclass
class SurgeryAttempt:
    attempted: bool
    result: "FlipResult | None"


def attempt_edge_flip(mesh: "SimplicialMesh", surgery_allowed: bool) -> SurgeryAttempt:
    if not surgery_allowed:
        return SurgeryAttempt(attempted=False, result=None)

    candidate = mesh.select_stressed_interior_edge()
    if candidate is None:
        return SurgeryAttempt(attempted=False, result=None)

    return SurgeryAttempt(attempted=True, result=mesh.try_edge_flip(candidate))
