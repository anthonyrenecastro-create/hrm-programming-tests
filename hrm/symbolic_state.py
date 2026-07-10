from __future__ import annotations


def update_symbolic_state(
    state_vector: tuple[float, float, float],
    fields: dict[str, float],
) -> tuple[float, float, float]:
    s0, s1, s2 = state_vector
    phi = float(fields.get("phi", 0.0))
    psi = float(fields.get("psi", 0.0))

    return (
        0.9 * s0 + 0.1 * phi,
        0.85 * s1 + 0.15 * psi,
        0.5 * s2 + 0.5 * (phi - psi),
    )
