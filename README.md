<p align="center"><img src="docs/assets/argus-logo.png" alt="Argus" width="320"></p>

# Argus Agent

<p align="center">
  <a href="README.vi.md">🇻🇳 Tiếng Việt</a> · <b>🇬🇧 English</b>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: AGPL-3.0-or-later" src="https://img.shields.io/badge/license-AGPL--3.0--or--later-blue"></a>
  <img alt="Python 3.11+" src="https://img.shields.io/badge/python-3.11%2B-3776AB">
  <img alt="PRs welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen">
</p>

An **open-source** personal AI assistant that runs on your own machine and keeps your data there: a background gateway, web UI, the **`argus` CLI**, `SKILL.md` skills, markdown memory, tools, MCP, Telegram and automations.

## Features

- **Models**: Ollama and local servers (LM Studio, vLLM), Gemini, Claude, OpenAI, OpenRouter, DeepSeek (R1, V3), Mistral, xAI, Groq, Cerebras, Together, Fireworks, Qwen, and any OpenAI-compatible API. Fallbacks, automatic retry on 429/503, cost estimates, and a visual local-model browser/picker.
- **Chat**: a right-hand Workspace panel (Files, Terminal, Activity); every tool/MCP call shown inline; collapsible "deep thinking" (`<think>`) blocks; Live Preview for HTML/SVG files the agent creates; file/image attachments; voice input; edit and regenerate messages; `/skill` commands and `@service` mentions. Each session gets its own working directory (`user-data/workspace/sessions/<id>/`).
- **Knowledge Base & RAG**: ingest and index PDF, Word `.docx`, Excel `.xlsx`, `.csv`, PowerPoint `.pptx`, Markdown and text with a progress bar. Turn on "Ask from documents" in the chat bar and answers come with clickable citations `[1]`, `[2]` that jump to the source passage and page.
- **Streamlined toolbar, deep customization**:
  - Pick the AI model directly, with detailed labels.
  - **Reasoning & Parameters**: reasoning level (`Auto`, `Deep thinking`, `Low`, `Medium`, `High`), **Temperature** slider (0.0–1.5) and **Max Tokens** (1k–8k).
  - **Permissions & Quota**: execution permission (`Default`, `Safe`, `Full access`) and token quota charts (5h / 7 days).
