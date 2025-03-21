# Lightning Network 手数料マネージャー

このプロジェクトは、SQLiteデータベースに保存された履歴データを使用して、Lightning Networkのチャネル手数料を管理・計算することを目的としています。アプリケーションはチャネルデータを取得し、分析して、事前に定義された設定や条件に基づいて手数料を調整します。

## プロジェクト構造

```
ln_fee_manager
├── src
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db
│   │   ├── __init__.py
│   │   └── database.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── channel.py
│   │   └── channel_data.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── fee_calculator.py
│   │   └── data_analyzer.py
│   └── utils
│       ├── __init__.py
│       └── helpers.py
├── data
│   ├── fixed_channel_list.csv
│   └── control_channel_list.csv
├── pyproject.toml
└── README.md
```

## インストール

1. リポジトリをクローンします：
   ```
   git clone <リポジトリURL>
   cd ln_fee_manager
   ```

2. Poetryを使用して依存関係をインストールします：
   ```
   poetry install
   ```

   Poetryがインストールされていない場合は、先に以下のコマンドでインストールしてください：

   ```
   pip install poetry
   ```

## 設定

アプリケーションは設定ファイル（src/config.py）を使用して、以下のようなさまざまなパラメータを設定します：

- `fixed_channel_list：固定手数料を持つチャネルを含むCSVファイル
- `control_channel_list：制御対象チャネルを含むCSVファイル
- `inboundFee_base：インバウンドチャネルの基本手数料
- `inboundFee_ratio：ローカル残高に基づいてインバウンド手数料を調整する比率
- `data_period：分析に使用する最新のデータポイント数
- `fee_decreasing_threshold：手数料を徐々に下げるためのしきい値

## 使用方法

Poetryを使用してアプリケーションを実行するには、次のコマンドを実行します：
```
poetry run python src/main.py
```

これにより、データベース接続の初期化、設定のロード、手数料計算プロセスが開始されます。

## コマンドラインオプション

- `--initial：初期設定モードで実行します（新しいチャネルに対して手数料を設定）
```
poetry run python src/main.py --initial
```

- `--channel_download：すべてのチャネル情報をCSVファイルにダウンロードします
```
poetry run python src/main.py --channel_download
```

## データファイル  

- `fixed_channel_list.csv：固定手数料を設定するチャネルのリスト（channel_name, channel_id, fee）
- `control_channel_list.csv：定期的に手数料を見直すチャネルのリスト

## ライセンス

このプロジェクトはMITライセンスのもとで提供されています。詳細についてはLICENSEファイルをご覧ください。