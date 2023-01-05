2023/01/04 Kenichi Ito

# src3_prempsearchC-before

## `prempsearchC-before`

- 視野内にある既知天体をリスト化し、精密位置を取得するシェルスクリプト（前半）
- 実行内容
  1. `have_all_precise_orbits.txt`を参照し、取得済みの位置データがない場合のみ取得操作を行う
  2. `searchB.py` 暗い既知天体を探索する
  3. `searchB_AstMPC.py` 明るい既知天体を探索する
  4. 結果を`cand.txt`にまとめ、整形する
  5. 確定番号付き小惑星の一覧を`cand3.txt`に、仮符号小惑星の一覧を`cand4.txt`に書き出す
  6. `make_asteroid_name_list_in_the_field.py` 15等級以上の明るい既知小惑星の一覧を保存する
  7. `getinfo_numbered2D.py` 確定番号付き小惑星の詳細位置を取得して保存する

### `searchB.py`

- `~/.coias/param/AstMPC_dim.edb`に記載の**暗い**既知小惑星の一覧から、視野内にあるものを抽出す
- 実行内容
  1. 1枚目の FITS 画像ファイルを検索して読み込み、tract中心の赤経（RA）・赤緯（DEC）・観測時刻のユリウス日（JD）を取得する
  2. 並列処理で、視野内（中心から ±1.8 度以内）の小惑星を`search()`関数で探索する
  - `search()`は、すばる望遠鏡の地点から天体の視方向を算出し、それが視野の範囲にあれば天体情報を返す
  - 計算には天体位置計算ライブラリ[PyEphem](https://rhodesmill.org/pyephem/index.html)を利用している
  3. 結果を`cand_dim.txt`に保存する

### `searchB_AstMPC.py`

- `~/.coias/param/AstMPC.edb`に記載の**明るい**既知小惑星の一覧から、視野内にあるものを抽出する
- 実行内容
  1. （`searchB.py`と同じ流れ）
  2. 天体名のみのリストを`bright_asteroid_raw_names_in_the_field.txt`に保存する

### `make_asteroid_name_list_in_the_field.py`

- 報告が不要な明るい小惑星を除外するためのリストを作成する
- 実行内容
  1. `bright_asteroid_raw_names_in_the_field.txt`を整形して天体名を取り出す
  2. 天体名を MPC フォーマットのものに変換し、`brightAsteroidsMPCNames`配列に並べ、`precise_orbit_directories.txtに記載のディレクトリ/bright_asteroid_MPC_names_in_the_field.txt`に保存する

### `getinfo_numbered2D.py`

- `cand3.txt`に記載された確定番号付き小惑星の精密位置を JPL に問い合わせる
- 実行内容
  1. `have_all_precise_orbits.txt`を参照し、取得済みの位置データがない場合のみ取得操作を行う
  2. `precise_orbit_directories.txt`、FITS 画像、`cand3.txt`の読み込み
  3. 並列処理で、天体ごとに JPL への問い合わせを実行する（[astroquery.jplhorizons](https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html)を使用）
  4. エラーで取得できなかった天体に関して再度 JPL へ問い合わせる
  5. 取得できた位置情報を`precise_orbit_directories.txtに記載のディレクトリ/numbered_new2B.txt`に保存する