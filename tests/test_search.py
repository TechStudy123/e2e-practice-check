from playwright.sync_api import Page, expect

from pages.item_list_page import ItemListPage


def test_search_pc(logged_in: Page) -> None:
    ItemListPage(logged_in).search("PC")
    expect(logged_in.get_by_test_id("item-count")).to_have_text("2 件")
