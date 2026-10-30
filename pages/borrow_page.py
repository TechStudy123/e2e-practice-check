from playwright.sync_api import Page


class BorrowPage:
    def __init__(self, page: Page):
        self.page = page

    def borrow(self, due, purpose):
        self.page.get_by_role("textbox", name="返す日").fill(due)
        self.page.get_by_role("textbox", name="使う目的").fill(purpose)
        self.page.get_by_role("button", name="貸し出しを登録").click()
