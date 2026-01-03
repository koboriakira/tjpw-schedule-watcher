# TJPW Schedule Watcher

東京女子プロレス（TJPW）のスケジュール自動取得・カレンダー登録サービス

## 🚀 概要

東京女子プロレスの公式サイトから試合スケジュール情報を自動取得し、Google Calendar / Notion等の外部カレンダーサービスに自動登録することで、ファンが観戦予定を立てやすくするためのツールです。

### 主な機能

- ✅ **自動スケジュール取得**: TJPWの公式サイトから試合スケジュールを自動的に取得
- ✅ **外部API連携**: Google Calendar、Notion APIへの自動登録
- ✅ **柔軟な期間指定**: デフォルト90日間、開発モード7日間の取得期間
- ✅ **クリーンアーキテクチャ**: ドメイン駆動設計に基づいた保守性の高い実装

## 📋 必要要件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (推奨)
- Selenium (Docker コンテナまたはローカル実行)

## セットアップ

### 1. プロジェクトのセットアップ

```bash
# uvのインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトのセットアップ
uv sync
```

### 2. Seleniumの起動

#### Docker で起動する場合（推奨）

```bash
docker run -d --name chrome-for-tjpw \
  -p 4444:4444 \
  --shm-size="2g" \
  -e TZ=Asia/Tokyo \
  seleniarm/standalone-chromium:114.0
```

#### Docker Compose で起動する場合

```yaml
services:
  chrome:
    image: seleniarm/standalone-chromium:114.0
    ports:
      - 4444:4444
      - 7900:7900  # ブラウザ画面確認用（VNC）
    environment:
      - TZ=Asia/Tokyo
    shm_size: 2gb
```

```bash
docker compose up -d
```

### 3. 環境変数の設定

**重要:** `.env`ファイルを使用することを推奨します（サンプルは`.env.example`を参照）。

```bash
# Selenium接続先（必須）
export SELENIUM_DOMAIN=http://localhost:4444

# Google Calendar API（Lambda経由）※オプション
# 実際のURLは開発チーム内で共有されているものを使用してください
export LAMBDA_GOOGLE_CALENDAR_API_DOMAIN=https://your-lambda-url.lambda-url.ap-northeast-1.on.aws/

# Notion API ※オプション
# 実際のURLとシークレットは開発チーム内で共有されているものを使用してください
export LAMBDA_NOTION_API_DOMAIN=https://your-lambda-url.lambda-url.ap-northeast-1.on.aws/
export NOTION_SECRET=your_notion_secret_token
```

または、`.env`ファイルを作成：

```bash
# .envファイルを作成（.env.exampleをコピー）
cp .env.example .env
# .envファイルを編集して実際の値を設定
```

## 使い方

### 基本的な使用方法

```bash
# dry-runモードでテスト実行（外部APIに保存しない）
uv run tjpw-schedule-watcher update --dry-run

# 開発モードで実行（7日間のスケジュールのみ取得）
uv run tjpw-schedule-watcher update --dev --dry-run

# 本番実行（90日間のスケジュールを取得し、外部APIに保存）
# ※外部API（Google Calendar/Notion）の環境変数が設定されている必要があります
uv run tjpw-schedule-watcher update
```

### コマンドオプション

```bash
# ヘルプの表示
uv run tjpw-schedule-watcher --help
uv run tjpw-schedule-watcher update --help

# オプション:
#   --dev      開発モード（7日間のみ取得）
#   --dry-run  外部APIに保存しない（テスト用）
```

## プロジェクト構造

```
tjpw-schedule-watcher/
├── src/
│   └── tjpw_schedule_watcher/
│       ├── domain/              # ドメイン層（ビジネスロジック）
│       │   ├── models.py        # ドメインモデル
│       │   ├── value_objects.py # 値オブジェクト
│       │   └── interfaces.py    # インターフェース定義
│       ├── usecase/             # ユースケース層
│       │   └── scrape_tjpw.py   # スケジュール取得ユースケース
│       ├── infrastructure/      # インフラ層（技術的実装）
│       │   ├── scrapers.py      # Seleniumスクレイピング実装
│       │   ├── selenium_factory.py # Selenium接続管理
│       │   ├── external_apis.py # 外部API連携実装
│       │   └── constants.py     # 定数定義
│       ├── main.py              # CLIエントリーポイント
│       └── api.py               # FastAPI（将来の拡張用）
├── tests/                       # テストコード
├── SPEC.md                      # 要求定義書
└── pyproject.toml               # プロジェクト設定
```

## アーキテクチャ

クリーンアーキテクチャに基づいた3層構造：

```
CLI層 (main.py)
    ↓
UseCase層 (ScrapeTjpw)
    ↓
Domain層 (TournamentSchedule, Scraper, ScheduleExternalApi)
    ↓
Infrastructure層 (SeleniumScraper, ScheduleGoogleCalendarApi, ScheduleNotionApi)
```

