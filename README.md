# 環境の構築方法

## 目次
- [検証したPC](#検証したPC)
  - [Dockerを使用した場合](#Dockerを使用した場合)
  - [PyCharmを利用した場合](#PyCharmを利用した場合)
- [実行方法](#実行方法)

## 検証したPC
  
機種ID:	MacBookPro11,3
プロセッサ名:	クアッドコアIntel Core i7

# Dockerを使用した場合

## 手順
### 1. Docker Desktopのインストール
   - <a href="https://www.docker.com/products/docker-desktop">Mac</a>
   - <a href="https://docs.docker.com/desktop/windows/install/">Windows</a>
### 2. 任意のディレクトリ(この場合は~/dev）配下にテスト画像の入ったディレクトリ(SubaruHSC)を配置する
### 3. ~/devの中で以下のコマンドを打つ
```
git clone https://github.com/Mizunanari/COIAS_program_github.git
cd COIAS_program_github
```
### 4. Dockerfileをビルド、実行する
```
docker build -t test-coias-image .
docker run -it test-coias-image 
```

### 5. コマンドラインで以下を実行
```
coias activate COIAS_program_github
```

### 6.　[実行方法](#実行方法)へ進む

# PyCharmを利用した場合

## IDE
  
[ダウンロード PyCharm：JetBrainsによるプロの開発者向けのPython IDE](https://www.jetbrains.com/ja-jp/pycharm/download/)

## パッケージ管理
  
* [Miniconda — Conda documentation](https://docs.conda.io/en/latest/miniconda.html)

* [Homebrew](https://brew.sh/index_ja)

## 手順

構築した手順。

### brewを使用してwgetをインストール

[Homebrew](https://brew.sh/index_ja)

```brew install wget```

### PyCharmをインストール

[JetBrains Toolbox App](https://www.jetbrains.com/ja-jp/toolbox-app/)

[PyCharm をインストールする | PyCharm](https://pleiades.io/help/pycharm/installation-guide.html)

### minicondaをインストール

[Miniconda — Conda documentation](https://docs.conda.io/en/latest/miniconda.html)

### インストールされたパスを調べる

```which conda```

### プロジェクトを作成

PyCharmよりconda環境にてプロジェクトを作成する

```https://github.com/Mizunanari/COIAS_program_github.git```

[Git リポジトリの設定 | PyCharm](https://pleiades.io/help/pycharm/set-up-a-git-repository.html#clone-repo)

[Python プロジェクトを作成する | PyCharm](https://pleiades.io/help/pycharm/creating-empty-project.html)

[Conda 仮想環境を構成する | PyCharm](https://pleiades.io/help/pycharm/conda-support-creating-conda-virtual-environment.html)

/COIAS_program_path以下の全てのpythonスクリプトとシェルスクリプトにchmodで実行許可を与えておく。

### パッケージのインストール

パッケージ依存関係の解決を行う。

### condaにチャンネルを追加

condaのインストールに使用するチャンネルを追加する。
tarminalから操作する。

```zsh
# 環境一覧
conda info -e

# 環境の切り替え
conda activate COIAS_program_github

# チャンネルの追加
conda config --append channels conda-forge
```

環境の切り替えを行うことで、terminalの表示が(base)から(COIAS_program_github)に変わる。

pythonのコード上で不足しているパッケージをインストール

[パッケージのインストール、アンインストール、アップグレード | PyCharm](https://pleiades.io/help/pycharm/installing-uninstalling-and-upgrading-packages.html)

pythonファイルのimportに赤下線が表示されているパッケージについて、カーソルをあわせパッケージをインストールする。
これをすべてのpythonファイルで行う。

下記はPyCharmからインストールできない。

* Julia
* PIL ([Pillow :: Anaconda.org](https://anaconda.org/anaconda/pillow))

代わりにPillowをインストール。

```conda install pillow```

### condaにないパッケージ

pipを使用してインストール

```pip install julian```

### EXtractorのインストール

```conda install -c conda-forge astromatic-source-extractor```

### AstsearchRをグローバルに設定

~/.zshrcにprojectのpathを追記。環境によって異なる。

```zsh
# coias pj
export PATH=$PATH:/Users/usuki/project/22/coias/COIAS_program_github
export PATH=$PATH:/Users/usuki/project/22/coias/COIAS_program_github/findOrb
```

設定の読み込み

```
source .zshrc
```

### Cython等のビルド

```https://github.com/Mizunanari/COIAS_program_github.git```をcloneしたファイルpathを```/COIAS_program_path```と記述している。

1. cythonのビルド。/COIAS_program_pathにターミナルで移動し、下のコマンドを実行
```
python setup12.py build_ext --inplace
```

もし既に一度コンパイルしたことがあったら、実行ファイル達を削除する

```
rm mktraclet.c mktraclet.cpython-39-darwin.so
```

2. findOrbのコンパイル。/COIAS_program_path/findOrb にターミナルで移動して、以下のコマンドを打つことでコンパイルを実行する。デフォルトのコンパイラは g++ なので、無い場合はインストールするか、持っているc++用のコンパイラを linlunar.make, linmake ファイル中の CC=コンパイラ名 に指定する必要がある。

もし既に一度コンパイルしたことがあったら、実行ファイル達を削除する

```
rm dos_findrm lunar.a
rm *.o
```

3. make

```
make -f linlunar.mak
make -f linmake
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
