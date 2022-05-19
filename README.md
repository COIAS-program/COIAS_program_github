#COIAS_programの使い方

##下準備

0.0. (Readme_COIAS2.pdfも参照してください) 3系のpythonのインストール。anaconda(pythonの統合開発環境)をインストールした方が良い。その上で以下のパッケージなどをインストールする: numpy, scipy, matplotlib, astropy, ephem, cython, pandas, pillow, photutils, SExtractor, astroquery, julian

0.1. より簡単な方法: 3系のpythonがインストールされたanacondaをインストールしたのち, $bash env_setting.sh でほぼ環境構築が終わる. ただし環境によってはうまくインストールできない or 使えないパッケージがあったりするので, それらは手でインストールする. coiasという仮想環境上に環境を構築するので, シェルを開き直した後は $source activate coias で環境を切り替えれば使用可能. => この方法でインストールした人は下準備6.までの全ての準備をスキップして実行方法から開始できる.

1. githubからこのプログラム一式をダウンロードして、任意のディレクトリに置く。本Readmeではこのディレクトリを /COIAS_program_path と呼ぶ。
2. /COIAS_program_path以下の全てのpythonスクリプトとシェルスクリプトにchmodで実行許可を与えておく。
3. シェルの環境変数PATHに、このディレクトリへのパス (/COIAS_program_path) とfindOrbへのパス (/COIAS_program_path/findOrb) とソースファイルへのパス (/COIAS_program_path/COIASlibs および /COIAS_program_path/src1_preprocess から /COIAS_program_path/src8_astsearch_manual までの8つのディレクトリ) を追加する。使用するシェルはbashが前提のようなので、bashでパスを通す。(以前COIASのプログラム群を使用しており昔のパスが残っている場合は、使用したいプログラム群へのパスのみが環境変数PATHに登録されるように注意する)
4. シェルの環境変数PYTHONPATHに、/COIAS_program_path/COIASlibs を追加する。
5. cythonのビルド。/COIAS_program_path/src5_astsearch_new にターミナルで移動して、 python setup12.py build_ext --inplace と入力する。
6. findOrbのコンパイル。/COIAS_program_path/findOrb にターミナルで移動して、以下のコマンドを打つことでコンパイルを実行する。デフォルトのコンパイラは g++ なので、無い場合はインストールするか、持っているc++用のコンパイラを linlunar.make, linmake ファイル中の CC=コンパイラ名 に指定する必要がある。
   1. もし一度コンパイルしたことがあったら、rm dos_find, rm lunar.a, rm *.o ですでにある実行ファイル達を削除する
   2. make -f linlunar.mak
   3. make -f linmake

##実行方法
1. 任意の好きなディレクトリに5枚の同一領域を写したwarp画像(warp-*.fits)を用意して、ターミナルでこのディレクトリに移動しておく。ほぼ全ての中間ファイルやpngファイルはこのディレクトリ (カレントディレクトリ) に展開される。2022/5/19追記: プログラム全体は画像5枚の場合で最適化されているが、現在は任意の枚数の解析に対応している。
2. AstsearchR と打ち込んで同スクリプトを使用し、binning、マスク画像引き、光源検出、視野周辺の既知小惑星取得、移動天体検出、測光、pngファイル生成、などなどを実行する。
3. COIAS.py と打ち込んで、GUIで移動天体を目視で確認する。操作の詳細は省略するが、png画像を選び、blinkさせて移動天体だと思うものの四角を左クリックして選択し、選択が終わったらoutputを押してmemo.txtを出力させる。
4. AstsearchR_between_COIAS_and_ReCOIAS [新天体の通し番号] と打ち込む。第二引数に今まで自分が見つけた新天体の番号のうち一番大きいもの+1を指定する。この作業で、新天体と同定したもののデータをMPCフォーマットに再整形、名前の付け替え、ReCOIASを再表示する準備をする。
5. ReCOIAS.py を実行する。ReCOIAS.pyはCOIAS.pyとほぼ同じであるが、既知天体とCOIAS.pyで新天体だと同定したもののみが表示される。この画面で改めて同定したものが新天体かどうか視認して再確認する。結果が良さそうなら特段の操作は不要で、画面を閉じて良い。
6. mpc4.txtを複製してsend_mpc.txtに名前を書き換える。手作業。何回か測定した場合は、複数回の測定でできた複数のmpc4.txtの内容をまとめてsend_mpc.txtに記入しても良い。
7. AstsearchR_afterReCOIAS と打ち込んで同スクリプトを使用し、重複行の削除、findOrbを用いた軌道測定、誤差が大きいデータの削除、新天体に米印をつける、などを実行する。
8. 作成されたsend_mpc.txtが完成形で、MPCに送信する報告メールのデータ部分になる。

##たまにするべきこと
1. (たまに実行して最新のMPCのデータベースを取り込んでおく。 初回はスクリプト中で自動で実行されるので、しなくて良い) ターミナルで getMPCORB_and_mpc2edb と打ち込んで同スクリプトを実行することで、 MPCからMPCORB.DATを~/.coias/param にダウンロードし、さらに解析してedb形式に書き換える。~/.coias以下は初回の実行時に自動で作られる隠しディレクトリ。
