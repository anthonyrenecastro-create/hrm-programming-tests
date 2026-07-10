from hrm.mesh import SimplicialMesh


def test_link_condition_holds_for_interior_edge() -> None:
    mesh = SimplicialMesh.from_regular_grid(width=5, height=5, seed=7)
    mesh.orient_faces_consistently()
    edge = mesh.select_stressed_interior_edge()
    assert edge is not None

    incident = mesh.edge_to_faces[edge]
    assert len(incident) == 2

    face_a, face_b = incident
    opposite_a = next(v for v in face_a if v not in edge)
    opposite_b = next(v for v in face_b if v not in edge)

    assert mesh.link_condition_holds(edge[0], edge[1], opposite_a, opposite_b)
