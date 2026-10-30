from playwright.sync_api import Page, expect


def test_news(logged_in: Page) -> None:
    expect(logged_in.locator("#news")).to_have_text("金曜日の 17 時から、備品の棚卸しをします")


def test_borrow_page(logged_in: Page) -> None:
    row = logged_in.get_by_role("row").filter(has_text="Web カメラ")
    row.get_by_role("link", name="借りる").click()
    expect(logged_in.get_by_role("heading", name="Web カメラ を借りる")).to_be_visible()


def test_item_count(logged_in: Page) -> None:
    expect(logged_in.get_by_test_id("item-count")).to_have_text("5 件")
