from hrm.mesh import SimplicialMesh


def test_faces_are_oriented_consistently() -> None:
    mesh = SimplicialMesh.from_regular_grid(width=5, height=5, seed=7)
    mesh.orient_faces_consistently()

    for face in mesh.faces:
        assert mesh._face_area2(face) > 0.0
