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

### 環境構築

```
# macの場合
conda env create -n coias -f ./env/mac_env.yml
# ubuntuの場合
conda env create -n coias -f ./env/ubuntu_env.yml
```

#### ResolvePackageNotFoundが出た時の対処法

例）
```
ResolvePackageNotFound : 
      - xxxxxxx=12.0.0
      - xxxxxxx=14.0.0
```

この場合、'=12.0.0'と'=14.0.0'を消すと対応するversionを見つけて補完してくれる

### activateで環境を切り替え

```
conda activate coias
```

### パソコン内の環境を一覧表示

```
conda info -e
```

### パッケージの確認

```
conda list
```

### パッケージの書き出し

```
# macの場合
conda env export --no-builds > ./env/mac_env.yml
# ubuntuの場合
conda env export --no-builds > ./env/ubuntu_env.yml
```