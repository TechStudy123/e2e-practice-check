from playwright.sync_api import Page


class ItemListPage:
    def __init__(self, page: Page):
        self.page = page

    def search(self, word):
        self.page.get_by_label("備品をさがす").fill(word)
        self.page.get_by_role("button", name="検索").click()

    def open_borrow(self, name):
        self.page.get_by_role("row", name=name).get_by_role("link", name="借りる").click()
