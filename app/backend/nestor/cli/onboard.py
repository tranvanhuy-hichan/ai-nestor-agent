"""nestor onboard: trinh huong dan cai dat lan dau (ngon ngu, ten, provider, an toan, Telegram, khoi dong)."""
import os
import shutil
import subprocess
import sys

import httpx

from ..core import config as cfgmod
from ..core.presets import OLLAMA, PRESETS, Preset
from ..services import auth, providers
from . import daemon, runtime, service
from .ui import L, ask, ask_secret, ask_yes_no, bold, choose, dim, err, green, ok, red, set_lang, warn, yellow


def _banner() -> None:
    from .banner import print_onboard_banner
    print_onboard_banner()


def _docker_ready() -> bool:
    if not shutil.which("docker"):
        return False
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=8).returncode == 0
    except (subprocess.SubprocessError, OSError):
        return False


def _unique(cfg: cfgmod.Config, base: str) -> str:
    name, i = base, 2
    while name in cfg.providers:
        name = f"{base}{i}"
        i += 1
    return name


def _test_provider(p: cfgmod.ProviderCfg) -> list[str] | None:
    """Tra ve danh sach model neu ket noi duoc, None neu loi (da in ly do)."""
    try:
        return providers.list_models(p, only_chat=True)
    except providers.ProviderError as e:
        print(red(f"  ✗ {e}"))
        return None


def _pick_model(models: list[str], default: str, interactive: bool) -> str | None:
    if not models:
        return ask(L("Tên model", "Model name"), default) if interactive else default
    shown = models[:12]
    default_i = shown.index(default) if default in shown else 0
    if not interactive:
        return default if default in models else models[0]
    i = choose(L("Chọn model", "Pick a model"),
               [*shown, L("(nhập tên khác)", "(type another name)"), L("← Quay lại", "← Back")],
               default_i, back=len(shown) + 1)
    if i == len(shown) + 1:
        return None
    return ask(L("Tên model", "Model name"), default) if i == len(shown) else shown[i]


def add_provider(cfg: cfgmod.Config, preset: Preset, *, interactive: bool, model: str | None = None, base_url: str | None = None,
                 api_key_env: str | None = None, api_key: str | None = None, skip_test: bool = False) -> str | None:
    p = cfgmod.ProviderCfg(type=preset.type, base_url=base_url or preset.base_url, model=model or preset.model, api_key_env=api_key_env or preset.env, **({"cli": preset.cli} if preset.cli else {}))
    if preset.type == "cli":  # CLI da dang nhap san: khong co API key, chi can kiem tra lenh co trong may
        from ..services import cli_provider

        exe = cli_provider.find(p)
        if not exe:
            warn(L(f"Không tìm thấy lệnh '{cli_provider.executable(p)[0]}'. Hãy cài CLI và đăng nhập một lần trong terminal.", f"Command '{cli_provider.executable(p)[0]}' not found. Install the CLI and log in once in a terminal."))
            if not interactive or not ask_yes_no(L("Vẫn lưu provider này?", "Save this provider anyway?"), False):
                return None
            models = []
        else:
            ok(L(f"Tìm thấy CLI: {exe}", f"Found the CLI: {exe}"))
            models = cli_provider.list_cli_models(p) if p.cli == "agy" else (cli_provider.CLAUDE_MODELS if p.cli == "claude" else [])
        return _store_provider(cfg, preset, p, models, interactive)
    if preset.id == "custom" and interactive:
        p.base_url = ask("Base URL", p.base_url)
    if api_key:
        p.api_key = api_key  # moi provider deu nhan key, ke ca provider tu host (custom) khong co ten bien mac dinh
    if preset.env:
        have_env = bool(os.environ.get(p.api_key_env))
        if api_key:
            pass
        elif interactive:
            if have_env and ask_yes_no(L(f"Dùng API key trong biến môi trường {p.api_key_env}?", f"Use the API key from the {p.api_key_env} environment variable?"), True):
                pass
            else:
                p.api_key = ask_secret(L(f"Dán API key cho {preset.label}", f"Paste the API key for {preset.label}"))
                if not p.api_key:
                    p.api_key_env = ask(L("…hoặc tên biến môi trường chứa key", "…or the environment variable holding the key"), p.api_key_env)
    elif interactive and not preset.env and preset.id == "custom":
        p.api_key = ask_secret(L("API key (bỏ trống nếu không cần)", "API key (leave empty if not needed)"))
    if skip_test:
        models = []
    else:
        print(dim(L("  Đang kiểm tra kết nối…", "  Checking the connection…")))
        models = _test_provider(p)
        if models is None:
            if not interactive or not ask_yes_no(L("Vẫn lưu provider này?", "Save this provider anyway?"), False):
                return None
            models = []
        else:
            ok(L(f"Kết nối được ({len(models)} model).", f"Connected ({len(models)} models)."))
    return _store_provider(cfg, preset, p, models, interactive)


def _store_provider(cfg, preset, provider, models, interactive):
    model = _pick_model(models, provider.model, interactive)
    if model is None:
        return None
    provider.model = model
    name = _unique(cfg, preset.id)
    cfg.providers[name] = provider
    return name


def _drop_untouched_local(cfg: cfgmod.Config) -> None:
    """Provider 'local' (Ollama qwen2.5:3b) la gia tri mac dinh; neu nguoi dung vua them provider khac thi bo no cho gon."""
    if "local" in cfg.providers and len(cfg.providers) > 1 and cfg.providers["local"] == cfgmod.Config().providers["local"] and cfg.default_provider != "local":
        del cfg.providers["local"]
        cfg.fallback = [f for f in cfg.fallback if f != "local"]


