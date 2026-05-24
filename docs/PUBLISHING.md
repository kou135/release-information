# Publishing to PyPI

This project publishes to PyPI via **GitHub Actions + Trusted Publishing (OIDC)**.
No long-lived API tokens are stored in repo secrets.

## First-time setup (one-time, manual)

These steps must be performed by the repo owner before the first release.

### 1. Create a PyPI account

https://pypi.org/account/register/

Enable 2FA (required for publishing).

### 2. Reserve the project name

Since `release-information` does not yet exist on PyPI, we use a **pending publisher**:

1. Go to https://pypi.org/manage/account/publishing/
2. Fill in the "Add a new pending publisher" form:
   - **PyPI Project Name**: `release-information`
   - **Owner**: `kou135`
   - **Repository name**: `release-information`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
3. Submit.

### 3. Create the GitHub Environment

1. Go to https://github.com/kou135/release-information/settings/environments
2. Click **New environment**, name it `pypi`.
3. (Optional) Add `Required reviewers` = yourself, so every publish needs a manual approval click.
4. Save.

## Releasing a new version

```bash
# 1. Bump version in pyproject.toml (e.g. 0.1.0 -> 0.1.1)
# 2. Update CHANGELOG.md
# 3. Commit and push
git commit -am "release: v0.1.1"
git push

# 4. Tag and push the tag (this triggers the publish workflow)
git tag v0.1.1
git push --tags
```

The `Publish to PyPI` workflow will:
1. Build `sdist` + `wheel`.
2. Wait for environment approval (if required reviewers configured).
3. Upload to PyPI via OIDC — no token needed.

After success, the package is live at https://pypi.org/project/release-information/
and installable via `pip install release-information`.

## After the first successful publish

The "pending publisher" becomes a regular publisher automatically.
Subsequent releases just need a new tag — no PyPI dashboard changes.

## Rolling back

PyPI does **not** allow re-uploading the same version. If something is broken,
yank the release on PyPI and publish a new patch version:

```bash
# yank via web UI: https://pypi.org/manage/project/release-information/releases/
# then:
# bump to 0.1.2 in pyproject.toml + CHANGELOG, commit, tag, push.
```
