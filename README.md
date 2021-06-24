#COIAS_programの使い方

##下準備
1. githubからこのプログラム一式をダウンロードして、任意のディレクトリに置く。このディレクトリを /COIAS_program_path とする。
2. 全てのpythonスクリプトとシェルスクリプトにchmodで実行権限を与えておく。
3. シェルの環境変数PATHに、このディレクトリへのパス (/COIAS_program_path) とfindOrbへのパス (/COIAS_program_path/findOrb) を追加する。
4. cythonのビルド。/COIAS_program_path にターミナルで移動して、 python setup12.py build_ext --inplace と入力する。
5. /COIAS_program_path 以下に存在する隠しディレクトリ .COIAS_param をホームディレクトリ以下 (~/) にコピーする。
6. (たまに実行して最新のMPCのデータベースを取り込んでおく) ターミナルで getMPCORB_and_mpc2edb と打ち込んで同スクリプトを実行することで、 MPCからMPCORB.DATを~/.COIAS_paramにダウンロードし、さらに解析してedb形式に書き換える。
