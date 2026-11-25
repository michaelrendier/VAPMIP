"""Tests never write the real usage store: every test gets its own PTOL_USAGE_DIR (the daemon's usage channel, conversation_usage.py)."""
import pytest


@pytest.fixture(autouse=True)
def _private_usage_dir(tmp_path, monkeypatch):
    monkeypatch.setenv('PTOL_USAGE_DIR', str(tmp_path / 'usage'))
