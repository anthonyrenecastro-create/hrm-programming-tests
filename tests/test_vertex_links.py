from hrm.mesh import SimplicialMesh


def test_regular_grid_vertex_links_manifold() -> None:
    mesh = SimplicialMesh.from_regular_grid(width=4, height=4, seed=7)
    mesh.orient_faces_consistently()
    assert all(mesh.vertex_link_is_manifold(v) for v in mesh.vertices)


def test_disconnected_link_is_not_manifold() -> None:
    vertices = {
        0: (0.0, 0.0),
        1: (1.0, 0.0),
        2: (0.0, 1.0),
        3: (-1.0, 0.0),
        4: (0.0, -1.0),
    }
    faces = [(0, 1, 2), (0, 3, 4)]
    mesh = SimplicialMesh(vertices=vertices, faces=faces)

    assert not mesh.vertex_link_is_manifold(0)
