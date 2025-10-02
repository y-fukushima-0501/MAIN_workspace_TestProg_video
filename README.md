# Video Stutter Detector（動画カクつき検出器）

このプロジェクトは、Python を使用して動画再生時のカクつきを検出することを目的としています。動画のパフォーマンスを解析し、カクつきに関連する問題を特定するための包括的なツールセットを提供します。

## プロジェクト構成

- **.gitignore**: Gitで追跡しないファイルやディレクトリを指定します。
- **.vscode/settings.json**: Visual Studio Code のプロジェクト設定を含みます。
- **notebooks/01_test.ipynb**: 動画カクつき検出に関する実験や解析用のJupyterノートブック。
- **src/detector/**: 動画カクつき検出のコア機能を含むディレクトリ。
  - **__init__.py**: detector パッケージの初期化。
  - **main.py**: アプリケーションのエントリーポイント。動画カクつき検出プロセスを開始。
  - **processor.py**: 動画データの処理用関数やクラスを定義。
  - **analyzer.py**: 動画カクつき解析のロジックを含む。
  - **utils.py**: 補助関数やユーティリティを提供。
  - **cli.py**: コマンドラインからプログラムを実行するためのインターフェース。
- **src/tests/**: detector モジュールの単体テスト。
  - **test_processor.py**: processor.py の単体テスト。
  - **test_analyzer.py**: analyzer.py の単体テスト。
- **tests/integration_test.py**: 統合テストを実行するスクリプト。
- **scripts/run_detection.sh**: 動画カクつき検出プロセスを実行するシェルスクリプト。
- **requirements.txt**: プロジェクトで必要なPythonパッケージを列挙。
- **pyproject.toml**: プロジェクトのメタデータと依存関係を管理。
- **setup.cfg**: プロジェクト設定とオプションを含む。

## インストール

必要なパッケージをインストールするには、以下を実行します：

```
pip install -r requirements.txt
```

## 使い方

動画カクつき検出プロセスを実行するには、`cli.py` のコマンドラインインターフェースを使用するか、シェルスクリプト `run_detection.sh` を実行します。

## コントリビューション

貢献は歓迎します！改善やバグ修正のためのプルリクエストの提出、または issue の作成をお願いします。

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は LICENSE ファイルを参照してください。