# COIAS_programの使い方

## 下準備
0. (Readme_COIAS2.pdfも参照してください) 3系のpythonのインストール。anaconda(pythonの統合開発環境)をインストールした方が良い。その上で以下のパッケージなどをインストールする: numpy, scipy, matplotlib, astropy, ephem, cython, pandas, pillow, photutils, SExtractor, astroquery, julian
1. githubからこのプログラム一式をダウンロードして、任意のディレクトリに置く。本Readmeではこのディレクトリを /COIAS_program_path と呼ぶ。
2. /COIAS_program_path以下の全てのpythonスクリプトとシェルスクリプトにchmodで実行許可を与えておく。
3. シェルの環境変数PATHに、このディレクトリへのパス (/COIAS_program_path) とfindOrbへのパス (/COIAS_program_path/findOrb) を追加する。使用するシェルはbashが前提のようなので、bashでパスを通す。(以前COIASのプログラム群を使用しており昔のパスが残っている場合は、使用したいプログラム群へのパスのみが環境変数PATHに登録されるように注意する)
4. cythonのビルド。/COIAS_program_path にターミナルで移動して、 python setup12.py build_ext --inplace と入力する。
5. findOrbのコンパイル。/COIAS_program_path/findOrb にターミナルで移動して、以下のコマンドを打つことでコンパイルを実行する。デフォルトのコンパイラは g++ なので、無い場合はインストールするか、持っているc++用のコンパイラを linlunar.make, linmake ファイル中の CC=コンパイラ名 に指定する必要がある。
   1. もし一度コンパイルしたことがあったら、rm dos_find, rm lunar.a, rm *.o ですでにある実行ファイル達を削除する
   2. make -f linlunar.mak
   3. make -f linmake

## 実行方法
1. 任意の好きなディレクトリに5枚のwarp画像 (warp-*.fits) を用意して、ターミナルでこのディレクトリに移動しておく。ほぼ全ての中間ファイルやpngファイルはこのディレクトリ (カレントディレクトリ) に展開される。
2. AstsearchR と打ち込んで同スクリプトを使用し、binning、マスク画像引き、光源検出、視野周辺の既知小惑星取得、移動天体検出、測光、pngファイル生成、などなどを実行する。
3. COIAS.py と打ち込んで、GUIで移動天体を目視で確認する。操作の詳細は省略するが、png画像を選び、blinkさせて移動天体だと思うものの四角を左クリックして選択し、選択が終わったらoutputを押してmemo.txtを出力させる。
4. prempedit と打ち込んで、MPCフォーマットに再整形。
5. prempedit3.py [新天体の通し番号] と打ち込んで、名前の付け替え。第二引数に今まで自分が見つけた新天体の番号のうち一番大きいもの+1を指定する。
6. redisp と打ち込んでCOIASを再表示する準備。
7. ReCOIAS.py を実行するが、プログラムを準備していないので省略。ReCOIAS.pyはCOIAS.pyで読み込むdisp.txtをredisp.txtに変えただけである。つまり、1度目のCOIAS.pyで選んだ天体のみに四角をつけて確認するだけ。
8. mpc4.txtを複製してsend_mpc.txtに名前を書き換える。手作業。何回か測定した場合は、複数回の測定でできた複数のmpc4.txtの内容をまとめてsend_mpc.txtに記入しても良い。
9. AstsearchR_afterReCOIAS と打ち込んで同スクリプトを使用し、重複行の削除、findOrbを用いた軌道測定、誤差が大きいデータの削除、新天体に米印をつける、などを実行する。
10. 作成されたsend_mpc.txtが完成形で、MPCに送信する報告メールのデータ部分になる。

## たまにするべきこと
1. (たまに実行して最新のMPCのデータベースを取り込んでおく。 初回はスクリプト中で自動で実行されるので、しなくて良い) ターミナルで getMPCORB_and_mpc2edb と打ち込んで同スクリプトを実行することで、 MPCからMPCORB.DATを~/.coiasにダウンロードし、さらに解析してedb形式に書き換える。~/.coiasは初回の実行時に自動で作られる隠しディレクトリ。

