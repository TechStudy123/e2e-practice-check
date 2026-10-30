from playwright.sync_api import Page, expect


def test_borrowed_item_is_shown(logged_in: Page) -> None:
    logged_in.request.post("/api/items/2/borrow", data={"borrower": "suzuki", "due": "2099-12-31"})  # 1. API で用意
    logged_in.goto("/")  # 2. 画面を開き直す
    row = logged_in.get_by_role("row").filter(has_text="ノートPC B")
    expect(row).to_contain_text("貸し出し中")  # 3. 確かめる


def test_webcam_borrowed_by_suzuki(logged_in: Page) -> None:
    logged_in.request.post("/api/items/4/borrow", data={"borrower": "suzuki", "due": "2099-12-31"})
    logged_in.goto("/")
    row = logged_in.get_by_role("row").filter(has_text="Web カメラ")
    expect(row).to_contain_text("貸出中（suzuki")
