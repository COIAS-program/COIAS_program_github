import os
import string
import subprocess
import shutil
import pathlib
from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

COIAS_DES = 'coiasフロントアプリからアクセスされるAPIです。\
    \n\n<img src="/static/icon.png" alt="drawing" width="200"/>'

tags_metadata = [
    {"name": "command", "description": "backendで実行されるコマンドAPIです。"},
    {"name": "files", "description": "backendに送信するファイルの操作APIです。"},
    {"name": "test", "description": "test用に用意されたAPIです。"},
]
app = FastAPI(
    title="COIAS API",
    description=COIAS_DES,
    version="0.2.1",
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

OPT_PATH = pathlib.Path("/opt")
PROGRAM_PATH = OPT_PATH / "COIAS_program_github"
IMAGES_PATH = OPT_PATH / "tmp_images"
FILES_PATH = OPT_PATH / "tmp_files"
SUBARU_PATH = PROGRAM_PATH / "SubaruHSC"
DOC_IMAGE_PATH = PROGRAM_PATH / "docs/image"

# https://fastapi.tiangolo.com/ja/tutorial/static-files/
app.mount("/static", StaticFiles(directory=DOC_IMAGE_PATH), name="icon")


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
    __テストデータアップロード時間短縮用__

    tmp_filesを削除した後、SubaruHSCの中身をtmp_filesにコピーします。
    あらかじめSubaruHSCにデータ(*.fits)を用意しておく必要があります。
    """  # noqa:W291

    if FILES_PATH.is_dir():
        shutil.rmtree(FILES_PATH)
    shutil.copytree(SUBARU_PATH, FILES_PATH)

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.get("/disp", summary="disp.txtを配列で取得", tags=["files"])
def get_disp():
    disp_path = FILES_PATH / "disp.txt"

    if not disp_path.is_file():
        raise HTTPException(status_code=404)

    with disp_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    result = split_list(result.split(), 4)

    return {"result": result}


@app.get("/unknown_disp", summary="unknown_disp.txtを配列で取得", tags=["files"])
def get_unknown_disp():
    disp_path = FILES_PATH / "unknown_disp.txt"

    if not disp_path.is_file():
        raise HTTPException(status_code=404)

    with disp_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    result = split_list(result.split(), 4)

    return {"result": result}


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
    FILES_PATH.mkdir(exist_ok=True)

    # fileを保存
    for file in files:

        tmp_path = FILES_PATH / file.filename

        try:
            with tmp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        finally:
            file.file.close()

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.delete("/deletefiles", summary="tmp_filesおよびtmp_imageの中身を削除", tags=["files"])
def run_deletefiles():

    for f in FILES_PATH.glob("*"):
        if f.is_file:
            f.unlink()

    for f in IMAGES_PATH.glob("*.png"):
        if f.is_file:
            f.unlink()

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/copy", summary="「tmp_files」から「tmp_image」へpng画像コピー", tags=["files"])
def run_copy():
    # fmt: off
    """
    「tmp_image」にあるpng画像はnginxによって配信されます。  
    配信されているpng画像のリストを配列で返却します。

    __res__

    ```JSON
    {
        "result": [
            "1_disp-coias.png",
            "1_disp-coias_nonmask.png",
            "2_disp-coias.png",
            "2_disp-coias_nonmask.png",
            "3_disp-coias.png",
            "3_disp-coias_nonmask.png",
            "4_disp-coias.png",
            "4_disp-coias_nonmask.png",
            "5_disp-coias.png",
            "5_disp-coias_nonmask.png",
        ]
    }
    ```
    """ # noqa
    # fmt: on
    for f in FILES_PATH.glob("*.png"):
        if f.is_file():
            shutil.copy(f, IMAGES_PATH)

    file_list = []
    for i in IMAGES_PATH.glob("*.png"):
        file_list.append(i.name)
    file_list.sort()

    return {"result": file_list}


@app.put("/memo", summary="outputを出力", tags=["files"])
def run_memo(output_list: list):
    # fmt: off
    """
    bodyの配列からmemo.txtを出力します。

    __body__

    ```JSON
    [
        "000001",
        "000010",
        "000013",
        "000012",
        "000005",
        "000003",
        "000004",
        "000009",
        "000000",
        "000006",
        "000014"
    ]
    ```
    """ # noqa
    # fmt: on

    memo: string = ""
    result: string = ""
    memo_path = FILES_PATH / "memo.txt"

    for i, list in enumerate(output_list):
        memo = memo + str(list)
        if not i == (len(output_list) - 1):
            memo = memo + "\n"

    with memo_path.open(mode="w") as f:
        f.write(memo)

    with memo_path.open(mode="r") as f:
        result = f.read()

    return {"memo.txt": result}


@app.put("/preprocess", summary="最新のMPCデータを取得", tags=["command"])
def run_preprocess():

    subprocess.run(["preprocess"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/startsearch2R", summary="ビギニング&マスク", tags=["command"])
def run_startsearch2R(binning: int = 2):

    if binning != 2 and binning != 4:
        raise HTTPException(status_code=400)
    else:
        binning = str(binning)

    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["startsearch2R"], input=binning, encoding="UTF-8")

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/fits2png", summary="画像変換", tags=["command"])
def run_fits2png():
    """未実装？"""
    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["fits2png"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/findsource", summary="光源検出", tags=["command"])
def run_findsource():

    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["findsource"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/prempsearchC-before", summary="精密軌道取得 前処理", tags=["command"])
def run_prempsearchC_before():

    premp = PROGRAM_PATH / "prempsearchC"
    script = ""

    with premp.open(mode="r") as f:
        for i in range(25):
            script = script + f.readline()

    os.chdir(FILES_PATH.as_posix())
    subprocess.run([premp])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/prempsearchC-after", summary="精密軌道取得 後処理", tags=["command"])
def run_prempsearchC_after():

    # todo 実装
    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["prempsearchC"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/astsearch_new", summary="自動検出", tags=["command"])
def run_astsearch_new():

    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["astsearch_new"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put(
    "/AstsearchR",
    summary="全自動処理",
    tags=["command"],
    status_code=status.HTTP_400_BAD_REQUEST,
)
def run_AstsearchR(binning: int = 2):

    if binning != 2 and binning != 4:
        raise HTTPException(status_code=400)
    else:
        binning = str(binning)

    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["AstsearchR"], input=binning, encoding="UTF-8")

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/prempedit", summary="MPCフォーマットに再整形", tags=["command"])
def run_prempedit():
    """"""
    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["prempedit"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/prempedit3", summary="出力ファイル整形", tags=["command"])
def run_prempedit3(num: int):

    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["prempedit3.py", str(num)])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/redisp", summary="再描画による確認作業", tags=["command"])
def run_redisp():
    """
    redispが動作し、redisp.txtを配列で取得

    __res__

    ```JSON
    {
        "result": [
            [
            "w7794",
            "3",
            "1965.52",
            "424.56"
            ],
            [
            "w7794",
            "2",
            "1927.21",
            "416.32"
            ]
        ]
    }
    ```

    """  # noqa

    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["redisp"])

    redisp_path = FILES_PATH / "redisp.txt"

    if not redisp_path.is_file():
        raise HTTPException(status_code=404)

    with redisp_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    result = split_list(result.split(), 4)

    return {"result": result}


@app.put("/AstsearchR_afterReCOIAS", summary="再描画による確認作業", tags=["command"])
def run_Astsearch_afterReCOIAS():

    os.chdir(FILES_PATH.as_posix())
    subprocess.run(["AstsearchR_afterReCOIAS"])

    send_path = FILES_PATH / "send_mpc.txt"
    result: string = ""

    with send_path.open(mode="r") as f:
        result = f.read()

    if not send_path.is_file():
        raise HTTPException(status_code=404)

    if result == "":
        raise HTTPException(status_code=404)

    return {"send_mpc": result}


@app.put("/rename", summary="「mpc4.txt」の複製と「send_mpc.txt」へrename", tags=["command"])
def run_rename():

    from_path = FILES_PATH / "mpc4.txt"
    to_path = FILES_PATH / "send_mpc.txt"
    shutil.copy(from_path, to_path)

    return JSONResponse(status_code=status.HTTP_200_OK)


def split_list(list, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return:
    """
    for idx in range(0, len(list), n):
        yield list[idx : idx + n]
