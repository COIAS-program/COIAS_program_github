# COIAS_programの使い方

## 下準備

0.0. (Readme_COIAS2.pdfも参照してください) 3系のpythonのインストール。anaconda(pythonの統合開発環境)をインストールした方が良い。その上で以下のパッケージなどをインストールする: numpy, scipy, matplotlib, astropy, ephem, cython, pandas, pillow, photutils, SExtractor, astroquery, julian, beautifulsoup4, lxml

0.1. より簡単な方法: 3系のpythonがインストールされたanacondaをインストールしたのち、$bash env_setting.sh でほぼ環境構築が終わる。ただし環境によってはうまくインストールできない or 使えないパッケージがあったりするので、それらは手でインストールする。coiasという仮想環境上に環境を構築するので、シェルを開き直した後は $source activate coias で環境を切り替えれば使用可能。=> この方法でインストールした人は下準備6.までの全ての準備をスキップして実行方法から開始できる。

1. githubからこのプログラム一式をダウンロードして、任意のディレクトリに置く。本Readmeではこのディレクトリを /COIAS_program_path と呼ぶ。
2. /COIAS_program_path 以下の全てのpythonスクリプトとシェルスクリプトにchmodで実行許可を与えておく。
3. シェルの環境変数PATHに、このディレクトリへのパス (/COIAS_program_path) とfindOrbへのパス (/COIAS_program_path/findOrb) とソースファイルへのパス (/COIAS_program_path/COIASlibs および /COIAS_program_path/src1_preprocess から /COIAS_program_path/src8_astsearch_manual までの8つのディレクトリ) を追加する。使用するシェルはbashが前提のようなので、bashでパスを通す。
4. シェルの環境変数PYTHONPATHに、/COIAS_program_path/COIASlibs を追加する。
5. cythonのビルド。/COIAS_program_path/src5_astsearch_new にターミナルで移動して、 python setup12.py build_ext --inplace と入力する。
6. findOrbのコンパイル。/COIAS_program_path/findOrb にターミナルで移動して、以下のコマンドを打つことでコンパイルを実行する。デフォルトのコンパイラは g++ なので、無い場合はインストールするか、持っているc++用のコンパイラを linlunar.make, linmake ファイル中の CC=コンパイラ名 に指定する必要がある。
   1. もし一度コンパイルしたことがあったら、rm dos_find、rm lunar.a、rm *.o ですでにある実行ファイル達を削除する
   2. make -f linlunar.mak
   3. make -f linmake

## 実行方法
1. 任意の好きなディレクトリに5枚の同一領域を写したwarp画像(warp-*.fits)を用意して、ターミナルでこのディレクトリに移動しておく。ほぼ全ての中間ファイルやpngファイルはこのディレクトリ (カレントディレクトリ) に展開される。2022/5/19追記: プログラム全体は画像5枚の場合で最適化されているが、現在は任意の枚数の解析に対応している。
2. AstsearchR と打ち込んで同スクリプトを使用し、binning、マスク画像引き、光源検出、視野周辺の既知小惑星取得、移動天体検出、測光、pngファイル生成、などなどを実行する。AstsearchR は以下のスクリプトの羅列であり、AstsearchR を実行することは以下のスクリプトを順に実行することと同じである。途中でエラーが出た時などは、AstsearchR を始めから実行しなくてもエラーが出た箇所から以下のスクリプトを順に実行し直しても良い。
   1. preprocess
   2. startsearch2R [フローチャート](flowcharts/flowchart1-startsearch2R.md)
   3. prempsearchC-before
   4. prempsearchC-after
   5. astsearch_new
