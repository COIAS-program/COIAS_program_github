# COIAS_program_github

```
.
├── API
├── Docker
├── SubaruHSC
├── data
├── docs
├── env
└── findOrb
```

* API
  
frontAppに情報を送信するためのAPI

* Docker

実行用・開発用のdockerfile

* SubaruHSC

imageの保管フォルダ。変更の可能性あり。

* data

~/.coiasを保存

* docs

ドキュメント

* env

condaのパッケージを保管

* findOrb

Cプログラム

# 備考

## コマンド

## コード変更時

* docker build

キャッシュを使用しないでビルドを行うコマンド

```
docker build -t coias . --no-cache
```

## conda関係

* conda環境のymlへの書き出し方

```
conda activate COIAS_program_github
conda env export --no-builds > env.yml
```

* ResolvePackageNotFoundが出た時の対処法

例）
```
ResolvePackageNotFound : 
      - xxxxxxx=12.0.0
      - xxxxxxx=14.0.0
```

この場合、'=12.0.0'と'=14.0.0'を消すと対応するversionを見つけて補完してくれる
