import os
import subprocess
import shutil
import pathlib
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


COIAS_DES = 'coiasフロントアプリからアクセスされるAPIです。\
    \n\n<img src="/static/icon.png" alt="drawing" width="200"/>'

tags_metadata = [
    {"name": "command", "description": "backendで実行されるコマンドAPIです。"},
    {"name": "files", "description": "backendに送信するファイルの操作APIです。"},
    {"name": "test", "description": "テスト用のAPIです。"},
]
app = FastAPI(
    title="COIAS API",
    description=COIAS_DES,
    version="0.3.1",
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

# ディレクトリがなければつくる
FILES_PATH.mkdir(exist_ok=True)


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


@app.get("/unknown_disp", summary="unknown_disp.txtを配列で取得", tags=["files"])
def get_unknown_disp(pj: int = -1):
    disp_path = pj_path(pj) / "unknown_disp.txt"

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

    dt = str(datetime.now())
    log = {
        "file_list": [],
        "create_time": [],
        "zip_upload": [],
    }
    log_path = FILES_PATH / "log"

    # logファイルがあれば読み込み
    if log_path.is_file():

        with log_path.open(mode="r") as conf:
            conf_json = conf.read()

        if not conf_json == "":
            log = json.loads(conf_json)

    # projectに割り振られる番号を生成
    if log["file_list"]:
        last_project = log["file_list"][-1] + 1
    else:
        last_project = 1

    # logを更新
    log["file_list"].append(last_project)
    log["create_time"].append(dt)
    log["zip_upload"].append(False)

    # logを書き込み
    json_str = json.dumps(log)
    with log_path.open(mode="w") as conf:
        conf.write(json_str)

    # プロジェクトディレクトリを作成
    file_name = str(log["file_list"][-1])
    current_project_folder_path = FILES_PATH / file_name
    current_project_folder_path.mkdir()

    # fileを保存
    for file in files:

        tmp_path = current_project_folder_path / file.filename

        try:
            with tmp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        finally:
            file.file.close()

    # プロジェクトディレクトリの内容を取得
    files_dir = [fd.name for fd in FILES_PATH.iterdir() if fd.is_dir()]
    project_files = [pf.name for pf in current_project_folder_path.iterdir()]

    files_dir.sort(key=int)
    project_files.sort()

    return {"tmp_files_projects": files_dir, "project_files": project_files, "log": log}


@app.get("/project-list", summary="projectのリストを返却します", tags=["files"])
def run_get_project_list():
    # fmt:off
    """
    projectのリストを返却します。  
    projectはファイルがアップロードされるたびに、作成されます。

    __res__

    ```
    {
        "tmp_files_projects": [
            "1",
            "2"
        ],
        "log": {
            "file_list": [
                1,
                2
            ],
            "create_time": [
                "2022-03-25 07:33:34.558611",
                "2022-03-25 08:03:34.850662"
            ],
            "zip_upload": [
                false,
                false
            ]
        }
    }
    ```

    tmp_files_projects  
    実際にtmpフォルダーに配置されている、プロジェクトフォルダー。

    log  
    project作成時に更新される、プロジェクトの詳細情報。

    """  # noqa
    # fmt:on
    log_path = FILES_PATH / "log"

    # logファイルがあれば読み込み
    if log_path.is_file():

        with log_path.open(mode="r") as conf:
            conf_json = conf.read()

        if not conf_json == "":
            log = json.loads(conf_json)

    else:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    # プロジェクトディレクトリpathを作成
    file_name = str(log["file_list"][-1])
    current_project_folder_path = FILES_PATH / file_name

    # プロジェクトディレクトリの内容を取得
    files_dir = [fd.name for fd in FILES_PATH.iterdir() if fd.is_dir()]
    project_files = [pf.name for pf in current_project_folder_path.iterdir()]

    files_dir.sort(key=int)
    project_files.sort()

    return {"tmp_files_projects": files_dir, "log": log}


@app.get("/project", summary="projectのフォルダ内容を返却します", tags=["files"])
def run_get_project(pj: int = -1):
    # fmt:off
    """
    projectのフォルダ内容を返却します。  

    __res__

    ```
    {
        "project_files": [
            "1_disp-coias.png",
            "1_disp-coias_nonmask.png",
            "2_disp-coias.png",
            "2_disp-coias_nonmask.png",
                    ・
                    ・
                    ・
        ]
    }
    ```


    """  # noqa
    # fmt:on

    log_path = FILES_PATH / "log"

    # logファイルがあれば読み込み
    if log_path.is_file():

        with log_path.open(mode="r") as conf:
            conf_json = conf.read()

        if not conf_json == "":
            log = json.loads(conf_json)

    else:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    # プロジェクトディレクトリを作成
    file_name = str(log["file_list"][-1])
    current_project_folder_path = FILES_PATH / file_name

    # プロジェクトディレクトリの内容を取得
    project_files = [pf.name for pf in current_project_folder_path.iterdir()]
    project_files.sort()

    return {"project_files": project_files}


@app.delete("/deletefiles", summary="tmp_imageの中身を削除", tags=["files"])
def run_deletefiles():

    for f in IMAGES_PATH.glob("*.png"):
        if f.is_file:
            f.unlink()

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/copy", summary="プロジェクトから「tmp_image」へpng画像コピー", tags=["files"])
def run_copy(pj: int = -1):
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
    for f in pj_path(pj).glob("*.png"):
        if f.is_file():
            shutil.copy(f, IMAGES_PATH)

    file_list = []
    for i in IMAGES_PATH.glob("*.png"):
        file_list.append(i.name)
    file_list.sort()

    return {"result": file_list}


@app.put("/memo", summary="outputを出力", tags=["files"])
def run_memo(output_list: list, pj: int = -1):
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

    memo = ""
    result = ""
    memo_path = pj_path(pj) / "memo.txt"

    for i, list in enumerate(output_list):
        memo = memo + str(list)
        if not i == (len(output_list) - 1):
            memo = memo + "\n"

    with memo_path.open(mode="w") as f:
        f.write(memo)

    with memo_path.open(mode="r") as f:
        result = f.read()

    return {"memo.txt": result}


@app.get("/memo2", summary="memo2.txtを取得", tags=["files"])
def get_memo2(pj: int = -1):
    memo_path = pj_path(pj) / "memo2.txt"

    if not memo_path.is_file():
        raise HTTPException(status_code=404)

    with memo_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    return {"memo2": result}


@app.put("/listb3.txt", summary="listb3を書き込み", tags=["files"])
def write_listb3(text: str, pj: int = -1):
    # fmt: off
    """
    textの文字列をlistb3.txtに書き込みます。  
    listb3の内容を返却します。
    """ # noqa
    # fmt: on

    text_path = pj_path(pj) / "listb3.txt"

    with text_path.open(mode="w") as f:
        f.write(text)

    with text_path.open(mode="r") as f:
        result = f.read()

    return {"listb3.txt": result}


@app.put("/preprocess", summary="最新のMPCデータを取得", tags=["command"])
def run_preprocess():

    subprocess.run(["preprocess"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/startsearch2R", summary="ビギニング&マスク", tags=["command"])
def run_startsearch2R(binning: int = 2, pj: int = -1):

    if binning != 2 and binning != 4:
        raise HTTPException(status_code=400)
    else:
        binning = str(binning)

    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["startsearch2R"], input=binning, encoding="UTF-8")

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/fits2png", summary="画像変換", tags=["command"])
def run_fits2png(pj: int = -1):
    """未実装？"""
    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["fits2png"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/findsource", summary="光源検出", tags=["command"])
def run_findsource(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["findsource"])

    return JSONResponse(status_code=status.HTTP_200_OK)


"""
prempsearchCを25行目で分割し、それぞれ別のAPIで動作させます。
連続して実行するとサーバーから情報を取得できないことがあるためです。
"""
P_C_SPLIT_LINE = 25


@app.put("/prempsearchC-before", summary="精密軌道取得 前処理", tags=["command"])
def run_prempsearchC_before(pj: int = -1):
    """
    prempsearchCを編集した場合、動かなくなります。
    """

    premp = PROGRAM_PATH / "prempsearchC"
    script = ""

    # prempsearchCの<P_C_SPLIT_LINE>行より上を実行
    with premp.open(mode="r") as f:

        for i in range(P_C_SPLIT_LINE):
            script = script + f.readline()

    script = script + "\necho 前処理が完了"

    os.chdir(pj_path(pj).as_posix())
    subprocess.run([script], shell=True)

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/prempsearchC-after", summary="精密軌道取得 後処理", tags=["command"])
def run_prempsearchC_after(pj: int = -1):
    """
    prempsearchCを編集した場合、動かなくなります。
    """

    premp = PROGRAM_PATH / "prempsearchC"
    script = "#!/bin/bash\n"
    count = 0

    # prempsearchCの<P_C_SPLIT_LINE>行より下を実行
    with premp.open(mode="r") as f:
        while True:
            count = count + 1
            data = f.readline()

            if count > P_C_SPLIT_LINE:

                if data == "":
                    break
                else:
                    script = script + data

    script = script + "\necho 後処理が完了"

    os.chdir(pj_path(pj).as_posix())
    subprocess.run([script], shell=True)

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/astsearch_new", summary="自動検出", tags=["command"])
def run_astsearch_new(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["astsearch_new"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put(
    "/AstsearchR",
    summary="全自動処理",
    tags=["command"],
    status_code=status.HTTP_400_BAD_REQUEST,
)
def run_AstsearchR(binning: int = 2, pj: int = -1):

    if binning != 2 and binning != 4:
        raise HTTPException(status_code=400)
    else:
        binning = str(binning)

    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["AstsearchR"], input=binning, encoding="UTF-8")

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/prempedit", summary="MPCフォーマットに再整形", tags=["command"])
def run_prempedit(pj: int = -1):
    """"""
    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["prempedit"])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/prempedit3", summary="出力ファイル整形", tags=["command"])
def run_prempedit3(num: int, pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["prempedit3.py", str(num)])

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/redisp", summary="再描画による確認作業", tags=["command"])
def run_redisp(pj: int = -1):
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

    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["redisp"])

    redisp_path = pj_path(pj) / "redisp.txt"

    if not redisp_path.is_file():
        raise HTTPException(status_code=404)

    with redisp_path.open() as f:
        result = f.read()

    if result == "":
        raise HTTPException(status_code=404)

    result = split_list(result.split(), 4)

    return {"result": result}


@app.put("/AstsearchR_afterReCOIAS", summary="再描画による確認作業", tags=["command"])
def run_Astsearch_afterReCOIAS(pj: int = -1):

    os.chdir(pj_path(pj).as_posix())
    subprocess.run(["AstsearchR_afterReCOIAS"])

    send_path = pj_path(pj) / "send_mpc.txt"
    result = ""

    with send_path.open(mode="r") as f:
        result = f.read()

    if not send_path.is_file():
        raise HTTPException(status_code=404)

    if result == "":
        raise HTTPException(status_code=404)

    return {"send_mpc": result}


@app.put("/rename", summary="「mpc4.txt」の複製と「send_mpc.txt」へrename", tags=["command"])
def run_rename(pj: int = -1):

    from_path = pj_path(pj) / "mpc4.txt"
    to_path = pj_path(pj) / "send_mpc.txt"
    shutil.copy(from_path, to_path)

    return JSONResponse(status_code=status.HTTP_200_OK)


@app.put("/astsearch_manual", summary="手動再測定モード", tags=["command"])
def run_astsearch_manual(pj: int = -1):
    """
    4行目を飛ばしてastsearch_manualを実行
    """

    astsearch = PROGRAM_PATH / "astsearch_manual"
    script = ""
    count = 1

    with astsearch.open(mode="r") as f:
        while True:

            data = f.readline()

            if not count == 4:
                script = script + data
            else:
                print("Skip loading : " + data)

            if data == "":
                break

            count += 1

    script = script + "\necho astsearch_manualが完了"

    os.chdir(pj_path(pj).as_posix())
    subprocess.run([script], shell=True)

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


def pj_path(pj):

    log_path = FILES_PATH / "log"

    with log_path.open(mode="r") as conf:
        conf_json = conf.read()

    if not conf_json == "":
        log = json.loads(conf_json)
    else:
        return

    file_name = log["file_list"][pj]
    path = FILES_PATH / str(file_name)

    return path
