import os
import subprocess
import shutil
import pathlib
from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


tags_metadata = [
    {"name": "disp", "description": "disp.txt及びredisp.txtを取得します。"},
    {"name": "command", "description": "backendで実行されるコマンドAPIです。"},
    {"name": "files", "description": "backendに送信するファイルの操作APIです。"},
    {"name": "test", "description": "test用に用意されたAPIです。"},
]
app = FastAPI(
    title="COIAS API",
    description="coiasフロントアプリからアクセスされるAPIです。",
    version="1.0",
    openapi_tags=tags_metadata,
)

origins = [
    "http://localhost",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGE_PATH = pathlib.Path("/opt/tmp_images")
SUBARU_PATH = pathlib.Path("/opt/SubaruHSC")


@app.get("/", summary="ファイルアップロード確認用", tags=["test"])
async def main():
    """
    [localhost](http://localhost:8000/)
    """
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/subaru_hsc_copy", summary="テストデータの準備", tags=["test"])
def run_subaru_hsc_copy():
    """
    __テスト画像アップロード時間短縮用__

    tmp_imagesを削除した後、SubaruHSCの中身をtmp_imagesにコピーします。  
    あらかじめSubaruHSCにデータ(*.fits)を用意しておく必要があります。
    """  # noqa:W291

    if IMAGE_PATH.is_file():
        shutil.rmtree(IMAGE_PATH)
    shutil.copytree(SUBARU_PATH, IMAGE_PATH)


@app.get(
    "/disp",
    summary="disp.txtを配列で取得",
    tags=["disp"],
    status_code=status.HTTP_404_NOT_FOUND,
)
def get_disp():
    disp_path = IMAGE_PATH / "disp.txt"

    if not disp_path.is_file():
        raise HTTPException(status_code=404)

    with disp_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    result = split_list(result.split(), 4)

    return {"result": result}


@app.get(
    "/redisp",
    summary="redisp.txtを配列で取得",
    tags=["disp"],
    status_code=status.HTTP_404_NOT_FOUND,
)
def get_redisp():
    redisp_path = IMAGE_PATH / "redisp.txt"
    if not redisp_path.is_file():
        raise HTTPException(status_code=404)

    with redisp_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    result = split_list(result.split(), 4)

    return {"result": result}


def split_list(list, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return:
    """
    for idx in range(0, len(list), n):
        yield list[idx : idx + n]


@app.post("/uploadfiles/", summary="fileアップロード", tags=["files"])
async def create_upload_files(files: list[UploadFile]):
    """
    複数のファイルをアップロードする場合はこちらのページを使用すると良い

    [localhost:8000](http://localhost:8000/)

    __参考__
    - [Request Files - FastAPI](https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile)
    - [フォーム - React](https://ja.reactjs.org/docs/forms.html)
    """  # noqa:E501

    # ディレクトリがなければつくる
    IMAGE_PATH.mkdir(exist_ok=True)

    # fileを保存
    for file in files:

        tmp_path = IMAGE_PATH / file.filename

        try:
            with tmp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                print(tmp_path)

        finally:
            file.file.close()

    return {"status_code": 200}


@app.delete("/deletefiles", summary="imageディレクトリ削除", tags=["files"])
def run_deletefiles():

    if not IMAGE_PATH.is_file():
        shutil.rmtree(IMAGE_PATH)

    return {"status_code": 200}


@app.put("/preprocess", summary="最新のMPCデータを取得", tags=["command"])
def run_preprocess():

    subprocess.run(["preprocess"])

    return {"status_code": 200}


@app.put("/startsearch2R", summary="ビギニング&マスク", tags=["command"])
def run_startsearch2R(binning: int = 4):

    if binning != 2 and binning != 4:
        raise HTTPException(status_code=400)
    else:
        binning = str(binning)

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["startsearch2R"], input=binning, encoding="UTF-8")

    return {"status_code": 200}


@app.put("/fits2png", summary="画像変換", tags=["command"])
def run_fits2png():
    """未実装？"""
    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["fits2png"])

    return {"status_code": 200}


@app.put("/findsource", summary="光源検出", tags=["command"])
def run_findsource():

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["findsource"])

    return {"status_code": 200}


@app.put("/prempsearchC", summary="精密軌道取得", tags=["command"])
def run_prempsearchC():

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["prempsearchC"])

    return {"status_code": 200}


@app.put("/astsearch_new", summary="自動検出", tags=["command"])
def run_astsearch_new():

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["astsearch_new"])

    return {"status_code": 200}


@app.put(
    "/AstsearchR",
    summary="全自動処理",
    tags=["command"],
    status_code=status.HTTP_400_BAD_REQUEST,
)
def run_AstsearchR(binning: int = 4):

    if binning != 2 and binning != 4:
        raise HTTPException(status_code=400)
    else:
        binning = str(binning)

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["AstsearchR"], input=binning, encoding="UTF-8")

    return {"status_code": 200}


@app.put("/prempedit", summary="MPCフォーマットに再整形", tags=["command"])
def run_prempedit():
    """"""
    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["prempedit"])

    return {"status_code": 200}


@app.put("/prempedit3", summary="出力ファイル整形", tags=["command"])
def run_prempedit3(num: int):

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["prempedit3.py", str(num)])

    return {"status_code": 200}


@app.put("/redisp", summary="再描画による確認作業", tags=["command"])
def run_redisp():

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["redisp"])

    return {"status_code": 200}


@app.put("/Astsearch_afterReCOIAS", summary="再描画による確認作業", tags=["command"])
def run_Astsearch_afterReCOIAS():

    os.chdir(IMAGE_PATH.as_posix())
    subprocess.run(["Astsearch_afterReCOIAS"])

    return {"status_code": 200}


@app.put("/rename", summary="「mpc4.txt」の複製と「send_mpc.txt」へrename", tags=["command"])
def run_rename():

    from_path = IMAGE_PATH / "mpc4.txt"
    to_path = IMAGE_PATH / "send_mpc.txt"
    shutil.copy(from_path, to_path)

    return {"status_code": 200}
