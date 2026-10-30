from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def login(self, user, password):
        self.page.get_by_label("ユーザー名").fill(user)
        self.page.get_by_label("パスワード").fill(password)
        self.page.get_by_role("button", name="ログイン").click()
