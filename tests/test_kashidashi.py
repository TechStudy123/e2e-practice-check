import datetime as dt

from playwright.sync_api import Page, expect


def login(page: Page) -> None:
    page.goto("/login")
    page.get_by_label("ユーザー名").fill("tanaka")
    page.get_by_label("パスワード").fill("renshu-1234")
    page.get_by_role("button", name="ログイン").click()


def test_login_ok(page: Page):
    login(page)
    expect(page.get_by_role("heading", name="備品の一覧")).to_be_visible()
    expect(page.get_by_text("tanaka さん")).to_be_visible()


def test_login_ng(page: Page):
    page.goto("/login")
    page.get_by_label("ユーザー名").fill("tanaka")
    page.get_by_label("パスワード").fill("wrong")
    page.get_by_role("button", name="ログイン").click()
    expect(page.get_by_role("alert")).to_have_text("ユーザー名かパスワードが違います")


def test_search(page: Page):
    login(page)
    page.get_by_label("備品をさがす").fill("PC")
    page.get_by_role("button", name="検索").click()
    expect(page.get_by_role("row")).to_have_count(3)
    expect(page.get_by_test_id("item-count")).to_have_text("2 件")


def test_news_appears_later(page: Page):
    login(page)
    expect(page.locator("#news")).to_have_text("金曜日の 17 時から、備品の棚卸しをします")


def test_borrow(page: Page):
    login(page)
    row = page.get_by_role("row").filter(has_text="プロジェクター")
    row.get_by_role("link", name="借りる").click()
    due = (dt.date.today() + dt.timedelta(days=3)).isoformat()
    page.get_by_label("返す日").fill(due)
    page.get_by_label("使う目的").fill("会議で使う")
    page.get_by_role("button", name="貸し出しを登録").click()
    expect(page.get_by_role("status")).to_have_text("プロジェクター を貸し出しました")
    expect(row).to_contain_text("貸出中")


def test_borrow_past_date(page: Page):
    login(page)
    page.goto("/items/1/borrow")
    page.get_by_label("返す日").fill("2020-01-01")
    page.get_by_label("使う目的").fill("会議で使う")
    page.get_by_role("button", name="貸し出しを登録").click()
    expect(page.get_by_role("alert")).to_have_text("返す日は今日以降にしてください")


def test_api_prepare(page: Page, playwright, base_url):
    req = playwright.request.new_context(base_url=base_url)
    req.post("/api/items/2/borrow", data={"borrower": "suzuki", "due": "2099-12-31"})
    req.dispose()
    login(page)
    expect(page.get_by_role("row").filter(has_text="ノートPC B")).to_contain_text("貸出中（suzuki")
