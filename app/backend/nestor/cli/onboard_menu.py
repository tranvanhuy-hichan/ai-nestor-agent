"""Interactive configuration menu for nestor onboard."""
import os
import shlex
import subprocess
from pathlib import Path

from pydantic import ValidationError

from ..core import config as cfgmod
from ..core.presets import OLLAMA, PRESETS
from ..core.workspace import ensure_workspace
from ..services import skills
from . import daemon, onboard, runtime, service, skillscmd
from .ui import L, ask, ask_secret, ask_yes_no, choose, err, info, warn


def _pick(title, options, *, default=0, back_label=None):
    back = len(options)
    index = choose(title, [*options, back_label or L("← Quay lại", "← Back")],
                   default, back=back)
    return None if index == back else index


def _menu(title, items):
    cursor = 0
    while True:
        cursor = _pick(title, [label for label, _ in items], default=cursor)
        if cursor is None:
            return
        try:
            items[cursor][1]()
        except (OSError, ValidationError) as exc:
            err(str(exc))


def _state(enabled):
    return L("Bật", "On") if enabled else L("Tắt", "Off")


def _field(model, key, label, choices=None):
    current = getattr(model, key)
    if isinstance(current, bool):
        choices = [True, False]
    if choices:
        labels = [_state(v) if isinstance(v, bool) else str(v) for v in choices]
        index = _pick(label, labels, default=choices.index(current))
        if index is None:
            return
        value = choices[index]
    else:
        value = ask(label, str(current))
    updated = type(model).model_validate({**model.model_dump(), key: value})
    setattr(model, key, getattr(updated, key))


def _setting(label, model, key, choices=None):
    return label, lambda: _field(model, key, label, choices)


