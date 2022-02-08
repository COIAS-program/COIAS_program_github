from fastapi import FastAPI,HTTPException
import os
import subprocess

app = FastAPI()

@app.put("/AstsearchR")
def run_AstsearchR(size:int = 4):
    if (size != 2 and size != 4):
        raise HTTPException(status_code=400)
    else:
        size = str(size)
        
    os.chdir('../SubaruHSC')
    subprocess.run(['../AstsearchR'],input=size,encoding='UTF-8')
    
    return{"status_code": 200}
