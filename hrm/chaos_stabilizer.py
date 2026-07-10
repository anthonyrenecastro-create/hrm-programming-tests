from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class ControlSignal:
    dt: float
    damping: float
    surgery_allowed: bool


class ChaosStabilizer:
    def __init__(self, base_dt: float = 0.002):
        self.base_dt = base_dt

    def measure(
        self,
        energy: float,
        field: dict[str, float],
        state: tuple[float, float, float],
    ) -> float:
        field_amp = abs(field.get("phi", 0.0)) + abs(field.get("psi", 0.0))
        state_amp = math.sqrt(sum(component * component for component in state))
        return energy + 0.5 * field_amp + 0.25 * state_amp

    def control(self, chaos: float) -> ControlSignal:
        normalized = chaos / (1.0 + chaos)
        dt = self.base_dt * (1.0 - 0.6 * normalized)
        damping = 0.02 + 0.2 * normalized
        surgery_allowed = normalized < 0.85
        return ControlSignal(dt=dt, damping=damping, surgery_allowed=surgery_allowed)