# COIAS、とても粗い手順解説。

すばるのデータ解析は大変だと思うのでテスト画像(warp 画像)を 5 枚用意しました。まず はそれを使ってください。プログラム群を置く所とは別のディレクトリに置くと良いと思 います。天文画像は ds9 というソフトをインストールすると見ることができます。
3 系の python を前提としています。私は ipython でプログラム開発しています。必要なモ ジュールは numpy,scipy,matplotlib などの科学系の定番+天文系の astropy,photutils などで す。他にも必要なものがあると思いますが本人が把握しきれていません(cython も一部使っ ています)。anaconda で環境設定すると良いと思います。anaconda と pip を併用しすぎる とたまにうまく動かないことがあるそうです。できるだけ anaconda で環境設定すると良い と思います。何言っているかよくわからないと思いますが、まずは上記の単語を google 先 生に聞いてみてください。作業で分からない点は、遠慮なくメールください。
0. warp 画像を特定のディレクトリに 5 枚置く.以下のプログラムはそのディレクトリで実 行
1. プログラム群を特定のディレクトリに置く.これまでプログラムの多くは私の PC 環境 に合わせて/home/urakawa/bin/Asthunter/の下となっている。適時変えてください MPCORB.DAT もここに置く。
2. AstsearchR スクリプトが根幹となる。
3. AstsearchR で最初に実行しているのが startsearch2R スクリプト
4. startsearch2R で実行しているのがビニングをする binnning2R プログラムとマスク画像
を引く subm2.py プログラム。さらに findsource スクリプトで SExtractor を使った光源
検出.SExtractor は事前に実行できるように設定しておく必要あり。
5. AstsearchR で 2 番目に実行しているのが prempsearchC スクリプト.
6. prempsearchC は一つの視野に対して 1 回実行すれば良い。全小惑星の軌道情報を edb
ファイルに変換し(mpc2edb.pl)、視野近辺の±1.8 度のものを選択し(searchB.py)、それ
らを JPL に問い合わせる(getinfo_numbered2D.py, getinfo_karifugo2D.py)
7. AstsearchR で 3 番目に実行しているのが astsearch_new スクリプト.
8. astsearch_new で実行しているのが、移動天体検出と測光を行うプログラム
astsearch1M.py あるいは astsearch1P.py。ここで、cython を使っている。setup12.py の 一番下の行をコマンドラインで実行させておかないといけない。さらに既知天体とのマ ッチングを行うプログラム match2D.py, MPC フォーマットなどへ変換するプログラム mpc1b.py と mpc2b.py
9. fits2png プログラムで png ファイルへ変換
10. ここからは GUI
11. COIAS と打てば COIAS 起動
12. COIAS に新天体の番号を記述して OUTPUT ボタン
13. prempedit プログラムで MPC フォーマットに再整形
14. prempedit3.py [新天体の通し番号]で名前の付け替え
15. redisp プログラムで COIAS を再表示する準備
16. ReCOIAS プログラム起動。COIAS で選択した天体がノイズでないか、あるいは検出漏
れがないか確認
17. このあと FINDORB プログラムでの誤測定チェックなどありますがひとまずここまで
です。

# COIAS の報告メール作成作業手順

