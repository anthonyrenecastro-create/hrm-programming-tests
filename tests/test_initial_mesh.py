from hrm.mesh import SimplicialMesh


def test_initial_mesh_properties() -> None:
    mesh = SimplicialMesh.from_regular_grid(width=4, height=4, seed=7)
    mesh.heal_initial_artifacts()
    mesh.orient_faces_consistently()
    mesh.validate_initial_state()

    assert len(mesh.vertices) == 16
    assert len(mesh.faces) == 18
    assert len(mesh.edges) == 33
    assert mesh.count_nonmanifold_vertices() == 0
