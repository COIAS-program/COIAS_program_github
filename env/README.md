# /envについて

```
.
├── README.md
├── env.yml
└── ubuntu_env.yml
```

__env.yml__

必要なパッケージのみ記載。依存関係については記載しない。  
パッケージを追加する際はこちらに手動で追加する。

__ubuntu_env.yml__

ubuntuでのconda環境構築にもちいる。  
インストール高速化およびバージョン固定のために使用。

## パッケージ追加手順

1. パッケージがcondaにあるかどうかや名称をcondaのページで確認する。
2. env.ymlに手動で追加する。
3. env.ymlを使用して環境を構築する
4. その後、ubuntu_env.ymlに環境を[書き出す](#パッケージの書き出し)。

## conda コマンド

### 環境構築

```
# 最新版を入れる場合
conda env create -n coias -f ./env/mac_env.yml
# 固定されたバージョンを導入するの場合
conda env create -n coias -f ./env/ubuntu_env.yml
```

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
# ubuntuの場合
conda env export --no-builds > ./env/ubuntu_env.yml
```

#### ResolvePackageNotFoundが出た時の対処法

例）
```
ResolvePackageNotFound : 
      - xxxxxxx=12.0.0
      - xxxxxxx=14.0.0
```

この場合、'=12.0.0'と'=14.0.0'を消すと対応するversionを見つけて補完してくれる
