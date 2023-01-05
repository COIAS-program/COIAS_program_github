2023/01/04 Kenichi Ito

# src4_prempsearchC-after

## `prempsearchC-after`

- 視野内にある既知天体をリスト化し、精密位置を取得するシェルスクリプト（後半）
- 実行内容
  1. `getinfo_karifugo2D.py` 仮符号小惑星の詳細位置を取得して保存する
  2. `make_search_astB_in_each_directory.py` 既知天体の位置情報のファイルを整形し、`precise_orbit_directories.txtに記載のディレクトリ/search_astB.txt`に出力する

### `getinfo_karifugo2D.py`

- `cand4.txt`に記載された仮符号小惑星の精密位置を JPL に問い合わせる
- 実行内容
  1. （`getinfo_numbered2D.py`と同じ流れ）
  2. 取得できた位置情報を`precise_orbit_directories.txtに記載のディレクトリ/karifugo_new2B.txt`に保存する
  3. tractの中心の赤経・赤緯と画像の観測時刻のjdと問い合わせ時刻を`precise_orbit_directories.txtに記載のディレクトリ/ra_dec_jd_time.txt`に保存する

### `make_search_astB_in_each_directory.py`

- 既知天体の位置情報のファイルを整形し、`precise_orbit_directories.txtに記載のディレクトリ/search_astB.txt`に出力する
- 実行内容
  1. `precise_orbit_directories.txtに記載のディレクトリ/karifugo_new2B.txt`と`precise_orbit_directories.txtに記載のディレクトリ/numbered_new2B.txt`を cat コマンドで結合する
  2. 整形したものを`precise_orbit_directories.txtに記載のディレクトリ/search_astB.txt`に保存する