## 開発コマンド

```bash
# テスト実行
uv run pytest

# テスト（詳細モード）
uv run pytest -v

# コードフォーマット
uv run ruff format .

# リンティング
uv run ruff check .

# 型チェック
uv run mypy
```

## 取得データ

### スクレイピング対象

- **対象サイト**: https://www.tjpw.jp/schedules
- **取得項目**:
  - 大会名
  - 開催日時（開場時刻/開始時刻）
  - 会場名
  - 座席種別
  - 備考
  - 詳細ページURL

### 外部API連携

#### Google Calendar API

```json
{
  "category": "東京女子",
  "title": "大会名",
  "start": "2026-01-15T13:00:00+09:00",
  "end": "2026-01-15T17:00:00+09:00",
  "detail": "URL\n\n会場\n\n座席種別\n\n備考"
}
```

#### Notion API

```json
{
  "url": "詳細ページURL",
  "title": "大会名",
  "date": "2026-01-15",
  "promotion": "東京女子プロレス",
  "tags": []
}
```

## 注意事項

- スクレイピングの間隔は3秒に設定されています（サーバー負荷を考慮）
- デフォルトでは90日間のスケジュールを取得します
- 外部APIへの登録には各サービスの認証情報が必要です
- Seleniumコンテナが起動していない場合はエラーになります

## トラブルシューティング

### Seleniumが起動しない

```bash
# Dockerコンテナの状態確認
docker ps

# コンテナが起動していない場合
docker start chrome-for-tjpw

# または再起動
docker rm chrome-for-tjpw
docker run -d --name chrome-for-tjpw \
  -p 4444:4444 \
  --shm-size="2g" \
  -e TZ=Asia/Tokyo \
  seleniarm/standalone-chromium:114.0
```

### 環境変数が設定されていない

```bash
# 現在の環境変数を確認
env | grep -E 'SELENIUM|LAMBDA|NOTION'

# 必要に応じて設定
export SELENIUM_DOMAIN=http://localhost:4444
```

## 今後の改善予定

- [ ] ユニットテストの拡充（カバレッジ向上）
- [ ] 選手誕生日の自動登録機能
- [ ] Playwright等の代替スクレイピング技術の検討
- [ ] エラーリトライ処理の実装
- [ ] 定期実行の自動化（cron、GitHub Actions等）
- [ ] 重複登録の防止機構

## ライセンス

MIT License

## 🚀 クイックスタート

ワンコマンドで新しいPythonプロジェクトを作成：

```bash
curl -fsSL https://raw.githubusercontent.com/koboriakira/tjpw-schedule-watcher/main/install.sh | sh -s my-new-project
```

作成後：

```bash
cd my-new-project
uv run pytest  # テスト実行
uv run my-new-project --help  # アプリケーション確認
```

## 📋 テンプレートとして使用

手動でテンプレートを使用する場合：

```bash
# このリポジトリをクローン
git clone https://github.com/koboriakira/tjpw-schedule-watcher.git
cd tjpw-schedule-watcher

# 新しいプロジェクトを作成
./install.sh my-new-project

# 作成されたプロジェクトに移動
cd my-new-project

# 開発開始！
uv run pytest  # テスト実行
uv run my-new-project --help  # アプリケーション確認
```

### install.shの機能

- ✅ **自動ダウンロード**: GitHubから最新のテンプレートを取得
- ✅ **完全なファイルコピー**: すべてのテンプレートファイルを新しいディレクトリにコピー
- ✅ **名前の一括置換**: プロジェクト名・パッケージ名を適切に変換
- ✅ **Git初期化**: 新しいGitリポジトリの初期化と初回コミット
- ✅ **環境セットアップ**: uv syncによる依存関係のインストール
- ✅ **エラーハンドリング**: 無効な名前や既存ディレクトリの検証

## 特徴

- 🚀 **超高速**: uvによる爆速パッケージ管理
- 🛠️ **最新ツール**: ruff、mypy、pytest、Claude Code hooks、pre-commit
- 📦 **モダンな構成**: pyproject.tomlによる一元管理
- 🧪 **完全なテスト**: カバレッジ測定とCI/CD
- 🔧 **開発者体験**: リンター、フォーマッター、型チェック
- 🚀 **自動リリース**: release-pleaseによるセマンティックバージョニング

## 必要要件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (推奨)

## セットアップ

### uvを使用（推奨）

```bash
# uvのインストール（まだの場合）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトのセットアップ
uv sync

# 品質管理ツールのセットアップ
uv run pre-commit install              # Git hooks（手動開発時）
# Claude Code hooks（AI統合）は .claude/settings.local.json で設定済み
```

### 従来の方法

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## 開発コマンド

