# 環境構築手順

Dockerを使用し環境を構築する。
ここではdocker-composeを使用しないが、特に理由のない場合は[aizulab/coias-docker-compose](https://github.com/aizulab/coias-docker-compose)を使用するとよい。

## dockerについて

dockerを使用することで、アプリ環境を自動でホストPCに増やせる。

[Docker](https://www.docker.com/)

### 1. Dockerのインストール

### mac windownの場合

* docker desktop

[Docker Desktop for Mac and Windows | Docker](https://www.docker.com/products/docker-desktop)

### Linux(例：ubuntu)の場合

* docker engine

ubuntuの場合は下記のスクリプトが使用できる。
dockerを使用する際に`sudo`が必要になる。

[UbuntuにDockerEngineをインストールする| Dockerドキュメント](https://docs.docker.com/engine/install/ubuntu/#upgrade-docker-after-using-the-convenience-script)

### 2. 任意のディレクトリで以下のコマンドを打つ

```
git clone https://github.com/coias/coias-back-app.git.git
cd coias-back-app
```

### 3. テスト画像の入ったディレクトリ(SubaruHSC)を配置する

coias-back-app/SubaruHSCにテストようの画像などを配置する。

### 4. Dockerfileをビルド、実行する

```
docker build -t coias -f Dockerfile.dev . 

docker run -it --name coias \
--mount type=bind,source="$(pwd)"/data,target=/root/.coias \
--mount type=bind,source="$(pwd)"/SubaruHSC,target=/opt/SubaruHSC \
-p 8000:8000 coias /bin/bash
```

### 5. コマンドラインで以下を実行

```
coias activate coias-back-app
```

# 実行方法

1. 任意の好きなディレクトリに5枚のwarp画像 (warp-*.fits) を用意して、ターミナルでこのディレクトリに移動しておく。ほぼ全ての中間ファイルやpngファイルはこのディレクトリ (カレントディレクトリ) に展開される。

2. AstsearchR と打ち込んで同スクリプトを使用し、binning、マスク画像引き、光源検出、視野周辺の既知小惑星取得、移動天体検出、測光、pngファイル生成、などなどを実行する。

3. COIAS.py と打ち込んで、GUIで移動天体を目視で確認する。操作の詳細は省略するが、png画像を選び、blinkさせて移動天体だと思うものの四角を左クリックして選択し、選択が終わったらoutputを押してmemo.txtを出力させる。

4. ```prempedit```と打ち込んで、MPCフォーマットに再整形。

5. prempedit3.py [新天体の通し番号] と打ち込んで、名前の付け替え。第二引数に今まで自分が見つけた新天体の番号のうち一番大きいもの+1を指定する。

6. redisp と打ち込んでCOIASを再表示する準備。

7. ReCOIAS.py を実行するが、プログラムを準備していないので省略。

8. ReCOIAS.pyはCOIAS.pyで読み込むdisp.txtをredisp.txtに変えただけである。つまり、1度目のCOIAS.pyで選んだ天体のみに四角をつけて確認するだけ。

9.  mpc4.txtを複製してsend_mpc.txtに名前を書き換える。手作業。何回か測定した場合は、複数回の測定でできた複数のmpc4.txtの内容をまとめてsend_mpc.txtに記入しても良い。

10. AstsearchR_afterReCOIAS と打ち込んで同スクリプトを使用し、重複行の削除、findOrbを用いた軌道測定、誤差が大きいデータの削除、新天体に米印をつける、などを実行する。

11. 作成されたsend_mpc.txtが完成形で、MPCに送信する報告メールのデータ部分になる。

### たまにするべきこと

たまに実行して最新のMPCのデータベースを取り込んでおく。 初回はスクリプト中で自動で実行されるので、しなくて良い)

ターミナルで```getMPCORB_and_mpc2edb```と打ち込んで同スクリプトを実行することで、 MPCからMPCORB.DATを~/.coiasにダウンロードし、さらに解析してedb形式に書き換える。

~/.coiasは初回の実行時に自動で作られる隠しディレクトリ。