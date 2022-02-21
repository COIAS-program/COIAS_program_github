# /envについて

```
.
├── README.md
├── mac_env.yml
└── ubuntu_env.yml
```

* mac_env.yml

macでのconda環境構築にもちいる

* ubuntu_env.yml

ubuntuでのconda環境構築にもちいる

## conda コマンド

環境構築

```
conda env create -n coias -f ./env/mac_env.yml
```

activateで環境を切り替え

```
conda activate coias
```

パソコン内の環境を一覧表示

```
conda info -e
```

パッケージの確認

```
conda list
```

パッケージの書き出し

```
conda env export --no-builds > ./env/mac_env.yml
conda env export --no-builds > ./env/ubuntu_env.yml
```