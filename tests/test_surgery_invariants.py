from hrm.diagnostics import compute_full_invariants
from hrm.mesh import SimplicialMesh


def test_edge_flip_preserves_global_invariants_when_accepted() -> None:
    mesh = SimplicialMesh.from_regular_grid(width=6, height=6, seed=7)
    mesh.orient_faces_consistently()

    edge = mesh.select_stressed_interior_edge()
    assert edge is not None

    before = compute_full_invariants(mesh)
    result = mesh.try_edge_flip(edge)

    if result.accepted:
        after = compute_full_invariants(mesh)
        assert after.euler_characteristic == before.euler_characteristic
        assert after.nonmanifold_vertices == 0
    else:
        assert result.reason in {
            "duplicate_diagonal",
            "link_condition",
            "orientation",
            "vertex_link",
            "boundary_or_nonmanifold_edge",
        }
