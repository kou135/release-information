# release-information

🌐 [English](./README.md) | **日本語** | [한국어](./README.ko.md) | [हिन्दी](./README.hi.md)

[![CI](https://github.com/kou135/release-information/actions/workflows/ci.yml/badge.svg)](https://github.com/kou135/release-information/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

リリースノートや設計仕様向けの、git pre-commit 駆動の Markdown → 単一 HTML ファイルレンダラー。
`docs/release-information/` 配下に Markdown ファイルを置いて commit するだけで、
**Tokyo Night** ダークテーマ（デフォルト）・インライン CSS・目次の自動生成・外部依存ゼロの
自己完結型 HTML ドキュメントが再生成され、同じ commit にステージングされます。
Midnight Museum をはじめ、他の全テーマも `--theme` で引き続き選択可能です。

## なぜこの OSS なのか (`python-markdown` 直接 / MkDocs / Quarto / Pandoc ではなく)

素の `python-markdown` でも HTML は得られますが、チームメンバーや Claude に手渡したい *種類* の
HTML にはなりません。MkDocs・Quarto・Pandoc はいずれも優れたツールですが、それぞれサイト全体・
テーマ付きの複数ページ成果物・Lua 拡張可能なツールチェーンを提供するものです。`release-information`
は意図的に範囲を絞っています:

- **仕様書グレードのダークテーマを、リポジトリ間でコピーするスニペットではなくパッケージとして提供。**
  Anthropic スタイルの *Midnight Museum* CSS (ダークな `#0F172A` の地、serif の本文、sans の見出し、
  Pygments monokai のコード、`[TOC]` 自動挿入) はコンバーター本体と *一緒に* 出荷されるため、
  インストール済みの全リポジトリで見た目の同一性が保たれます。`style.css` のクローンが
  あちこちで分岐することもありません。
- **`docs/release-information/` 規約を pre-commit hook で強制。** `release-information install` コマンドは
  単一のシェル hook を書き込み、その 1 つの glob に *マッチする* ステージ済み Markdown のみを
  再レンダリングし、生成された HTML を同じ commit に `git add` します。サイトディレクトリも、
  `mkdocs build` も、CI ステップも不要です。成果物はソースと同じ commit に並んで存在します。
- **単一 HTML 出力、インライン CSS、CDN ゼロ — Claude のコンテキストウィンドウに貼り付け可能。**
  各 `.html` は 1 ファイルです。`_site/` も、アセットディレクトリも、外部フォントへの
  `<link rel>` もありません。ドキュメント全体が密で自己完結しており、スタイルを失うことなく
  AI エージェントや Slack へコピー & ペーストできます。これが既存ツールが残しているギャップです。
  既存ツールが *公開* に最適化されているのに対し、この OSS は *密なコンテキストを (人間または
  モデルの) 読み手に手渡すこと* に最適化されています。

「Markdown を HTML に」だけが必要なら `python-markdown` を直接使ってください。
ドキュメントサイトが欲しければ MkDocs か Quarto を使ってください。**すべての** プロジェクトで
**同じ** ダークで密な単一ファイルのリリースノート HTML を、何も考えずに毎 commit で生成したいときに
`release-information` を選んでください。

## インストール

現状は GitHub から直接インストールします。プロジェクトの venv を汚さずに CLI をグローバルで
使えるよう、`pipx` を推奨します。

```bash
pipx install git+https://github.com/kou135/release-information.git
# あるいは: pip install git+https://github.com/kou135/release-information.git
```

`release-information` は Python 3.10+ が必要です。macOS と Linux に対応しており、Windows は
ロードマップ入りしています (バンドルされている pre-commit hook は POSIX shell スクリプトです)。

> **PyPI**: publish workflow は配線済み (`.github/workflows/publish.yml`) ですが、まだ
> トリガーされていません。fork して自分のコピーを公開したい場合は
> [`docs/PUBLISHING.ja.md`](./docs/PUBLISHING.ja.md) を参照してください。

## クイックスタート

ゼロからレンダリング済み HTML リリースノートまでの 5 分パス:

```bash
# 1. CLI をグローバルにインストール
pipx install git+https://github.com/kou135/release-information.git

# 2. HTML リリースノートを置きたいリポジトリへ移動
cd ~/workspace/your-project

# 3. pre-commit hook を <repo>/.git/hooks/pre-commit にインストール
#    (docs/release-information/ が無ければ同時に作成される — 下の "install" 節参照)
release-information install
#   - 既存の pre-commit hook がある? まず: release-information install --force でバックアップ
#   - .git が無い? 明示的にエラーが出るだけで、何も書かれない。

# 4. リリースノートを追加 (上の install がディレクトリを作っているので mkdir は不要)
cat > docs/release-information/v1.0.0.md <<'EOF'
# v1.0.0

## Highlights
- First public release.

## Breaking changes
- None.
EOF

# 5. commit する。hook が docs/release-information/v1.0.0.html をレンダリングし、
#    同じ commit の一部として自動でステージングする。
git add docs/release-information/v1.0.0.md
git commit -m "docs: add v1.0.0 release notes"

# 6. 確認
ls docs/release-information/
# v1.0.0.md  v1.0.0.html   <- 一緒に生成され commit される
```

## 使い方

```text
release-information [--version]
release-information --help
release-information render <FILE.md>
release-information render-all [--root .]
release-information install [--repo-root PATH] [--force]
release-information uninstall [--repo-root PATH]
release-information delete --file <NAME> [--repo-root PATH]
release-information version
```

### `render` — 単一ファイル

```bash
release-information render docs/release-information/v1.0.0.md
# docs/release-information/v1.0.0.html を書き出す (同じ stem、同じディレクトリ)
# 出力ファイルの絶対パスを stdout に表示する
```

### `render-all` — 一括再レンダリング

```bash
release-information render-all                # CWD を --root として使用
release-information render-all --root ./repo  # --root を明示

# docs/release-information/**/*.md (再帰) を glob し、それぞれを再レンダリングする。
# マッチ 0 件はエラーではない: exit code 0。
```

### `install` / `uninstall` — pre-commit hook の管理

```bash
release-information install                   # <repo>/.git/hooks/pre-commit を書き込む
release-information install --force           # 既存 hook を上書き (バックアップ済み)
release-information uninstall                 # バックアップを復元、または自前 hook を削除
```

副作用: `install` は `<repo>/docs/release-information/` も作成します
(`mkdir -p`、冪等)。これまで Quick start で手順として案内していた
`mkdir -p docs/release-information` は不要になりました。

hook は `docs/release-information/**/*.md` にマッチするステージ済みファイルにのみ作用します。
それ以外の Markdown ファイル (`README.md`、`docs/blog/*.md` 等) の編集は完全に無視され、
hook は exit 0 で短絡します。

### `delete` — 仕様書とその HTML を削除

```bash
release-information delete --file v1.0.0
# docs/release-information/v1.0.0.md と docs/release-information/v1.0.0.html を削除する
# `--file` 引数は `v1.0.0` でも `v1.0.0.md` でも受け付ける (拡張子は内部で除去)
```

`.md` と `.html` を 1 コマンドで両方削除します。ペアの片方しか存在しない
場合は、存在する方だけが削除されます。パストラバーサル (`..`、`/`、絶対
パス) と `docs/release-information/` 配下のシンボリックリンクは exit code 2
で拒否されます。どちらのファイルも存在しない場合は、exit code 2 で
stderr に `no such file` メッセージが出力されます。

## 設計思想

### なぜ仕様書を HTML で?

Anthropic チームと、2026 年の何人かのライター (Lenny's Newsletter、Simon Willison、ChatPRD の
Thariq Shihipar) は独立に同じ知見に至りました: HTML は、AI エージェントへコンテキストを手渡す
フォーマットとして Markdown よりも情報密度が高い、というものです。タイポグラフィ・色・目次・
シンタックスハイライト済みコード・インラインデータを 1 つのファイルに重ねて、モデルが
前処理なしで解釈できます。`release-information` はこの観察の上に構築されています。

### なぜ「Midnight Museum」?

デフォルトテーマはパレットとタイポグラフィを著者の `minima` ワークスペース仕様レンダラーから
継承しています: ダークな `#0F172A` の地、serif 本文 (macOS では Hiragino Mincho、Noto Serif JP に
フォールバック)、sans-serif の見出し、コードには Pygments *monokai*。美学はドキュメントサイトと
いうよりギャラリーの壁掛けカードに近い — どうでもいい所はコントラストが低く穏やかで、
大事な所はコントラストが高い、密で静かな構成です。テーマは `core/theme.py` の単一インライン
`<style>` ブロックとして出荷され、render 時にも閲覧時にも外部フォント CDN にアクセスしません。

### なぜサイトではなく単一 HTML 出力?

リリースノートは 1 度読まれ、永遠にアーカイブされ、ときどき AI のコンテキストウィンドウに
貼られます。これらのワークフローのどれも `_site/` ディレクトリを欲しがりません。
`.md` ごとに 1 ファイルなら、出力は `cat` 可能・メール添付可能・GitHub の 1 つの diff で
レビュー可能です。

### 参考文献

- Lenny Rachitsky — *HTML is the new Markdown* (Lenny's Newsletter, 2026)
- Simon Willison — *The Unreasonable Effectiveness of HTML* (2026-05-08)
- Thariq Shihipar — ChatPRD のインタビュー (*How I AI*, "Claude Code at Anthropic")

## 貢献方法

```bash
git clone https://github.com/kou135/release-information.git
cd release-information
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

Issue と PR を歓迎します。このプロジェクトは **レンダリング HTML 出力の安定性** に最適化
されています (インライン CSS は public な契約であり、変更すると下流のすべてのリポジトリが
再レンダリングを強制されます)。挙動変更には `CHANGELOG.md` の *Changed* または *Breaking*
セクションへのエントリが必要です。

## リリース

メンテナ向け: PyPI リリースワークフロー (タグ駆動、OIDC による Trusted Publishing — API
トークン不要) については [`docs/PUBLISHING.ja.md`](./docs/PUBLISHING.ja.md) を参照してください。

## ロードマップ (v0.1.0 のスコープ外)

- `pre-commit` フレームワーク (`.pre-commit-hooks.yaml`) によるバンドル hook との並列統合
- CLI フラグによる複数テーマ切替
- フロントマター駆動のリリースノート構造 (`version`, `date`, `breaking` キー)
- npm 配布 / Husky ブリッジ
- Windows pre-commit hook (PowerShell)

## ライセンス

[MIT](./LICENSE)
