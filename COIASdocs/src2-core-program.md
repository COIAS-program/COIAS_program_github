2023/01/04 Kenichi Ito

# src2_startsearch2R

## `startsearch2R`

- ビニング・マスク・光源検出などを統括するシェルスクリプト
- 実行内容
  1. `binning.py` ビニングを行う
  2. `subm2.py` マスクをかける
  3. `findsource_auto_thresh_correct.py` 光源検出を行う
  4. `search_precise_orbit_directories.py` 精密軌道情報がすでにあるかどうかチェック

### `binning.py`

- 元画像の **ビニング（複数ピクセルの結合）** を行い、処理済みの画像ファイルに変換する
- 実行内容
  1. FITS 画像ファイルを検索して順番に読み込み（[astropy.io.fits](https://docs.astropy.org/en/stable/io/fits/index.html)による）
  2. 2x2（または 4x4）の範囲で平均を取り、新しい画像を生成する
  3. 新しい画像にヘッダ情報を書き込み、保存する

### `subm2.py`

- ビニングされた画像データに対して恒星をマスク（隠す）処理し、FITS・PNG ファイルとして保存する
- 実行内容
  1. FITS 画像ファイルを検索して順番に読み込み（[astropy.io.fits](https://docs.astropy.org/en/stable/io/fits/index.html)による）
  2. 全ファイルのマスクデータを取得し、中央値（`median_maskdata`）を計算する
  3. 中央値が 0 の部分を 1、1 より大きい部分を 1 としたマスクデータを生成する
  4. マスクした部分を埋めるための背景画像（`image_sky`）を生成する
  5. マスクを乗算し、新規画像を保存する。また、PNG 画像（マスクあり・なし）も同時に保存する

### `findsource_auto_thresh_correct.py`

- `findsource`シェルスクリプトを実行し、SExtractor を用いた光源検出を行う。検出数が適切になるように閾値を調節する
- 実行内容
  1. 検出閾値（`detect_thresh`）を 1.2 として初回の処理を行う
  2. 検出数が定数`SOURCE_NUMBER`の 0.75 倍～ 1.25 倍の間になるまで閾値を二分探索する
  3. 探索を達成したら終了

### `search_precise_orbit_directories.py`

- 解析対象画像の位置から、取得済みの視野内の既知天体の精密軌道情報があるかどうか検索する
- 実行内容
  1. FITS 画像ファイルを検索して順番に読み込み、tract中心の赤経（RA）・赤緯（DEC）・観測時刻のユリウス日（JD）を取得する
  2. 精密軌道情報のファイルがあれば読み込み、なければディレクトリを作成する
  3. 解析対象画像の精密軌道情報を既に取得していたらその情報があるディレクトリへのパスを、取得したものがなければ新規ディレクトリへのパスを`precise_orbit_directories.txt`に書き出す
  4. 全ての解析対象画像で精密軌道情報を既に取得していた場合, `have_all_precise_orbits.txt`に1を書き込み, 次のsrc3_prempsearchC-beforeとsrc4_prempsearchC-afterをほとんどスキップする