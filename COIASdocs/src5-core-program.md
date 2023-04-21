2023/04/16 Kenichi Ito

# src5_astsearch_new

## `astsearch_new`
- [`src2_startsearch2R`](./src2-core-program.md)で検出した光源から移動天体と思われる候補を自動検出し，既知天体との照合を行い, MPCフォーマットに変換するシェルスクリプト
- 実行内容
  1. `make_gathered_search_astB.py` [`src4_prempsearchC-after`](./src4-core-program.md)の最後に生成された既知天体リスト（`search_astB.txt`）をまとめてカレントディレクトリに取り出す
  2. `astsearch1M2_optimized.py` 移動天体候補の自動検出
  3. `match2D.py` 既知天体との照合
  4. `change_data_to_mpc_format.py` MPCフォーマットに変換
  5. ファイルを3種類のテキストファイルに整理
  6. `rm_should_modify_files` 再解析時に辻褄が合わなくなるファイルを削除

### `make_gathered_search_astB.py`
- 実行内容
  1. `precise_orbit_directories.txt` を読み込む
  2. `search_astB.txt` があるディレクトリを巡回し，各行に画像番号を追加する
  3. 全てのファイルを結合した`search_astB.txt` を作成する
  4. `bright_asteroid_MPC_names_in_the_field.txt` をカレントディレクトリにコピーする

### `astsearch1M2_optimized.py`
- 移動天体候補の自動検出と測光
- `TrackletClass`
  tracklet（線形に移動する光源の組）の情報を保持するクラス
    - コンストラクタ：2つの画像IDと初期のtrackletを受け取ってオブジェクトを生成
    - `add_data()` 画像IDとデータ点を受け取り，trackletに情報を追加
    - `del_data()`画像IDを受け取り，trackletから情報を削除
    - `merge_another_tracklet_to_this()` 別のtrackletの情報を自分に追加
    - `get_image_ids_for_predict()` 未検出の点がありそうな画像を推測して返す
    - `get_median_mag_of_this_tracklet()` trackletの等級の中央値を返す
    - `calculate_characteristic_properties()` trackletの情報をまとめて返す
    - `is_identical_to_another_tracklet` 2つのtrackletが同一かどうか，角度・速度・位置・等級から判定し，bool値で返す
- `detect_points_from_tracklets()`
  - 任意のtrackletから点を検出し，`trackletClassList`に追加する
  - 検出した点数が`N_DETECT_THRESH`より小さい場合はそのtrackletを削除する
- 実行内容
  1. データの読み込み，準備
    - FITSファイルからヘッダー情報を読み取る
    - テキストファイルから位置と明るさの情報を読取る
    - kd木の準備
  2. メインパート
    - `mktracklet_opt`（cythonで書かれている）を用いてtrackletを検出する
    - `trackletClassList`にtracklet情報を格納する
    - `detect_points_from_tracklets()`によって点の検出を行う
  3. 測光
    - 光源の明るさを算出し，`trackletListAll`に格納する
    - 中央値から明るさがかけ離れている点は削除する
  4. trackletの統合
    - 同じとみなせるtrackletかどうか判定し，trueであれば統合する
    - 統合後，不要になったtrackletに対しては`shouldBeDeleted`のフラグを立てる
    - `shouldBeDeleted`がtrueのものを削除する
  5. 出力
    - `listb2.txt`に結果を書き込む

### `match2D.py`
- `listb2.txt`は全ての移動天体候補を含んでいるので，既知天体と未知天体に分類し，前者を`match.txt`，後者を`nomatch.txt`に記入する
- 実行内容
  1. `listb2.txt`を読み込む（ない場合は空ファイルを出力して終了）
  2. `search_astB_*.txt`に一致するファイルを全て読み込む
  3. 両者のデータをマッチングする
  4. マッチしたデータを`match.txt`に，残りを`nomatch.txt`に書き込む

### `change_data_to_mpc_format.py`
- `match.txt`と`nomatch.txt`をMPCフォーマットに変換する
- その際，既知天体は仮符号付きか，確定番号付きかでさらに分類する
- 天体の種類3 x ファイル形式3の9個のテキストファイルが保存される
  - これらは，最終的に`astsearch_new`によって`mpc.txt`, `all.txt`, `disp.txt`に整理される
  - `mpc.txt`はMPCフォーマットに従う各行80文字のデータ, `all.txt`はMPCフォーマットに加え測光誤差やピクセル位置・画像番号などの情報も加えたデータ, `disp.txt`は天体名・ピクセル位置・画像番号など描画に必要最低限のデータである.