3. COIAS.py と打ち込んで、searchモードにてGUIで移動天体を目視で確認する。COIAS.py を実行すると画面が1つ開くが、まずはその画面のCOIAS mode欄の「search」ラジオボタンを選ぶ。お好みに応じてマスクあり画像かマスクなし画像かを「image preference」ラジオボタンから選べる。選んだら「Load img」ボタンを押すとメインGUI画面が開くので。画像をブリンクさせ、移動天体だと思う天体の四角をクリックして、その四角を赤くする。一通り選び終えたら右上の「Output」ボタンを押して memo.txt を出力させる。[詳しい COIAS.py の操作方法はこちら](COIASdocs/READMECOIAS.md)
4. AstsearchR_between_COIAS_and_ReCOIAS [新天体の通し番号] と打ち込む。第二引数に今まで自分が見つけた新天体の番号のうち一番大きいもの+1を指定する。この作業で、新天体と同定したもののデータをMPCフォーマットに再整形、名前の付け替え、ReCOIAS を再表示する準備をする。
5. COIAS.py と打ち込んで、manual measureモードにて自動検出できなかった天体を測定する。詳しい使い方は[こちら](COIASdocs/READMECOIAS.md)に記載するが、自動検出されていないが移動天体だと思う光源をクリックし、拡大画面で3点をクリックし四角形アパーチャーを設置する。一通り選び終えたら右上の「Output」ボタンを押して memo_manual.txt を出力させる。
6. AstsearchR_after_manual と打ち込んで、手動測定天体の測光および既知天体との照合を行う。
7. COIAS.py と打ち込んで、reconfirm/modify nameモードにて選択・測定した天体が本当に移動天体であるかどうか目視で再確認する。他、自動検出である移動天体の光源をいくつか検出し損ねていた時、その検出漏れした光源を手動測定で測定しても天体番号が自動検出のものと変わってしまうので、同じ移動天体とみなさせるために新天体の名前を任意に変更できる。詳しい使い方は[こちら](COIASdocs/READMECOIAS.md)。結果が良さそうなら特段の操作は不要で、画面を閉じて良い。
8. AstsearchR_afterReCOIAS と打ち込んで同スクリプトを使用し、重複行の削除、findOrbを用いた軌道測定、誤差が大きいデータの削除、新天体に米印をつける、などを実行する。
9. 作成された send_mpc.txt が完成形で、MPCに送信する報告メールのデータ部分になる。自分で必要なヘッダ情報を追加してMPCにメールで報告するか、本プロジェクト開発主任の浦川まで send_mpc.txt をメールに添付して送付すること。また、final_all.txt に元fitsファイルの名前や検出された移動天体の詳細情報が記載されている。
10. send_mpc.txt に記載の天体名は、最終的に連番になるように付け替えられている。またfindOrbによって弾かれた検出点もあったりする。その結果をGUIで視認したければ、COIAS.py の final checkモードを使用すること。

## たまにするべきこと
1. (たまに実行して最新のMPCのデータベースを取り込んでおく。 初めて AstsearchR を実行した時はスクリプト中で自動で取り込まれるので、しなくて良い) ターミナルで getMPCORB_and_mpc2edb と打ち込んで同スクリプトを実行することで、 MPCからMPCORB.DATを~/.coias/param にダウンロードし、さらに解析してedb形式に書き換える。~/.coias以下は初回の AstsearchR 実行時に自動で作られる隠しディレクトリ。

## パラメータについて
1. binning(元画像を粗視化すること)を2x2か4x4のどちらか選ぶことができる(基本的に2x2を推奨)。startseach2R を実行すると始めの方でどちらが良いか聞かれるので、2か4のどちらかを打ち込む必要がある。
2. 自動検出(astsearch_new)で、何枚以上検出したら移動天体と見なすのか、測光のアパーチャー半径[pixel]、移動天体を自動検出する際の移動速度の上限値[arcsec/min]をオプションにて設定できる。AstsearchR もしくは astsearch_new を実行するときに、それぞれ nd=\*、ar=\*、vt=\*、の書式で引数に指定することで設定できる (nd: N detection、ar: aparture radius、vt: velocity thresholdの略)。例) AstsearchR nd=5 ar=7 vt=3.0。オプションを指定する順番は問わず、順不同である。特に指定しない時は、nd=4、ar=6、vt=1.5がデフォルトの値として設定される。
3. 事前処理(preprocess)で、SExtractorの解析で何ピクセル以上明るい場所が連結していたら光源と見なすのかを[pixel]単位でオプションにて指定できる。AstsearchR もしくは preprocess を実行する時に、dm=\*、の書式で引数に指定することで設定できる (dm: DETECTION MINAREAの略)。例) AstsearchR dm=15。2.で説明したパラメータと同時に設定できる。例) AstsearchR dm=15 nd=5 ar=7 vt=3.0。特に指定しない時は、dm=6がデフォルトの値として設定される。ノイズが多すぎて解析に支障を来すと思われる時はこの値を増やすと良い。
4. ビニングマスク(startsearch2R)で、SExtractorによって検出される光源数の平均値の大雑把な上限を指定できる。AstsearchR もしくは startsearch2R を実行する時に、sn=\*、の書式で引数に指定することができる (sn: source numberの略)。 例) AstsearchR sn=300。これも2.3.で説明したパラメータと同時に設定でき、順不同である。特に指定しない時は、sn=2000がデフォルトの値として設定される。こちらもノイズの数を少なくする効果があるが、3.よりも小さな移動天体を逃しにくいかもしれない。(試行錯誤が必要) 注: 3.はSExtractorのDETECT_MINAREAを直接指定するパラメータであるが、4.はDETECT_THRESHを調整することで検出光源数をsnの値に近づけるという動作をする。また検出光源数がsnの値よりも少ない時はDETECT_THRESH=1.2をそのまま使用し、あえて検出光源数を増やしてsnの値に近づけるということはしない。
5. Astsearch_afterReCOIAS の delLargeZansa_and_modPrecision.py の第二引数にて、MPCに報告する赤緯(dec)の秒の小数点以下の精度を指定できる。デフォルトでは1桁で、特に精度を要求される時には2桁にする必要があるらしい。1桁必要なら第二引数に1を、2桁必要なら2を指定する。