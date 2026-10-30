import datetime as dt

from playwright.sync_api import Page, expect

from pages.borrow_page import BorrowPage
from pages.item_list_page import ItemListPage


def test_borrow_projector(logged_in: Page) -> None:
    ItemListPage(logged_in).open_borrow("プロジェクター")
    due = dt.date.today() + dt.timedelta(days=3)
    BorrowPage(logged_in).borrow(due.isoformat(), "会議で使う")
    expect(logged_in.get_by_role("status")).to_have_text("プロジェクター を貸し出しました")
    expect(logged_in.get_by_role("row", name="プロジェクター")).to_contain_text("貸出中")


def test_borrow_yesterday(logged_in: Page) -> None:
    ItemListPage(logged_in).open_borrow("延長コード")
    yesterday = dt.date.today() - dt.timedelta(days=1)
    BorrowPage(logged_in).borrow(yesterday.isoformat(), "会議で使う")
    expect(logged_in.get_by_role("alert")).to_have_text("返す日は今日以降にしてください")
