# PyPI 에 공개

이 프로젝트는 **GitHub Actions + Trusted Publishing (OIDC)** 을 통해 PyPI 에 공개됩니다.
장기 보존되는 API 토큰을 repo 의 secret 에 저장하지 않습니다.

## 초기 셋업 (한 번만, 수동)

다음 절차는 최초 릴리스 전에 리포지토리 소유자가 수행해야 합니다.

### 1. PyPI 계정 생성

https://pypi.org/account/register/

2FA 를 활성화해 주십시오 (공개에 필수).

### 2. 프로젝트 이름 예약

`release-information` 은 PyPI 에 아직 존재하지 않으므로 **pending publisher** 를 사용합니다.

1. https://pypi.org/manage/account/publishing/ 에 접속
2. "Add a new pending publisher" 폼에 다음을 입력:
   - **PyPI Project Name**: `release-information`
   - **Owner**: `kou135`
   - **Repository name**: `release-information`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
3. Submit.

### 3. GitHub Environment 를 생성

1. https://github.com/kou135/release-information/settings/environments 에 접속
2. **New environment** 를 클릭하고 이름을 `pypi` 로 설정합니다.
3. (선택) `Required reviewers` 에 본인을 추가하면, 공개할 때마다 수동 승인 클릭이 필요해집니다.
4. Save.

## 새 버전을 릴리스

```bash
# 1. pyproject.toml 의 버전을 bump (예: 0.1.0 -> 0.1.1)
# 2. CHANGELOG.md 를 업데이트
# 3. commit 후 push
git commit -am "release: v0.1.1"
git push

# 4. 태그를 만들고 push (이것으로 publish workflow 가 트리거됩니다)
git tag v0.1.1
git push --tags
```

`Publish to PyPI` workflow 는 다음을 수행합니다:
1. `sdist` 와 `wheel` 을 빌드.
2. (required reviewers 가 설정되어 있다면) Environment 의 승인을 대기.
3. OIDC 를 통해 PyPI 에 업로드 — 토큰 불필요.

성공하면 패키지는 https://pypi.org/project/release-information/ 에서 공개되며,
`pip install release-information` 으로 설치할 수 있게 됩니다.

## 최초 공개 성공 이후

"pending publisher" 는 자동으로 일반 publisher 로 승격됩니다.
이후의 릴리스는 새 태그를 push 하기만 하면 됩니다 — PyPI 대시보드 변경은 불필요합니다.

## 롤백

PyPI 는 같은 버전의 재업로드를 **허용하지 않습니다**. 무언가 깨졌을 때는,
PyPI 상에서 릴리스를 yank 하고 새 패치 버전을 공개합니다:

```bash
# Web UI 로 yank: https://pypi.org/manage/project/release-information/releases/
# 그 후:
# pyproject.toml 과 CHANGELOG 를 0.1.2 로 bump 하고 commit, 태그, push.
```
