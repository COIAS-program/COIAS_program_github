# COIAS の報告メール作成作業手順

1. COIAS での測定完了。例では mpcOeg.txt がまとまった状態。

2. mpcOeg.txt から重複行を取り除く。光源検出プログラムなどの影響で重複行あります。
それを取り除く作業。1 のファイルを hoge2.txt という名前にコピーした後、 deldaburi4.py を実行。mpc7.txt ができあがる。ただし 60 行目で警告出ます。解決して いません。=>杉浦さんにより解決済

3. お送りしたファイルを解凍してでできあがる findOrb ディレクトリ中に mpc7.txt を移 動させてコマンドラインで./dos_find mpc7.txt -k > result.txt を実行。目的は find_orb を実行したときの誤差 Xres, Yres や等級をファイル出力させる。中身はネットで落ち ている find_orb のプログラムの一部変更版。変更部分は dos_find.cpp 中に/KKK/とコ メントアウトされている部分。美星のスタッフが10年ぐらい前に作ったもの。-k オプ ションをつけることで find_orb の結果をテキスト出力できるようになっています。作 った本人ももうわからないとのこと。私は C++が素人なので内容わかっていません。 また、findOrb ディレクトリに入らないとプログラムが実行できないという不便さがあ ります。このあたりを改良してもらうととても助かります。その他、CentOS8 にアッ プデートしたら libncurses.so.5 がないとエラーがでました。未解決ですが他の古い PC では実行できています。=>杉浦さんにより解決済。

4. ./zansa2.sh で誤差が大きい(1 秒角以上)データのリスト(checklist.txt)を作る。2015 年 の観測データにしか対応できていません。=>杉浦さんにより解決済。

5. checklist.txt を見ながら mpc7.txt からエラーデータを削除。現在手作業。完成したのが mpc8.txt。

6. 赤緯の精度が小数点2桁になっている。これを1桁に直す。手作業。完成したのが pre_repo.txt。一部の特別の観測所は精度の高い小数点2桁の報告を受け付けてくれる らしいが多くの観測所は1桁しか受け取ってくれない。ここも自動化するか最初から 1桁にしておいた方が良い。

7. 新天体マークの記入。既知の天体でない観測データの内、最も時刻の若い観測データに *をつけることになっています。それを実行するプログラム komejirushi.py を実行。 mpc_reportOeg.txt(これでようやく完成)

8. MPC にメール送信(obs@cfa.harvard.edu)。ヘッダ部分に例えば以下の情報をつける。 そのうしろに mpc_reportOeg.txt の中身をコピペすれば良い。このあたりもメールを送 る GUI を作って測定者欄などを自由に編集できるようにしたい。

```
COD 568
CON S. Urakawa, Bisei Spaceguard Center, 1716-3, Okura, Bisei, CON Ibara, 714-1411 Okayama, Japan [urakawa@spaceguard.or.jp] OBS S. Urakawa, F. Yoshida, T. Terai
MEA S. Urakawa
TEL 8.2-m f/2.0 reflector + CCD(HSC)
NET Pan-STARRS(PS1) DR1 catalog
ACK
```

ヘッダ情報ここまで  

注)  
COD:天文台コード 568 はマウナケア。CON:対応する人の連絡先。OBS:観測者。MEA: 測定者。TEL:望遠鏡情報。NET:星表カタログ。ACK:必要な時のメッセージ欄。