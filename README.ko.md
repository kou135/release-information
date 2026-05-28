# release-information

🌐 [English](./README.md) | [日本語](./README.ja.md) | **한국어** | [हिन्दी](./README.hi.md)

[![CI](https://github.com/kou135/release-information/actions/workflows/ci.yml/badge.svg)](https://github.com/kou135/release-information/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

릴리스 노트와 설계 사양을 위한, git pre-commit 기반의 Markdown → 단일 HTML 파일 렌더러입니다.
`docs/release-information/` 아래에 Markdown 파일을 두고 commit 하기만 하면, Anthropic 스타일의
**Midnight Museum** 다크 테마 · 인라인 CSS · 자동 목차 · 외부 의존성 0 의 자기 완결형 HTML 문서가
다시 생성되어 같은 commit 에 스테이징됩니다.

## 왜 이 OSS 인가 (`python-markdown` 직접 / MkDocs / Quarto / Pandoc 이 아니라)

순수한 `python-markdown` 으로도 HTML 은 얻을 수 있지만, 팀 동료나 Claude 에게 건네고 싶은 *종류* 의
HTML 은 아닙니다. MkDocs · Quarto · Pandoc 은 모두 훌륭한 도구이지만, 각각 사이트 전체 · 테마가 적용된
다중 페이지 산출물 · Lua 로 확장 가능한 툴체인을 제공합니다. `release-information` 은 의도적으로
범위를 좁혔습니다.

- **사양서 수준의 다크 테마를 리포지토리 사이에서 복사하는 스니펫이 아니라 패키지로 제공합니다.**
  Anthropic 스타일의 *Midnight Museum* CSS (어두운 `#0F172A` 배경, serif 본문, sans 제목,
  Pygments monokai 코드, `[TOC]` 자동 삽입) 는 컨버터 본체와 *함께* 출하되므로, 설치된 모든
  리포지토리에서 시각적 일관성이 유지됩니다. `style.css` 의 복제본이 여기저기에서 분기될 일이
  없습니다.
- **`docs/release-information/` 규약을 pre-commit hook 으로 강제합니다.** `release-information install`
  명령은 단일 shell hook 을 기록하고, 그 하나의 glob 에 *일치하는* 스테이지된 Markdown 만
  다시 렌더링하여 생성된 HTML 을 같은 commit 에 `git add` 합니다. 사이트 디렉터리도, `mkdocs build` 도,
  CI 단계도 필요 없습니다. 산출물은 소스와 같은 commit 안에 나란히 존재합니다.
- **단일 HTML 출력, 인라인 CSS, CDN 0 — Claude 의 context window 에 붙여넣기 가능.**
  각 `.html` 은 한 개의 파일입니다. `_site/` 도, 자산 디렉터리도, 외부 폰트로 향하는 `<link rel>` 도
  없습니다. 문서 전체가 밀도 있게 자기 완결되어 있어 스타일을 잃지 않고 AI 에이전트나 Slack 에
  복사 & 붙여넣기 할 수 있습니다. 이것이 기존 도구들이 남겨 둔 빈틈입니다. 기존 도구가 *공개* 에
  최적화되어 있다면, 이 OSS 는 *밀도 높은 컨텍스트를 (사람이든 모델이든) 독자에게 건네는 것* 에
  최적화되어 있습니다.

"Markdown 을 HTML 로" 만 필요하다면 `python-markdown` 을 직접 사용하시기 바랍니다.
문서 사이트가 필요하다면 MkDocs 나 Quarto 를 사용하시기 바랍니다. **모든** 프로젝트에서
**같은** 어두우면서 밀도 높은 단일 파일 릴리스 노트 HTML 을, 아무 생각 없이 매 commit 마다
생성하고 싶을 때 `release-information` 을 선택해 주십시오.

## 설치

현재는 GitHub 에서 직접 설치합니다. 프로젝트의 venv 를 더럽히지 않고 CLI 를 전역에서 사용할 수 있도록
`pipx` 사용을 권장합니다.

```bash
pipx install git+https://github.com/kou135/release-information.git
# 또는: pip install git+https://github.com/kou135/release-information.git
```

`release-information` 은 Python 3.10+ 이 필요합니다. macOS 와 Linux 를 지원하며, Windows 는
로드맵에 포함되어 있습니다 (번들된 pre-commit hook 은 POSIX shell 스크립트입니다).

> **PyPI**: publish workflow 는 이미 연결되어 있지만 (`.github/workflows/publish.yml`) 아직
> 트리거된 적은 없습니다. fork 해서 자신의 사본을 공개하고 싶다면
> [`docs/PUBLISHING.ko.md`](./docs/PUBLISHING.ko.md) 를 참조하십시오.

## 빠른 시작

0 에서 렌더링된 HTML 릴리스 노트까지 5 분 경로:

```bash
# 1. CLI 를 전역으로 설치
pipx install git+https://github.com/kou135/release-information.git

# 2. HTML 릴리스 노트를 두고 싶은 리포지토리로 이동
cd ~/workspace/your-project

# 3. pre-commit hook 을 <repo>/.git/hooks/pre-commit 에 설치
#    (docs/release-information/ 가 없으면 함께 생성됩니다 — 아래 "install" 절 참고)
release-information install
#   - 기존 pre-commit hook 이 있나요? 먼저: release-information install --force 로 백업
#   - .git 이 없나요? 명시적인 에러만 표시되고 아무것도 기록되지 않습니다.

# 4. 릴리스 노트를 추가 (위의 install 이 디렉터리를 만들었으므로 mkdir 은 필요 없음)
cat > docs/release-information/v1.0.0.md <<'EOF'
# v1.0.0

## Highlights
- First public release.

## Breaking changes
- None.
EOF

# 5. commit. hook 이 docs/release-information/v1.0.0.html 을 렌더링하고
#    같은 commit 의 일부로 자동 스테이징합니다.
git add docs/release-information/v1.0.0.md
git commit -m "docs: add v1.0.0 release notes"

# 6. 확인
ls docs/release-information/
# v1.0.0.md  v1.0.0.html   <- 함께 생성되어 commit 됩니다
```

## 사용법

```text
release-information [--version]
release-information --help
release-information render <FILE.md>
release-information render-all [--root .]
release-information install [--repo-root PATH] [--force]
release-information uninstall [--repo-root PATH]
release-information version
```

### `render` — 단일 파일

```bash
release-information render docs/release-information/v1.0.0.md
# docs/release-information/v1.0.0.html 을 출력합니다 (같은 stem, 같은 디렉터리)
# 출력 파일의 절대 경로를 stdout 에 표시합니다
```

### `render-all` — 일괄 재렌더링

```bash
release-information render-all                # CWD 를 --root 로 사용
release-information render-all --root ./repo  # --root 를 명시

# docs/release-information/**/*.md (재귀) 를 glob 하여 각각 재렌더링합니다.
# 일치 0 건은 에러가 아닙니다: exit code 0.
```

### `install` / `uninstall` — pre-commit hook 관리

```bash
release-information install                   # <repo>/.git/hooks/pre-commit 을 기록
release-information install --force           # 기존 hook 을 덮어쓰기 (백업 후)
release-information uninstall                 # 백업을 복원하거나 자체 hook 을 제거
```

부수 효과: `install` 은 `<repo>/docs/release-information/` 도 생성합니다
(`mkdir -p`, 멱등). 기존에 Quick start 에서 안내하던
`mkdir -p docs/release-information` 단계는 더 이상 필요하지 않습니다.

hook 은 `docs/release-information/**/*.md` 에 일치하는 스테이지된 파일에만 작용합니다.
그 외의 Markdown 파일 (`README.md`, `docs/blog/*.md` 등) 의 편집은 완전히 무시되며,
hook 은 exit 0 으로 단락됩니다.

## 설계 철학

### 왜 사양서를 HTML 로?

Anthropic 팀과 2026 년의 몇몇 저자 (Lenny's Newsletter, Simon Willison, ChatPRD 의 Thariq
Shihipar) 는 독립적으로 같은 결론에 도달했습니다. HTML 은 AI 에이전트에게 컨텍스트를 건네는
포맷으로서 Markdown 보다 정보 밀도가 높다는 것입니다. 타이포그래피 · 색상 · 목차 ·
syntax highlight 된 코드 · 인라인 데이터를 하나의 파일에 겹쳐서, 모델이 사전 처리 없이 해석할 수
있습니다. `release-information` 은 이 관찰을 토대로 만들어졌습니다.

### 왜 "Midnight Museum"?

기본 테마는 팔레트와 타이포그래피를 저자의 `minima` 워크스페이스 사양 렌더러에서 계승했습니다.
어두운 `#0F172A` 배경, serif 본문 (macOS 에서는 Hiragino Mincho, Noto Serif JP fallback),
sans-serif 제목, 코드에는 Pygments *monokai* 입니다. 미학은 문서 사이트라기보다 갤러리의
벽걸이 카드에 가깝습니다 — 중요하지 않은 곳은 콘트라스트가 낮고 차분하며, 중요한 곳은
콘트라스트가 높은, 밀도 있고 조용한 구성입니다. 테마는 `core/theme.py` 의 단일 인라인
`<style>` 블록으로 출하되며, render 시점에도 열람 시점에도 외부 폰트 CDN 에 접근하지 않습니다.

### 왜 사이트가 아닌 단일 HTML 출력?

릴리스 노트는 한 번 읽히고, 영원히 아카이브되며, 가끔 AI 의 context window 에 붙여집니다.
이 워크플로 어느 것도 `_site/` 디렉터리를 원하지 않습니다. `.md` 하나당 1 파일이면 출력은
`cat` 으로 출력 가능 · 메일 첨부 가능 · GitHub 의 단일 diff 에서 리뷰 가능합니다.

### 참고 문헌

- Lenny Rachitsky — *HTML is the new Markdown* (Lenny's Newsletter, 2026)
- Simon Willison — *The Unreasonable Effectiveness of HTML* (2026-05-08)
- Thariq Shihipar — ChatPRD 인터뷰 (*How I AI*, "Claude Code at Anthropic")

## 기여 방법

```bash
git clone https://github.com/kou135/release-information.git
cd release-information
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
```

Issue 와 PR 을 환영합니다. 이 프로젝트는 **렌더링된 HTML 출력의 안정성** 에 최적화되어 있습니다
(인라인 CSS 는 public 계약이며, 변경하면 모든 downstream 리포지토리가 강제로 재렌더링됩니다).
동작 변경에는 `CHANGELOG.md` 의 *Changed* 또는 *Breaking* 섹션에 항목이 필요합니다.

## 릴리스

메인테이너 안내: PyPI 릴리스 워크플로 (태그 기반, OIDC 를 통한 Trusted Publishing — API
토큰 불필요) 에 대해서는 [`docs/PUBLISHING.ko.md`](./docs/PUBLISHING.ko.md) 를 참조하십시오.

## 로드맵 (v0.1.0 의 범위 외)

- `pre-commit` 프레임워크 (`.pre-commit-hooks.yaml`) 와의 번들 hook 병렬 통합
- CLI 플래그를 통한 다중 테마 전환
- 프런트매터 기반 릴리스 노트 구조 (`version`, `date`, `breaking` 키)
- npm 배포 / Husky 브리지
- Windows pre-commit hook (PowerShell)

## 라이선스

[MIT](./LICENSE)
