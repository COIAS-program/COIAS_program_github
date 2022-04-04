# SSP データのダウンロード方法
(信用しないようにダウンロード経験一回。記載は浦川の理 解です。これをヒントに試行錯誤してください)
1. Hyper Suprime-Cam Subaru Strategic Program の web サイトで、アカウントを作る。

https://hsc-release.mtk.nao.ac.jp/doc/index.php/tools-2/

2. いろいろとデータの探し方はあると思うが詳しい方法はわかっていない。ここではひと まずうまくいった DAS Search Form で 2016 の deep サーベイのデータから⻩道面付近 のデータをダウンロードする方法を示す。
3. 以下のページから SSP で⻩道面をサーベイしている観測を探す。DEEP2 が適している よ う だ 。 https://hsc-release.mtk.nao.ac.jp/doc/index.php/survey-2/#1486969193563- b5ec24a4-7968
4. 改めて、Data Access のページに戻り、DAS(Data Archive System) Search Form をクリ ック。右上 2 段目に field map というタグがあるので、そこから Release=> (U)DEEP =>DEEP2-3 とマウスを選択すると DEEP2-3 というサーベイマップがでてくる。座標 は赤道座標。数字が書かれていて、それが Tracts 番号。Tract 番号とは、サーベイ領域 をナンバリングしたもの。ここでは 9464 と 9707 領域をダウンロードしよう。
5. Region, Date, &c の欄で NB(ナローバンド)filter のチェックを外す。別につけても良 いけど限界等級が浅そうだし、MPC フォーマットが対応していないので外す。Tracts に 9464 9707 と記入。9464 と 9707 の間はスペース
6. File type は coadds と images のみにチェック
7. Rerun は U/DEEP にのみチェック
8. Search ボタンを押す
9. 容量が多かったので 9464、フィルターG、R、I だけにしてみた。
10. URL list (Text)をクリック
11. ファイル一覧が出てくる。これを wget で取得する。さてどうするか。URL list(Text)を クリックした時の url をどこかにコピーしておく
12. 以下のコマンドでダウンロードできたようだ。
wget --force-directories ‒user=urakawa@local --ask-password --input-fille=ʼ先程の url アド レスʼ
13. wget を実行したディレクトリ以下に hsc-release.mtk.nao.ac.jp のディレクトリができて
いる。
14. 例 え ば 、 ./hsc-release.mtk.nao.ac.jp/archive/filtertree/pdr2_dud/deepCoadd/HSC-
R/9464/2,6 とかに画像データがある。この画像データから 1 日で 5 回 visit しているデ ータを探して、それを一つのディレクトリにおく。このディレクトリで COIAS 実施。 画像はディザリングしている場合が多いので 5 回 visit していても視野の端にしか画像 がない場合もある。視野の半分以上ぐらいをカバーしている画像を選ぶこと。ここはま だ手動。