def _edit_file(cfg, name):
    command = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
    try:
        subprocess.run([*shlex.split(command), str(cfg.workspace_path() / name)], check=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        err(str(exc))


def _workspace(cfg, initial_name):
    def change_path():
        path = ask(L("Thư mục workspace", "Workspace directory"), cfg.agent.workspace)
        candidate = cfg.model_copy(deep=True)
        candidate.agent.workspace = str(Path(path).expanduser())
        ensure_workspace(candidate)
        if candidate.heartbeat.enabled:
            onboard._enable_heartbeat(candidate)
        cfg.agent.workspace = candidate.agent.workspace
        info(str(cfg.workspace_path()))

    def profile():
        if (cfg.workspace_path() / "USER.md").exists():
            info(L("Chọn USER.md để sửa hồ sơ hiện có.", "Select USER.md to edit the existing profile."))
            return
        name = ask(L("Bạn tên là gì?", "What is your name?"), initial_name)
        onboard._write_profile(cfg, name)

    _menu(L("Không gian làm việc", "Workspace"), [
        (L("Đổi thư mục workspace", "Change workspace directory"), change_path),
        (L("Tạo hồ sơ người dùng", "Create user profile"), profile),
        ("USER.md", lambda: _edit_file(cfg, "USER.md")),
        ("SOUL.md", lambda: _edit_file(cfg, "SOUL.md")),
        ("MEMORY.md", lambda: _edit_file(cfg, "MEMORY.md")),
    ])


def _providers(cfg):
    def add():
        presets = [OLLAMA, *PRESETS]
        index = _pick(L("Chọn nhà cung cấp", "Choose a provider"), [p.label for p in presets])
        if index is not None:
            name = onboard.add_provider(cfg, presets[index], interactive=True)
            if name and ask_yes_no(L("Đặt làm provider mặc định?", "Make this the default provider?")):
                cfg.default_provider = name
                cfg.fallback = [p for p in cfg.fallback if p != name]

    def default():
        names = list(cfg.providers)
        index = _pick(L("Provider mặc định", "Default provider"), names,
                      default=names.index(cfg.default_provider) if cfg.default_provider in names else 0)
        if index is not None:
            cfg.default_provider = names[index]
            cfg.fallback = [name for name in cfg.fallback if name != cfg.default_provider]

    def fallback():
        names = [name for name in cfg.providers if name != cfg.default_provider]
        info(", ".join(names) or "—")
        value = ask(L("Provider dự phòng theo thứ tự, cách nhau bằng dấu phẩy (0 để xóa)",
                      "Fallback providers in order, comma-separated (0 to clear)"), ", ".join(cfg.fallback))
        selected = list(dict.fromkeys(name.strip() for name in value.split(",") if name.strip())) if value != "0" else []
        if any(name not in names for name in selected):
            warn(L("Provider dự phòng không hợp lệ.", "Invalid fallback provider."))
            return
        cfg.fallback = selected

    def edit():
        names = list(cfg.providers)
        index = _pick(L("Chọn provider cần sửa", "Select a provider to edit"), names)
        if index is None:
            return
        provider = cfg.providers[names[index]]
        items = [_setting(L("Tên model", "Model name"), provider, "model")]
        if provider.type == "cli":
            items.append(_setting(L("Lệnh CLI", "CLI command"), provider, "command"))
        else:
            def api_key():
                value = ask_secret(L("API key mới (Enter để giữ nguyên)", "New API key (Enter to keep current)"))
                if value:
                    provider.api_key = value

            items.extend([
                _setting("Base URL", provider, "base_url"),
                _setting(L("Biến môi trường API key", "API key environment variable"), provider, "api_key_env"),
                ("API key", api_key),
            ])
        _menu(names[index], items)

    _menu(L("Model AI", "AI models"), [
        (L("Thêm provider", "Add provider"), add),
        (L("Sửa provider", "Edit provider"), edit),
        (L("Provider mặc định", "Default provider"), default),
        (L("Provider dự phòng", "Fallback providers"), fallback),
    ])


def _skills(cfg):
    def install():
        ref = ask(L("Tên skill trên ClawHub (owner/slug)", "ClawHub skill name (owner/slug)"))
        if ref:
            skillscmd.install(ref, yes=False, overwrite=False, cfg=cfg)

    _menu("Skills", [
        (L("Bật / tắt skill đã cài", "Enable / disable installed skills"), lambda: _installed_skills(cfg)),
        (L("Cài skill từ ClawHub", "Install a skill from ClawHub"), install),
        _setting("ClawHub URL", cfg, "clawhub_url"),
    ])


def _installed_skills(cfg):
    installed = skills.discover(cfg)
    names = sorted(name for name, skill in installed.items() if not skill.bundled)
    if not names:
        info(L("Chưa có skill. Dùng nestor skills search và nestor skills install.",
               "No skills found. Use nestor skills search and nestor skills install."))
        return
    cursor = 0
    while True:
        labels = [(name, _state(cfg.skills.get(name, cfgmod.SkillEntry()).enabled)) for name in names]
        cursor = _pick("Skills", labels, default=cursor)
        if cursor is None:
            return
        name = names[cursor]
        _skill_settings(cfg, installed[name])


def _skill_settings(cfg, skill):
    name = skill.name
    entry = cfg.skills.get(name, cfgmod.SkillEntry())
    if skill.missing:
        info(L("Yêu cầu chưa đáp ứng", "Unmet requirements") + " · " + ", ".join(skill.missing))

    def set_secret(var):
        value = ask_secret(L(f"{var} (Enter để giữ nguyên)", f"{var} (Enter to keep current)"))
        if value:
            entry.env[var] = value
            if var == skill.meta.get("primaryEnv"):
                entry.api_key = value

    requires = skill.meta.get("requires") or {}
    variables = list(dict.fromkeys(requires.get("env") or []))
    primary = skill.meta.get("primaryEnv")
    if primary and primary not in variables:
        variables.insert(0, primary)
    _menu(name, [
        _setting(L("Bật / tắt skill", "Enable / disable skill"), entry, "enabled"),
        *((var, lambda var=var: set_secret(var)) for var in variables),
    ])
    if name in cfg.skills or not entry.enabled or entry.env:
        cfg.skills[name] = entry


def _tool(cfg, name, label):
    policy = cfg.agent.tool_policies.get(name)
    enabled = cfg.agent.tools_enabled.get(name, True) and (policy is None or policy.enabled)
    index = _pick(label, [_state(True), _state(False)], default=0 if enabled else 1)
    if index is not None:
        cfg.agent.tools_enabled[name] = index == 0
        if policy is not None:
            policy.enabled = index == 0


def _web(cfg):
    _menu(L("Tìm kiếm web và trình duyệt", "Web search and browser"), [
        ("Web search · DuckDuckGo", lambda: _tool(cfg, "web_search", "DuckDuckGo")),
        (L("Đọc trang web", "Fetch web pages"), lambda: _tool(cfg, "web_fetch", "Web fetch")),
        _setting(L("Công cụ trình duyệt", "Browser tool"), cfg.browser, "enabled"),
        _setting(L("Trình duyệt không giao diện", "Headless browser"), cfg.browser, "headless"),
        _setting(L("Đường dẫn Chrome / Chromium", "Chrome / Chromium executable"), cfg.browser, "executable"),
        _setting(L("Thời gian chờ trình duyệt (phút)", "Browser idle time (minutes)"), cfg.browser, "idle_minutes"),
    ])


def _security(cfg):
    def sandbox():
        previous = cfg.agent.exec_sandbox
        _field(cfg.agent, "exec_sandbox", "Sandbox", ["none", "docker"])
        if previous != "docker" and cfg.agent.exec_sandbox == "docker" and not onboard._docker_ready():
            cfg.agent.exec_sandbox = previous
            warn(L("Docker chưa sẵn sàng.", "Docker is not ready."))

    def password():
        if ask_yes_no(L("Đặt mật khẩu web?", "Set a web password?"), False):
            onboard._set_password(cfg)

    _menu(L("An toàn và truy cập", "Security and access"), [
        _setting(L("Xác nhận lệnh shell", "Shell command approval"), cfg.agent, "confirm_exec"),
        ("Sandbox", sandbox),
        _setting(L("Image sandbox Docker", "Docker sandbox image"), cfg.agent, "sandbox_image"),
        (L("Đặt hoặc đổi mật khẩu web", "Set or change web password"), password),
    ])


def _telegram(cfg):
    telegram = cfg.channels.telegram

    def connect():
        token = ask_secret(L("Token bot từ @BotFather (Enter để quay lại)",
                             "Bot token from @BotFather (Enter to go back)"))
        if token:
            onboard._connect_telegram(cfg, token, "")

    def allowed_users():
        value = ask(L("ID Telegram, cách nhau bằng dấu phẩy (0 để ghép đôi lại)",
                      "Telegram IDs, comma-separated (0 to pair again)"),
                    ", ".join(map(str, telegram.allowed_users)))
        if not value:
            return
        try:
            ids = [] if value == "0" else list(dict.fromkeys(int(uid.strip()) for uid in value.split(",")))
        except ValueError:
            warn(L("ID Telegram không hợp lệ.", "Invalid Telegram ID."))
            return
        telegram.allowed_users = ids

    def toggle():
        if telegram.token:
            _field(telegram, "enabled", "Telegram")
        else:
            warn(L("Hãy kết nối bot trước.", "Connect a bot first."))

    _menu("Telegram", [
        (L("Kết nối bot", "Connect bot"), connect),
        (L("Bật / tắt Telegram", "Enable / disable Telegram"), toggle),
        (L("Người dùng được phép", "Allowed users"), allowed_users),
    ])


def _heartbeat(cfg):
    heartbeat = cfg.heartbeat

    def toggle():
        index = _pick("Heartbeat", [_state(True), _state(False)], default=0 if heartbeat.enabled else 1)
        if index == 0:
            onboard._enable_heartbeat(cfg)
        elif index == 1:
            heartbeat.enabled = False

    def provider():
        names = [None, *cfg.providers]
        index = _pick(L("Provider heartbeat", "Heartbeat provider"),
                      [L("Mặc định", "Default"), *cfg.providers],
                      default=names.index(heartbeat.provider) if heartbeat.provider in names else 0)
        if index is not None:
            heartbeat.provider = names[index]

    _menu("Heartbeat", [
        (L("Bật / tắt heartbeat", "Enable / disable heartbeat"), toggle),
        _setting(L("Chu kỳ (phút)", "Interval (minutes)"), heartbeat, "interval_minutes"),
        (L("Provider heartbeat", "Heartbeat provider"), provider),
        ("HEARTBEAT.md", lambda: _edit_file(cfg, "HEARTBEAT.md")),
    ])


def _daemon(cfg, host, port):

    def address():
        nonlocal host, port
        new_host = ask(L("Địa chỉ lắng nghe", "Listen address"), host)
        raw = ask(L("Cổng", "Port"), str(port))
        if not raw.isascii() or not raw.isdecimal() or len(raw) > 5 or not 1 <= int(raw) <= 65535:
            warn(L("Cổng phải nằm trong khoảng 1–65535.", "Port must be between 1 and 65535."))
            return
        host, port = new_host, int(raw)

    def launch(action):
        if ask_yes_no(L("Lưu cấu hình và tiếp tục?", "Save configuration and continue?"), False):
            onboard._save(cfg)
            action(host, port)

    _menu("Daemon", [
        (L("Trạng thái", "Status"), daemon.status),
        (L("Địa chỉ và cổng cho lần chạy này", "Address and port for this launch"), address),
        (L("Khởi động", "Start"), lambda: launch(daemon.start)),
        (L("Khởi động lại với địa chỉ hiện tại", "Restart at current server address"), lambda: launch(daemon.restart)),
        (L("Dừng", "Stop"), lambda: daemon.stop() if ask_yes_no(L("Dừng daemon?", "Stop daemon?"), False) else None),
        (L("Cài dịch vụ tự khởi động", "Install auto-start service"), lambda: launch(service.install)),
        (L("Gỡ dịch vụ tự khởi động", "Remove auto-start service"),
         lambda: service.uninstall() if ask_yes_no(L("Gỡ dịch vụ?", "Remove service?"), False) else None),
    ])
    return host, port


def run(args) -> int:
    cfg = runtime.bootstrap()
    cfg.language = L("vi", "en")
    info(str(cfgmod.CONFIG_PATH))
    state = daemon.read_state()
    host = state.get("host", daemon.default_host())
    port = state.get("port", daemon.default_port())

    def daemon_menu():
        nonlocal host, port
        host, port = _daemon(cfg, host, port)

    items = [
        (L("Model AI", "AI models"), lambda: _providers(cfg)),
        (L("Không gian làm việc", "Workspace"), lambda: _workspace(cfg, args.name)),
        ("Skills", lambda: _skills(cfg)),
        (L("Tìm kiếm web và trình duyệt", "Web search and browser"), lambda: _web(cfg)),
        (L("An toàn và truy cập", "Security and access"), lambda: _security(cfg)),
        ("Telegram", lambda: _telegram(cfg)),
        ("Heartbeat", lambda: _heartbeat(cfg)),
        (L("Bộ nhớ", "Memory"), lambda: _menu(L("Bộ nhớ", "Memory"), [
            _setting("Embeddings", cfg.memory, "embeddings", ["off", "auto", "ollama", "openai", "hash"]),
            _setting(L("Tự lập chỉ mục", "Automatic indexing"), cfg.memory, "auto_index"),
            _setting(L("Model embedding", "Embedding model"), cfg.memory, "model"),
        ])),
        (L("Giới hạn agent", "Agent limits"), lambda: _menu(L("Giới hạn agent", "Agent limits"), [
            _setting(L("Số bước tối đa", "Maximum steps"), cfg.agent, "max_steps"),
            _setting(L("Số tin nhắn lịch sử", "History length"), cfg.agent, "max_history"),
            _setting(L("Ngưỡng tóm tắt (ký tự)", "Compaction threshold (characters)"), cfg.agent, "compact_chars"),
            _setting(L("Gợi ý thói quen", "Suggest habits"), cfg.agent, "suggest_habits"),
        ])),
        ("Daemon", daemon_menu),
    ]
    title = L("Thiết lập Nestor", "Nestor setup")
    save = L("Lưu và thoát", "Save and exit")
    cursor = 0
    while True:
        try:
            cursor = _pick(title, [label for label, _ in items] + [save], default=cursor,
                           back_label=L("Thoát không lưu cấu hình", "Exit without saving configuration"))
            if cursor is None:
                return 0
            if cursor == len(items):
                onboard._save(cfg)
                if args.service:
                    return service.install(host, port)
                return daemon.start(host, port) if args.start else 0
            items[cursor][1]()
        except EOFError:
            return 0
        except (OSError, ValidationError) as exc:
            err(str(exc))