- **Smart conversation management**: automatic short titles after the first reply, pinned chats, wrapped sidebar titles, full-text search across chat history.
- **Skills**: reads the `SKILL.md` format (compatible with [ClawHub](https://clawhub.ai)); browse, install and update from ClawHub.
- **MCP client**: connect your MCP servers (stdio, HTTP, SSE); tools appear as `servername__toolname`.
- **Call the agent from other apps**: `POST /v1/run` with an API token, or the MCP server (`agent_run`) usable from Claude Code, Cursor, etc.
- **Office assistant (COffice-AI style)**: creates real Word / Excel (live formulas) / PowerPoint files, drafts and **checks Vietnamese administrative document formatting per Decree 30/2020**; 10 **specialist assistants** (records, Party documents, report synthesis, secretary, accounting, HR, sales, project, legal, IT) plus custom ones; **Zalo OA** channel (send tasks, receive results, pairing like Telegram); a **Morning digest** automation; one-click **distill a chat into a Skill/Rule**; multi-agent **teams** running in parallel with a shared notebook; the agent can **write and run scripts** for batch jobs and save them as skills.
- **Proactive**: Automations (cron), Heartbeat (the agent checks `HEARTBEAT.md` and pings you when needed), a notification inbox, and a **Telegram** channel (approval buttons in chat, file send/receive).
- **Memory**: `MEMORY.md`, full-text search over all past chats (`memory_search`), automatic summarization of long conversations.
- **Bilingual Vietnamese/English UI**: switch language at the top of the sidebar (CLI follows `--lang`). To add strings, wrap them in `t('Vietnamese text')` and add the English version under `app/frontend/src/i18n/en/`; `npm run i18n:check` catches missing, untranslated or conflicting strings.
- **Safe by default**: shell commands, files outside the session directory and MCP tools ask for confirmation; optional Docker sandbox (no network); optional login password; audit log of every tool call; localhost-only by default; API tokens stored only as hashes.

## Documentation

> The in-depth docs are currently written in Vietnamese. English translations are welcome as contributions.

- [User guide](docs/huong-dan-su-dung.md): for everyday users
- [`argus` CLI reference](docs/cli.md)
- [Architecture](docs/kien-truc.md): for developers

## Installation

Requires Python 3.11+ (and Node 20+ if you want to build the UI yourself).

```bash
git clone https://github.com/tranvanhuy-hichan/argus-agent.git && cd argus-agent
python3 -m venv .venv && .venv/bin/pip install -e app/backend
(cd app/frontend && npm install && npm run build)     # web UI
.venv/bin/argus onboard                           # wizard: model, safety, Telegram, start
```

Add `.venv/bin` to your `PATH` (or `source .venv/bin/activate`) to type just `argus ...`.

## `argus` CLI

| Command | Purpose |
|---|---|
| `argus onboard` | First-time setup: menus driven by **↑/↓, Space (tick), Enter**, Yes/No toggled with ←/→. Falls back to numbered prompts without a real terminal (pipe, CI, Windows); `--non-interactive` + flags for automation |
| `argus start` / `stop` / `restart` / `status` | Manage the background server (`start -f` runs in the foreground, `--host 0.0.0.0` exposes it to other machines) |
| `argus logs -f` | Follow logs |
| `argus open` | Open the web UI |
| `argus doctor` | Diagnostics (`--fix` repairs safe issues, `--offline`, `--json`) |
| `argus chat` | Chat in the terminal (asks `y/N` for approvals; `/help` lists commands) |
| `argus run "task"` | One-shot run then exit: `--json`, `--exec-policy deny\|allow\|allowlist`, `--allow "git status"`, `--ask`, `--permission readonly`, `-` to read stdin |
| `argus token create\|list\|revoke` | API tokens for `/v1/run` and the MCP server |
| `argus skills list\|search\|install\|remove\|update` | Skills from ClawHub |
| `argus service install\|uninstall\|start\|stop\|status` | Run at login (systemd on Linux, launchd on macOS; `install --dry-run` to preview) |
| `argus backup` / `restore` | Back up and restore config, database and workspace. `--encrypt` password-protects, `--include-key` adds the master key, `restore --force` backs up the current state first |
| `argus secrets status\|encrypt\|decrypt\|keychain\|file\|rotate` | Manage encryption of secrets in `config.json` |
| `argus config path\|show` | Show config (API keys masked) |

`chat` and `run` execute the agent in-process (no running server needed) and share config, skills, MCP and conversations with the web UI. Change CLI language with `--lang vi|en` or `ARGUS_LANG`.

Environment variables: `ARGUS_HOME` (data directory), `ARGUS_PORT`, `ARGUS_HOST`, `ARGUS_CONFIG`, `ARGUS_ALLOWED_HOSTS`, `ARGUS_TOKEN`/`ARGUS_URL` (MCP server). Legacy `AGENT_*` names are still accepted.

`./run.sh` still works as a thin wrapper around `argus`.

## Docker, service, tests

```bash
docker compose up -d --build         # open http://127.0.0.1:8787 (personal data in ./user-data)
argus service install                # run at login, no Docker needed
cd app/backend && pip install -e ".[dev]" && python -m pytest -q
```

To reach Ollama on the host from inside a container, set the Base URL to `http://host.docker.internal:11434/v1`.

## Contributing

Argus is open source and contributions are very welcome: bug reports, feature ideas, docs, translations, skills and code.

1. Open an [issue](https://github.com/tranvanhuy-hichan/argus-agent/issues) to report a bug or discuss an idea before large changes.
2. Fork the repo and branch from `main` (e.g. `feat/my-feature`).
3. Before submitting, run `cd app/backend && python -m pytest -q` and `cd app/frontend && npm run i18n:check`.
4. Open a Pull Request describing what changed and why. Use conventional commit prefixes (`feat:`, `fix:`, `docs:`, ...).
5. To add a language or fix a translation, see the *Bilingual UI* item under Features.

For security vulnerabilities, please do not post publicly; contact the maintainer privately via GitHub.

## License

Argus Agent is free software under the **GNU AGPL-3.0-or-later** (see [LICENSE](LICENSE)). If you modify it and offer it as a network service, you must make the modified source available to that service's users.

Copyright (C) 2026 tranvanhuy-hichan

## Project layout

The project is split in two so your source code and your data are never confused:

```
argus-agent/
├── app/                  # FIXED SOURCE CODE: safe to delete/reinstall, you lose nothing
│   ├── backend/argus/
│   │   ├── api/          # FastAPI routers: chat, skills, providers, integrations, external API (/v1)
│   │   ├── services/     # agent loop, providers, tools, skills, MCP, Telegram, scheduler, browser…
│   │   ├── core/         # config, SQLite, paths
│   │   └── cli/          # the `argus` command (start, doctor, onboard, chat, run, tasks, memory…)
│   ├── frontend/src/     # React + TypeScript + Tailwind (features/ per page, i18n/)
│   ├── templates/workspace/   # SOUL.md and sample skills used to seed a new workspace
│   ├── deploy/           # sample systemd unit
│   └── examples/         # sample MCP server for trying integrations
├── user-data/            # YOUR PERSONAL DATA: don't delete, back it up (`argus backup`)
│   ├── config.json       # config (API keys encrypted)
│   ├── data/             # database, master key (master.key), logs
│   ├── workspace/        # SOUL.md, USER.md, MEMORY.md, skills/, sessions/ (personality, memory, agent files)
│   └── backups/          # backups
├── Dockerfile, docker-compose.yml, run.sh, LICENSE, README.md, README.vi.md
```

To keep data elsewhere (another drive, a synced folder…), set `ARGUS_HOME=/path`. If you installed an older version (data in the repo root), Argus keeps using it until you move `config.json`, `data/`, `workspace/`, `backups/` into `user-data/`.

## Security notes

- Skills downloaded from the internet are only instructions, but they can tell the agent to run commands. Read `SKILL.md` before installing and keep shell-command confirmation on.
- stdio MCP servers run the command you configure with your own privileges. Only add servers you trust.
- `user-data/config.json` (the whole `user-data/` folder is in `.gitignore`). Every secret in it (API keys, Telegram token, MCP env vars/headers, skill keys) is **encrypted** with a master key taken from `ARGUS_MASTER_KEY`, the OS keychain (`pip install keyring` then `argus secrets keychain`) or `user-data/data/master.key` (mode 600). This protects you if the config file leaks on its own (attached to a bug report, pushed to git by mistake, backed up apart from the key); it does **not** protect against an attacker who has both files or is running on your machine. Back up the master key (`argus backup --include-key --encrypt`): without it nothing can be decrypted. `argus doctor` checks this.
