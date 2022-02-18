# coias api

[FastAPI](https://fastapi.tiangolo.com/ja/)

## uvicornの起動コマンド

### 手動実行

```
uvicorn API.main:app --host 0.0.0.0 --reload
```

### 開発コンテナの場合

vscode「実行とデバック」より「Python:FastAPI」を実行

## アクセス

http://127.0.0.1:8000/docs

http://127.0.0.1:8000/redoc