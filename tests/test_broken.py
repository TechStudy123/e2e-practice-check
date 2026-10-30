import datetime as dt

from playwright.sync_api import Page, expect

from pages.borrow_page import BorrowPage
from pages.item_list_page import ItemListPage


def test_borrow_webcam(logged_in: Page) -> None:
    ItemListPage(logged_in).open_borrow("Web カメラ")
    due = dt.date.today() + dt.timedelta(days=3)
    logged_in.get_by_role("textbox", name="返す日").fill(due.isoformat())
    logged_in.get_by_role("textbox", name="使う目的").fill("研修で使う")
    logged_in.get_by_role("button", name="貸し出しを登録").click()
    expect(logged_in.get_by_role("status")).to_have_text("Web カメラ の貸し出しを登録しました")


def test_news_quick(logged_in: Page) -> None:
    expect(logged_in.locator("#news")).to_have_text("金曜日の 17 時から、備品の棚卸しをします")


def test_laptop_b_is_borrowed(logged_in: Page) -> None:
    ItemListPage(logged_in).open_borrow("ノートPC B")
    due = dt.date.today() + dt.timedelta(days=3)
    BorrowPage(logged_in).borrow(due.isoformat(), "出張で使う")
    row = logged_in.get_by_role("row", name="ノートPC B")
    expect(row).to_contain_text("貸出中")