def _step_provider(cfg: cfgmod.Config, args) -> None:
    if not args.provider:
        return
    preset = next((x for x in [OLLAMA, *PRESETS] if x.id == args.provider), None)
    if not preset:
        err(L(f"Không có provider mẫu '{args.provider}'.", f"Unknown provider preset '{args.provider}'."))
        return
    key = sys.stdin.read().strip() if args.api_key_stdin else None
    name = add_provider(cfg, preset, interactive=False, model=args.model, base_url=args.base_url, api_key_env=args.api_key_env, api_key=key, skip_test=args.skip_test)
    if name:
        cfg.default_provider = name
        _drop_untouched_local(cfg)
        ok(L(f"Đã thêm {name}.", f"Added {name}."))


def _set_password(cfg: cfgmod.Config) -> None:
    while True:
        pw = ask_secret(L("Mật khẩu giao diện (≥ 8 ký tự, Enter để quay lại)", "Interface password (8+ characters, Enter to go back)"))
        if not pw:
            return
        if len(pw) < 8:
            print(red(L("  Quá ngắn.", "  Too short.")))
            continue
        if pw != ask_secret(L("Nhập lại", "Repeat")):
            print(red(L("  Không khớp.", "  They do not match.")))
            continue
        auth.set_password(cfg, pw)
        return


def _connect_telegram(cfg: cfgmod.Config, token: str, uid: str) -> bool:
    if not token:
        return False
    try:
        r = httpx.post(f"{cfg.channels.telegram.api_base}/bot{token}/getMe", timeout=10).json()
    except (httpx.HTTPError, ValueError):
        warn(L("Không gọi được Telegram.", "Could not reach Telegram."))
        return False
    if not r.get("ok"):
        warn(L(f"Token không hợp lệ: {r.get('description')}", f"Invalid token: {r.get('description')}"))
        return False
    cfg.channels.telegram.enabled, cfg.channels.telegram.token = True, token
    if uid.isdigit():
        cfg.channels.telegram.allowed_users = [int(uid)]
    ok(L(f"Đã kết nối @{r['result']['username']}.", f"Connected @{r['result']['username']}.") + ("" if uid.isdigit() else dim(L(" Ghép đôi: giao diện web > Tích hợp > Kênh chat.", " Pair it in the web UI > Integrations > Chat channels."))))
    return True


def _enable_heartbeat(cfg: cfgmod.Config) -> None:
    from ..services import heartbeat

    f = cfg.workspace_path() / "HEARTBEAT.md"
    if not f.exists():
        f.write_text(heartbeat.DEFAULT_FILE)
    cfg.heartbeat.enabled = True


def _write_profile(cfg: cfgmod.Config, name: str) -> None:
    user_md = cfg.workspace_path() / "USER.md"
    if name and not user_md.exists():
        user_md.write_text(f"# USER\n- {L('Tên', 'Name')}: {name}\n- {L('Ngôn ngữ ưu tiên', 'Preferred language')}: {'Tiếng Việt' if cfg.language == 'vi' else 'English'}\n")
        ok(L("Đã ghi USER.md.", "Wrote USER.md."))


def _save(cfg: cfgmod.Config) -> None:
    cfgmod.save(cfg)
    ok(L(f"Đã lưu cấu hình: {cfgmod.CONFIG_PATH}", f"Configuration saved: {cfgmod.CONFIG_PATH}"))


def run(args) -> int:
    if args.language:
        set_lang(args.language)
    elif not args.non_interactive:
        i = choose("Language / Ngôn ngữ", ["Tiếng Việt", "English"], 0 if L("v", "e") == "v" else 1)
        set_lang(("vi", "en")[i])
    _banner()
    if not args.non_interactive:
        from . import onboard_menu

        return onboard_menu.run(args)

    cfg = runtime.bootstrap()
    cfg.language = L("vi", "en")
    _write_profile(cfg, args.name)
    _step_provider(cfg, args)
    cfg.agent.exec_sandbox = args.sandbox
    if args.password_env and not cfg.auth.password_hash:
        pw = os.environ.get(args.password_env, "")
        if len(pw) >= 8:
            auth.set_password(cfg, pw)
        else:
            warn(L(f"Biến {args.password_env} trống hoặc ngắn hơn 8 ký tự, bỏ qua mật khẩu.", f"{args.password_env} is empty or shorter than 8 characters; password skipped."))
    if args.telegram_token_env:
        _connect_telegram(cfg, os.environ.get(args.telegram_token_env, ""), "")
    if args.heartbeat:
        _enable_heartbeat(cfg)
    _save(cfg)
    host, port = daemon.default_host(), daemon.default_port()
    if args.service:
        service.install(host, port)
    elif args.start:
        daemon.start(host, port)
    print(f"\n{green(L('Xong!', 'Done!'))} {L('Các lệnh hữu ích', 'Useful commands')}:")
    for cmd, vi, en in [("nestor open", "mở giao diện web", "open the web UI"), ("nestor chat", "trò chuyện ngay trong terminal", "chat right in the terminal"),
                        ("nestor run \"…\"", "giao một việc rồi thoát", "run one task and exit"), ("nestor doctor", "chẩn đoán sự cố", "diagnose problems"), ("nestor --help", "mọi lệnh", "all commands")]:
        print(f"  {bold(cmd.ljust(16))}{dim(L(vi, en))}")
    return 0


__all__ = ["run", "add_provider", "yellow"]
