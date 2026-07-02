# Repository Health

**Project:** callscope

**Type:** Python transcript analytics library

## Public boundary

Open transcript parsing and scoring engine only. Real customer transcripts, provider exports, call recordings, and production credentials stay out of this repo.

## Local verification

Run these before opening a PR or publishing a release:

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
ruff check .
```

## Release checklist

- Tests pass from a clean clone.
- Examples use synthetic names, numbers, domains, and records.
- No `.env`, credentials, real transcripts, customer data, private URLs, or production exports are included.
- README examples still match the CLI and library API.
- Any side-effecting workflow stays dry-run or explicitly gated by default.

## GitHub hygiene added

- Bug report and feature request templates.
- Pull request checklist focused on tests and data safety.
- Weekly Dependabot checks for GitHub Actions.
- Security policy when the repo did not already have one.
