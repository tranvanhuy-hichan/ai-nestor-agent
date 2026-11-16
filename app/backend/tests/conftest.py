import pytest

from nestor.core import config as cfgmod
from nestor.core import db as dbmod
from nestor.core import secrets


@pytest.fixture
def tmp_env(tmp_path, monkeypatch):
    """Co lap moi thu: DB, config.json va workspace nam trong thu muc tam."""
    monkeypatch.setattr(dbmod, "DB_PATH", tmp_path / "agent.db")
    monkeypatch.setattr(dbmod, "DATA", tmp_path)
    monkeypatch.setattr(cfgmod, "CONFIG_PATH", tmp_path / "config.json")
    monkeypatch.setattr(secrets, "KEY_FILE", tmp_path / "master.key")
    monkeypatch.delenv("NESTOR_MASTER_KEY", raising=False)
    monkeypatch.delenv("AGENT_MASTER_KEY", raising=False)
    secrets.failures.clear()
    ws = tmp_path / "workspace"
    ws.mkdir()
    cfg = cfgmod.Config()
    cfg.agent.workspace = str(ws)
    cfg.memory.embeddings = "off"  # tin nhan trong test khong duoc nhung ngam (luong nen se ghi nham vao DB cua test sau); test tri nho tu bat lai
    cfgmod.save(cfg)
    dbmod.init()
    yield tmp_path
    # luong nen lap chi muc tri nho dung DB_PATH hien tai: cho no ghi het vao DB cua test nay truoc khi monkeypatch tra DB_PATH ve cu
    from nestor.services import memory_index
    memory_index.flush(15)
