# Contributing to Argus Agent / Đóng góp cho Argus Agent

Thanks for your interest! Bug reports, ideas, docs, translations, skills and code are all welcome.
Cảm ơn bạn đã quan tâm! Báo lỗi, ý tưởng, tài liệu, bản dịch, skill và code đều được chào đón.

## Quick start (development)

```bash
git clone https://github.com/tranvanhuy-hichan/argus-agent.git && cd argus-agent
python3 -m venv .venv && .venv/bin/pip install -e "app/backend[dev]"
(cd app/frontend && npm install && npm run build)
```

## Workflow

1. Open an [issue](https://github.com/tranvanhuy-hichan/argus-agent/issues) first for large changes. Look for `good first issue` / `help wanted` labels if you are new.
2. Fork, then branch from `main` (`feat/...`, `fix/...`, `docs/...`).
3. Keep changes focused; add or update tests when behavior changes.
4. Before opening a PR, run:
   ```bash
   cd app/backend && python -m pytest -q
   cd app/frontend && npm run lint && npm run i18n:check && npm run build
   ```
5. Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`) and describe *what* and *why* in the PR.

## Translations

UI strings are wrapped in `t('Vietnamese text')`; add the English version under `app/frontend/src/i18n/en/`. `npm run i18n:check` reports missing or conflicting strings. English translations of `docs/` (currently Vietnamese) are very welcome.

## Never commit personal data

`user-data/` (config with API keys, databases, memory, sessions) is gitignored. Do not commit API keys, tokens or personal documents, including in tests and screenshots.

## License

By contributing you agree that your contributions are licensed under the project's [AGPL-3.0-or-later](LICENSE).

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md). For vulnerabilities see [SECURITY.md](SECURITY.md).
