# 実行手順メモ

coias実行手順のまとめ

## 前提条件

５枚画像(*.fits)を用意する

## 実行

1. AstsearchR

下記をまとめたもの

* binning
* マスク画像引き
* 高原検出
* 視野周辺の測地小惑星取得
* 移動天体検出
* 測光
* pngファイル生成

2. COIAS.py

guiアプリが実行。disp.txtを読み込む。outputで下記が出力される

-> memo.txt

3. prempedit

MPCフォーマットに再整形
memo.txt -> mpc2.txt -> hlist.txt

4. prempedit3.py

名前の付け替え
第二引数に今まで自分が見つけた新天体の番号のうち一番大きいもの+1を指定する。

__exa: hlist.txtの最後が`H000014`の場合__

```prempedit3.py 15```

-> mpc3.txt

5. redisp

COIASを再表示する準備。

-> redisp.txt

6. ReCOIAS.py

guiアプリの実行。
読み込むファイルはredisp.txt
(再測定モード)

7. 手作業

mpc4.txtを複製 -> rename「send_mpc.txt」

8. AstsearchR_afterReCOIAS

重複行の削除、indOrbを用いた軌道測定、誤差が大きいデータの削除、新天体に米印をつける、などを実行する。

-> result.txt -> pre_repo.txt -> send_mpc.txt

9. レポート

作成されたsend_mpc.txtが完成形で、MPCに送信する報告メールのデータ部分になる。

## 最新MPCデータの取得

* preprocess
* ~~getMPCORB_and_mpc2edb~~

 たまに実行して最新のMPCのデータベースを取り込んでおく。 初回はスクリプト中で自動で実行されるので、しなくて良い。
 
 /.coiasは初回の実行時に自動で作られる隠しディレクトリ。
 MPCデータはここに保存される。