```bash
# テスト実行
uv run pytest

# テスト（カバレッジ付き）
uv run pytest --cov

# コードフォーマット
uv run ruff format .

# リンティング
uv run ruff check .

# 型チェック
uv run mypy

# 品質チェック実行
.claude/scripts/pre-commit-replacement.sh   # Claude Code hooks（推奨）
uv run pre-commit run --all-files           # 従来のpre-commit

# アプリケーション実行
uv run tjpw-schedule-watcher hello --name "開発者"
```

## FastAPI Web API

FastAPIによるモダンなWeb APIも実装されています：

```bash
# 開発サーバー起動（開発モード）
ENVIRONMENT=development uv run uvicorn tjpw_schedule_watcher.api:app --reload

# または環境変数をエクスポート
export ENVIRONMENT=development
uv run uvicorn tjpw_schedule_watcher.api:app --reload

# 本番モード（セキュアな設定）
ENVIRONMENT=production ALLOWED_ORIGINS=https://yourdomain.com uv run uvicorn tjpw_schedule_watcher.api:app

# APIドキュメントにアクセス（開発モードのみ）
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)

# APIテスト実行
uv run pytest tests/test_api.py
```

### 環境変数

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `ENVIRONMENT` | `production` | 環境設定（`development`, `dev`, `local`, `production`） |
| `DEBUG` | `false` | デバッグモード（`true`, `1`, `yes`で有効） |
| `ALLOWED_ORIGINS` | なし | 許可するオリジン（カンマ区切り、例：`https://example.com,https://app.example.com`） |

**開発モードの動作:**
- すべてのオリジンからのCORS許可
- API ドキュメント（/docs, /redoc）有効
- より詳細なログ出力

**本番モードの動作:**
- 指定されたオリジンのみCORS許可
- API ドキュメント無効化
- セキュアな設定

## プロジェクト構造

```
tjpw-schedule-watcher/
├── src/
│   └── tjpw_schedule_watcher/
│       ├── __init__.py
│       ├── main.py          # CLIエントリーポイント
│       ├── api.py           # FastAPI アプリケーション
│       ├── utils.py
│       └── routers/         # FastAPI ルーター
│           ├── __init__.py
│           └── hello.py
├── tests/
│   ├── test_main.py
│   ├── test_api.py          # API テスト
│   └── test_utils.py
├── pyproject.toml
├── README.md
└── .pre-commit-config.yaml
```

## 設定ファイル

すべての設定は `pyproject.toml` に統一されています：

- **ruff**: リンティングとフォーマット
- **pytest**: テストの実行と設定
- **mypy**: 型チェック
- **coverage**: カバレッジ測定

## デプロイ

### Render（FastAPI Web Service）

[Render](https://render.com)を使用したFastAPIアプリケーションのデプロイが可能です：

#### デプロイ設定

1. Render Dashboardで"New Web Service"を作成
2. GitHubリポジトリを接続
3. 以下の設定を使用：

| 項目 | 設定値 |
|------|--------|
| **Root Directory** | （指定なし） |
| **Build Command** | `uv sync --frozen && uv cache prune --ci` |
| **Start Command** | `uvicorn src.tjpw_schedule_watcher.api:app --host 0.0.0.0 --port $PORT` |
| **Language** | Python 3 |

4. 環境変数を設定（Render Dashboard）：
   - `ENVIRONMENT`: `production`
   - `ALLOWED_ORIGINS`: `https://yourdomain.com`（実際のドメインに置き換え）
ヘルスチェック**: `https://your-app.onrender.com/health`
- **API ドキュメント**: 本番環境では無効化（セキュリティのため）

#### 注意事項

- 本番環境では環境変数`ALLOWED_ORIGINS`を必ず設定してください
- 開発環境では`ENVIRONMENT=development`を設定するとセキュリティ制限が緩和されます

#### 注意事項

- 本番環境では[api.py](src/tjpw_schedule_watcher/api.py)のCORS設定を適切に制限してください
- 環境変数はRender DashboardまたはBlueprint（render.yaml）で管理可能

## CI/CD

GitHub Actionsによる自動化：

- マルチプラットフォーム（Linux、Windows、macOS）
- 複数Python バージョン（3.12、3.13）
- テスト、リンティング、型チェック
- セキュリティ監査

## 自動リリース管理

[release-please](https://github.com/googleapis/release-please)による自動リリース：

### Conventional Commits使用例

```bash
# パッチバージョン更新 (0.1.0 → 0.1.1)
git commit -m "fix: バリデーションエラーを修正"

# マイナーバージョン更新 (0.1.0 → 0.2.0)
git commit -m "feat: 新しい機能を追加"

# メジャーバージョン更新 (0.1.0 → 1.0.0)
git commit -m "feat!: 破壊的変更を実装"
```

### 自動化される処理

- **バージョン更新**: Conventional Commitsに基づいてセマンティックバージョニング
- **CHANGELOG生成**: コミットメッセージから自動的にCHANGELOGを更新
- **GitHub Releases**: 新しいバージョンのリリースを自動作成
- **PyPI公開**: 本番環境とテスト環境への自動パッケージ公開

## ライセンス

MIT License
