2023/01/04 Kenichi Ito

# src1_preprocess

## `preprocess`

- 事前準備を行うシェルスクリプト
- 実行内容
  1. ディレクトリ、ログファイルの準備
  2. `make_default_parameter_files.py`の実行
  3. （MPCORB.DAT がないとき）`getMPCORB_and_mpc2edb` の実行

### `make_default_parameter_files.py`

- SExtractor と findOrb で使用するパラメータファイルの初期値を生成するスクリプト
- 実行内容
  1. `make_default_conv()` 畳み込みマスクの設定を生成する
  2. `make_default_sex(DETECT_MINAREA: int)` SExtractor で用いる設定を生成する
  3. `make_default2_param()` `default2.param`を生成する
  4. `make_ObsCodes_htm()` 天文台コードのリストを生成する
  5. `make_options_txt()` `options.txt`を生成する
  6. `make_rovers_txt()` Roving observer に関するテキストファイルを生成する
  7. `make_xdesig_txt()` 名称の異なる天体に関するテキストファイルを生成する

### `getMPCORB_and_mpc2edb`

- `minorplanetcenter.net`から最新の小惑星データを取得し、edb 形式に変換するシェルスクリプト

### `getMPCORB_and_mpc2edb_for_button`

- `minorplanetcenter.net`から最新の小惑星データを取得し、edb 形式に変換するシェルスクリプト
- 手動で小惑星データ更新ボタンを押した場合に実行される