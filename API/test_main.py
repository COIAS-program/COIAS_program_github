from main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_unknown_disp():

    with open("/opt/tmp_files/unknown_disp.txt", mode="w") as f:
        # fmt: off
        f.write(
            """
A B C D
0 1 2 3
            """
        )
        # fmt: on
    response = client.get("/unknown_disp")
    assert response.status_code == 200
    assert response.json() == {"result": [["A", "B", "C", "D"], ["0", "1", "2", "3"]]}
