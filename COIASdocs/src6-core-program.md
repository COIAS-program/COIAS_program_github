2023/04/16 Kenichi Ito

# src6_between_COIAS_and_ReCOIAS

## `AstsearchR_between_COIAS_and_ReCOIAS`
- `COIAS.py`でGUIを用いて選択した天体のH番号を付け替え，既知天体と選択した未知天体のみを残したリストを作成するシェルスクリプト
- 実行内容
  1. `prempedit2.py` 既知天体と選択した未知天体を抽出する
  2. `makeHlist` H番号付け替えの準備
  3. `prempedit3.py` mpc.txtのH番号付け替え
  4. `redisp.py` all.txtのH番号付け替え
  5. `correct_manual_delete_list.py` 手動測定モードから戻ってきた際に天体名が変わってしまうことを防ぐ


### `prempedit2.py`
- `mpc.txt`から，既知天体と選択した未知天体（`memo.txt`）を抽出し，`mpc2.txt`に書き出す

### `makeHlist`
- mpc2.txtから名前の部分を切り取り，Hから始まるものを重複なしで`Hlist.txt`に書き出すシェルスクリプト

### `prempedit3.py`
- `mpc2.txt`の新天体名を連番とした`mpc3.txt`を作成する．第2引数に開始番号を指定できる
- 実行内容
  1. `mpc2.txt`, `Hlist.txt`を読み込む
  2. 開始番号`firstH`を設定する
  3. `mpc2.txt`の天体名部分を新しいものに置換する
  4. `H_conversion_list.txt`にH番号の変換リストを出力
  5. 変換後のリストを`mpc3.txt`に出力
  6. `start_H_number.txt`に開始番号を出力

### `redisp.py`
- `mpc3.txt`の情報をもとに`all.txt`を更新して`newall.txt`，`predisp.txt`に書き出す
- 実行内容
  1. `all.txt`と`mpc3.txt`を開き，各行を読み込む
  2. `all.txt`の各行の15文字目から80文字目を取得する
  3. `mpc3.txt`の各行の15文字目から80文字目を取得し，`all.txt`の取得した文字列と比較する
  4. 一致するものがあれば，`mpc3.txt`の各行の14文字目までと，`all.txt`の取得した文字列の残りの部分を結合し，新しいリストに追加する
  5. 新しいリストをソートし，重複行を削除した結果を出力する. 最後の文字まで全て書き出したものは`newall.txt`, 描画に必要な位置などのみを書き出したものは`predisp.txt`になる.

### `correct_manual_delete_list.py`
- 手動測定モードから戻ってきた際に天体名が変わってしまうことを防ぐためのスクリプト
- 実行内容
  1. ファイルサイズが0でない`manual_delete_list2.txt`がある場合に実行する
  2. `H_conversion_list.txt`を基に，名前付替えの結果を反映したリストを作成し，`manual_delete_list.txt`を出力する
