from fastapi import FastAPI,HTTPException,UploadFile,File,Form
from fastapi.responses import HTMLResponse
import os
import subprocess
import shutil
import pathlib


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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


@app.put("/AstsearchR")
def run_AstsearchR(size:int = 4):
    if (size != 2 and size != 4):
        raise HTTPException(status_code=400)
    else:
        size = str(size)
        
    os.chdir('/opt/SubaruHSC')
    subprocess.run(['AstsearchR'],input=size,encoding='UTF-8')
    
    return{"status_code": 200}

@app.get("/disp")
def get_disp():

    with open("/opt/SubaruHSC/disp.txt") as f:
        l = f.read().split()

    l = split_list(l,4)

    return{"result":l}


def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return: 
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

"""
fastAPIのチュートリアルから

https://fastapi.tiangolo.com/tutorial/request-files/#uploadfile
https://anaconda.org/conda-forge/python-multipart
"""

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):

    # pathlibでpathの操作
    image_path = pathlib.Path("/opt/tmp_images")

    # ディレクトリがなければつくる
    image_path.mkdir(exist_ok=True)

    # fileを保存
    for file in files:

        tmp_path = image_path/file.filename

        try:
            with tmp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                print(tmp_path)

        finally:
            file.file.close()

    return {"tmp_folder":image_path.iterdir()}

# ファイルアップロード確認用
@app.get("/")
async def main():
    content = """
<body>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
