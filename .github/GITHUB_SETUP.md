# GitHub Repository Setup Guide

release-pleaseとGitHub Actionsが正常に動作するために、以下の設定を行ってください。

## ✅ 必要な設定

### 1. GitHub Actions権限設定

**Repository Settings > Actions > General**で以下を有効にしてください：

- ✅ **Allow GitHub Actions to create and approve pull requests**
- ✅ **Read and write permissions** for GITHUB_TOKEN
- ✅ **Allow actions and reusable workflows**

### 2. Branch Protection Rules

**Repository Settings > Branches**で`main`ブランチに以下を設定：

- ✅ **Require pull request reviews before merging**
- ✅ **Require status checks to pass before merging**
  - ✅ CI workflow checks
- ✅ **Require branches to be up to date before merging**

### 3. Environment設定（PyPI公開用）

**Repository Settings > Environments**で以下の環境を作成：

#### `production`環境（PyPI本番）
- **Environment protection rules**:
  - ✅ Required reviewers（推奨）
  - ✅ Wait timer: 0 minutes
- **Environment secrets**:
  - PyPI API tokenが必要な場合に設定

#### `test`環境（TestPyPI）
- **Environment protection rules**:
  - ✅ Required reviewers（推奨）
  - ✅ Wait timer: 0 minutes
- **Environment secrets**:
  - TestPyPI API tokenが必要な場合に設定

### 4. Codecov設定（カバレッジレポート用）

**Repository Settings > Secrets and variables > Actions**で以下のシークレットを設定：

#### `CODECOV_TOKEN`
1. **Codecov.io**（https://codecov.io）でGitHubアカウントログイン
2. リポジトリ追加：「Add new repository」→ `tjpw-schedule-watcher`選択
3. **Repository Settings**→「General」タブ
4. **Repository Upload Token**をコピー
5. GitHub**Repository Settings**→「Secrets and variables」→「Actions」
6. **New repository secret**クリック
   - **Name**: `CODECOV_TOKEN`
   - **Secret**: コピーしたトークンを貼り付け

### 5. Trusted Publishing（推奨）

PyPI/TestPyPIでTrusted Publishingを設定：

1. **PyPI**: https://pypi.org/manage/account/publishing/
2. **TestPyPI**: https://test.pypi.org/manage/account/publishing/

設定項目：
- **Owner**: GitHubユーザー名
- **Repository name**: `tjpw-schedule-watcher`
- **Workflow name**: `release-please.yml`
- **Environment name**: `production` (PyPI) / `test` (TestPyPI)

## 🚀 動作確認

1. **テストコミット**をmainブランチにpush
2. **GitHub Actions**タブで実行結果を確認
3. **Release Please PR**が自動作成されることを確認

## ⚠️ トラブルシューティング

### エラー: "GitHub Actions is not permitted to create or approve pull requests"

**解決方法**:
1. Repository Settings > Actions > General
2. **Workflow permissions**セクション
3. **Allow GitHub Actions to create and approve pull requests**にチェック

### エラー: "Resource not accessible by integration"

**解決方法**:
1. GITHUB_TOKENの権限不足
2. Repository Settings > Actions > General
3. **Workflow permissions**で**Read and write permissions**を選択

### Codecovエラー: "Token required - not valid tokenless upload"

**解決方法**:
1. `CODECOV_TOKEN`が正しく設定されているか確認
2. Codecov.ioでリポジトリが追加されているか確認
3. トークンが有効期限切れでないか確認
4. Codecovサービス障害の場合は復旧を待つ

### PyPI公開エラー

**解決方法**:
1. Trusted Publishingが正しく設定されているか確認
2. Environment名が一致しているか確認
3. PyPI/TestPyPIでプロジェクト名が利用可能か確認

## 📖 参考資料

- [GitHub Actions Permissions](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token)
- [Release Please Documentation](https://github.com/googleapis/release-please)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
