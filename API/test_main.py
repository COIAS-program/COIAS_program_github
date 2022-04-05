from main import app

import pathlib
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_unknown_disp():

    OPT_PATH = pathlib.Path("/opt")
    FILES_PATH = OPT_PATH / "tmp_files"
    FILES_PATH.mkdir(exist_ok=True)

    with open("/opt/tmp_files/unknown_disp.txt", mode="w+",) as f:
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
