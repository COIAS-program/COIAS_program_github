# Dockerfileについて

```
.
├── Dockerfile
├── Dockerfile.dev
├── REEADME.md
└── setup.sh
```

* Dockerfile

実行用Dockerfile

* Dockerfile.dev

開発用Dockerfile.
なお開発はvscodeで行うことを前提にしています。

* setup.sh

開発環境構築用スクリプト。
開発環境用のコンテナ実行後（bind後）に実行され、パッケージのインストールなどを行います。

## 実行用コンテナの実行コマンド

詳しくは /docs を見てください。

```
docker build -t coias ./Docker

docker run -it --name coias \
--mount type=bind,source="$(pwd)"/data,target=/root/.coias \
--mount type=bind,source="$(pwd)"/SubaruHSC,target=/opt/SubaruHSC \
-p 8000:8000 coias /bin/bash
```