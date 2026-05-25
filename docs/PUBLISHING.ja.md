# PyPI への公開

このプロジェクトは **GitHub Actions + Trusted Publishing (OIDC)** 経由で PyPI に公開します。
長期保持の API トークンを repo の secret に保存することはありません。

## 初回セットアップ (一度だけ、手動)

これらの手順は最初のリリース前にリポジトリオーナーが実施する必要があります。

### 1. PyPI アカウントを作成

https://pypi.org/account/register/

2FA を有効化してください (公開に必須)。

### 2. プロジェクト名を予約

`release-information` は PyPI に未登録のため、**pending publisher** を使用します:

1. https://pypi.org/manage/account/publishing/ にアクセス
2. "Add a new pending publisher" フォームに以下を入力:
   - **PyPI Project Name**: `release-information`
   - **Owner**: `kou135`
   - **Repository name**: `release-information`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
3. Submit。

### 3. GitHub Environment を作成

1. https://github.com/kou135/release-information/settings/environments にアクセス
2. **New environment** をクリックし、`pypi` という名前を付ける。
3. (任意) `Required reviewers` に自分を追加すると、公開のたびに手動承認が必要になります。
4. Save。

## 新しいバージョンをリリースする

```bash
# 1. pyproject.toml のバージョンを bump (例: 0.1.0 -> 0.1.1)
# 2. CHANGELOG.md を更新
# 3. commit して push
git commit -am "release: v0.1.1"
git push

# 4. タグを打って push (これで publish workflow がトリガーされる)
git tag v0.1.1
git push --tags
```

`Publish to PyPI` workflow は以下を実行します:
1. `sdist` と `wheel` をビルド。
2. (required reviewers を設定していれば) Environment の承認を待つ。
3. OIDC 経由で PyPI にアップロード — トークン不要。

成功すると、パッケージは https://pypi.org/project/release-information/ で公開され、
`pip install release-information` でインストール可能になります。

## 初回公開成功後

"pending publisher" は自動的に通常の publisher に昇格します。
以降のリリースは新しいタグを打つだけ — PyPI ダッシュボードの変更は不要です。

## ロールバック

PyPI は同じバージョンの再アップロードを **許可しません**。何か壊れている場合は、
PyPI 上でリリースを yank し、新しいパッチバージョンを公開します:

```bash
# Web UI で yank: https://pypi.org/manage/project/release-information/releases/
# その後:
# pyproject.toml と CHANGELOG を 0.1.2 に bump し、commit、タグ、push。
```
