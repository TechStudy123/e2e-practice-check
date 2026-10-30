from playwright.sync_api import Page, expect


def test_login(page: Page):
    page.goto("/login")
    page.get_by_label("ユーザー名").fill("tanaka")
    page.get_by_label("パスワード").fill("renshu-1234")
    page.get_by_role("button", name="ログイン").click()
    expect(page.get_by_role("heading", name="備品の一覧")).to_be_visible()


def test_login_wrong_password(page: Page):
    page.goto("/login")
    page.get_by_label("ユーザー名").fill("tanaka")
    page.get_by_label("パスワード").fill("wrong")
    page.get_by_role("button", name="ログイン").click()
    expect(page.get_by_role("alert")).to_have_text("ユーザー名かパスワードが違います")


def test_login_suzuki(logged_in_suzuki: Page):
    expect(logged_in_suzuki.get_by_text("suzuki さん")).to_be_visible()