1. COIAS での測定完了。例では mpcOeg.txt がまとまった状態。
2. mpcOeg.txt から重複行を取り除く。光源検出プログラムなどの影響で重複行あります。
それを取り除く作業。1 のファイルを hoge2.txt という名前にコピーした後、 deldaburi4.py を実行。mpc7.txt ができあがる。ただし 60 行目で警告出ます。解決して いません。=>杉浦さんにより解決済
3. お送りしたファイルを解凍してでできあがる findOrb ディレクトリ中に mpc7.txt を移 動させてコマンドラインで./dos_find mpc7.txt -k > result.txt を実行。目的は find_orb を実行したときの誤差 Xres, Yres や等級をファイル出力させる。中身はネットで落ち ている find_orb のプログラムの一部変更版。変更部分は dos_find.cpp 中に/KKK/とコ メントアウトされている部分。美星のスタッフが10年ぐらい前に作ったもの。-k オプ ションをつけることで find_orb の結果をテキスト出力できるようになっています。作 った本人ももうわからないとのこと。私は C++が素人なので内容わかっていません。 また、findOrb ディレクトリに入らないとプログラムが実行できないという不便さがあ ります。このあたりを改良してもらうととても助かります。その他、CentOS8 にアッ プデートしたら libncurses.so.5 がないとエラーがでました。未解決ですが他の古い PC では実行できています。=>杉浦さんにより解決済。
4. ./zansa2.sh で誤差が大きい(1 秒角以上)データのリスト(checklist.txt)を作る。2015 年 の観測データにしか対応できていません。=>杉浦さんにより解決済。
5. checklist.txt を見ながら mpc7.txt からエラーデータを削除。現在手作業。完成したのが mpc8.txt。
6. 赤緯の精度が小数点2桁になっている。これを1桁に直す。手作業。完成したのが pre_repo.txt。一部の特別の観測所は精度の高い小数点2桁の報告を受け付けてくれる らしいが多くの観測所は1桁しか受け取ってくれない。ここも自動化するか最初から 1桁にしておいた方が良い。
7. 新天体マークの記入。既知の天体でない観測データの内、最も時刻の若い観測データに *をつけることになっています。それを実行するプログラム komejirushi.py を実行。 mpc_reportOeg.txt(これでようやく完成)
8. MPC にメール送信(obs@cfa.harvard.edu)。ヘッダ部分に例えば以下の情報をつける。 そのうしろに mpc_reportOeg.txt の中身をコピペすれば良い。このあたりもメールを送 る GUI を作って測定者欄などを自由に編集できるようにしたい。
COD 568
CON S. Urakawa, Bisei Spaceguard Center, 1716-3, Okura, Bisei, CON Ibara, 714-1411 Okayama, Japan [urakawa@spaceguard.or.jp] OBS S. Urakawa, F. Yoshida, T. Terai
 
MEA S. Urakawa
TEL 8.2-m f/2.0 reflector + CCD(HSC)
NET Pan-STARRS(PS1) DR1 catalog
ACK
ヘッダ情報ここまで
注)
COD:天文台コード 568 はマウナケア。CON:対応する人の連絡先。OBS:観測者。MEA: 測定者。TEL:望遠鏡情報。NET:星表カタログ。ACK:必要な時のメッセージ欄。

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

# COIAS の使い方(手動測定付き編)
0. getinfo_numbered と getinfo_karifugo はスクリプトで実行しない方が良い。GUI のボ
タンにしてもらおう。astsearch_new の内容を実行させて、小惑星探しをできる状態に
する。
1. 自動検出に関しはクリックする。すべて選択したら OutPut ボタンを押す。
2. 手動測定する天体にカーソルを合わせてスペースバー
3. “Same object with a previous image?”と聞かれるので 1 枚目なら No を選択。自動検出
と重複しない大きめの数字を打つ。Blink して画像を進める。2 枚目以降は yes を選択。
4. ここで一旦 Quit ボタン
5. astsearch_manual とコマンドラインで打つと matplotlib な画面で手動測定する光源の
  クローズアップ画面がでてくる。
6. 四角形のアパーチャーが設定できるので、光源を取り囲むお好みの四角形をつくるべく
3 点をクリックする。 7. クリックしたら右上の
✖ボタンで画像を一旦消す。すぐさまに四角形のアパーチャーが 記された画像が再描画される。もしそのアパーチャーで良ければどこでも良いのでダブ
 ルクリックする。気に入らなければもう一回3点を選択する。
8. ✖ボタンで次の画像になる。以下同じ
9. prempedit
10. prempedit3.py 続きの天体番号
(続きの天体番号とは MPC 送信済みの H 番号の次の数字部分のみを打つ。最新が
H006367 なら 6368 と打つ。)
11. redisp
12. ReCOIAS.py 確認
13. mpc4.txt ができる。以降は改良の余地があるが、README.md と同じ.最終的に
send_repo.txt ができあがる。ひとまずここまで。