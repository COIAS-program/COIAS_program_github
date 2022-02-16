from unittest import result
from fastapi import FastAPI,HTTPException
import os
import subprocess

app = FastAPI()

@app.get("/test")
def test():
    print("test")

    return{"hello": "world"}

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
 