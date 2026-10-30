"""テストの準備（題材のアプリを起動し、終わったら止める）。"""
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import expect

from pages.login_page import LoginPage

PORT = 8810


@pytest.fixture(scope="session", autouse=True)
def app_server():
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "kashidashi.main:app", "--port", str(PORT)]
    )
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", PORT), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    else:
        proc.terminate()
        raise RuntimeError("題材のアプリが起動しませんでした")
    yield
    proc.terminate()
    proc.wait(timeout=10)


@pytest.fixture(scope="session")
def base_url():
    return f"http://127.0.0.1:{PORT}"


@pytest.fixture(autouse=True)
def reset_data(page):
    page.request.post("/api/reset")  # データを最初の状態に戻す


@pytest.fixture(scope="session")
def auth_state(browser, base_url):
    path = Path("playwright/.auth/tanaka.json")
    path.parent.mkdir(parents=True, exist_ok=True)  # 保存先のフォルダを作る
    context = browser.new_context(base_url=base_url)
    page = context.new_page()
    page.goto("/login")
    LoginPage(page).login("tanaka", "renshu-1234")
    expect(page.get_by_role("heading", name="備品の一覧")).to_be_visible()
    context.storage_state(path=path)  # ログインした状態をファイルに保存する
    context.close()
    return path


@pytest.fixture
def browser_context_args(browser_context_args, auth_state):
    return {**browser_context_args, "storage_state": auth_state}


@pytest.fixture
def logged_in(page):
    page.goto("/")
    return page


@pytest.fixture
def logged_in_suzuki(page):
    page.goto("/login")
    LoginPage(page).login("suzuki", "renshu-5678")
    return page
