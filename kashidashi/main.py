"""備品の貸し出しアプリ（E2E テストの練習用の題材）。

起動: uv run uvicorn kashidashi.main:app --port 8000
ログイン: ユーザー名 tanaka／パスワード renshu-1234（練習用）
"""
import asyncio
import datetime as dt
import html
import random
import secrets

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

app = FastAPI(title="備品の貸し出し")

USERS = {"tanaka": "renshu-1234", "suzuki": "renshu-5678"}
SESSIONS: dict[str, str] = {}

FIRST_ITEMS = [
    {"id": 1, "name": "ノートPC A", "kind": "PC", "borrower": None, "due": None},
    {"id": 2, "name": "ノートPC B", "kind": "PC", "borrower": None, "due": None},
    {"id": 3, "name": "プロジェクター", "kind": "映像", "borrower": None, "due": None},
    {"id": 4, "name": "Web カメラ", "kind": "映像", "borrower": None, "due": None},
    {"id": 5, "name": "延長コード", "kind": "その他", "borrower": None, "due": None},
]
ITEMS: list[dict] = []


def reset_items() -> None:
    ITEMS.clear()
    ITEMS.extend(dict(x) for x in FIRST_ITEMS)


reset_items()


def page(title: str, body: str, user: str | None = None) -> HTMLResponse:
    nav = ""
    if user:
        nav = (f'<nav><span id="user-name">{html.escape(user)} さん</span> '
               '<form method="post" action="/logout" class="inline"><button>ログアウト</button></form></nav>')
    return HTMLResponse(f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><title>{html.escape(title)} | 備品の貸し出し</title>
<style>
body{{font-family:Meiryo,"Hiragino Sans",sans-serif;margin:24px;max-width:860px}}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #bbb;padding:6px 10px;text-align:left}}
.inline{{display:inline}} .error{{color:#b00020}} .ok{{color:#05631f}} label{{display:block;margin:8px 0}}
nav{{float:right}}
</style></head>
<body>{nav}<h1>{html.escape(title)}</h1>
{body}
</body></html>""")


def current_user(request: Request) -> str | None:
    return SESSIONS.get(request.cookies.get("session", ""))


@app.get("/login", response_class=HTMLResponse)
def login_form(error: str = ""):
    msg = '<p role="alert" class="error">ユーザー名かパスワードが違います</p>' if error else ""
    return page("ログイン", f"""{msg}
<form method="post" action="/login">
<label>ユーザー名 <input name="username" autocomplete="username"></label>
<label>パスワード <input name="password" type="password" autocomplete="current-password"></label>
<button>ログイン</button>
</form>""")


@app.post("/login")
def login(username: str = Form(""), password: str = Form("")):
    if USERS.get(username) != password or not password:
        return RedirectResponse("/login?error=1", status_code=303)
    token = secrets.token_hex(16)
    SESSIONS[token] = username
    r = RedirectResponse("/", status_code=303)
    r.set_cookie("session", token, httponly=True)
    return r


@app.post("/logout")
def logout(request: Request):
    SESSIONS.pop(request.cookies.get("session", ""), None)
    r = RedirectResponse("/login", status_code=303)
    r.delete_cookie("session")
    return r


@app.get("/", response_class=HTMLResponse)
def index(request: Request, q: str = "", done: str = ""):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    rows = []
    for it in ITEMS:
        if q and q not in it["name"] and q not in it["kind"]:
            continue
        if it["borrower"]:
            state = f'貸出中（{html.escape(it["borrower"])}・{it["due"]} まで）'
            action = ""
        else:
            state = "貸出できます"
            action = f'<a href="/items/{it["id"]}/borrow">借りる</a>'
        rows.append(f'<tr><td>{html.escape(it["name"])}</td><td>{html.escape(it["kind"])}</td>'
                    f'<td>{state}</td><td>{action}</td></tr>')
    count = len(rows)
    flash = f'<p role="status" class="ok">{html.escape(done)} を貸し出しました</p>' if done else ""
    body = f"""{flash}
<form method="get" action="/" role="search">
<label>備品をさがす <input name="q" value="{html.escape(q)}" placeholder="名前か種類"></label>
<button>検索</button>
</form>
<table><caption>備品の一覧</caption>
<thead><tr><th>名前</th><th>種類</th><th>状態</th><th>操作</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<p data-testid="item-count">{count} 件</p>
<section aria-labelledby="news-h"><h2 id="news-h">お知らせ</h2>
<p id="news">読み込み中…</p></section>
<script>
fetch('/api/news').then(r => r.json()).then(j => {{ document.getElementById('news').textContent = j.text; }});
</script>"""
    return page("備品の一覧", body, user)


@app.get("/items/{item_id}/borrow", response_class=HTMLResponse)
def borrow_form(request: Request, item_id: int, error: str = ""):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    it = next((x for x in ITEMS if x["id"] == item_id), None)
    if it is None:
        return page("見つかりません", "<p>その備品はありません</p>", user)
    msg = f'<p role="alert" class="error">{html.escape(error)}</p>' if error else ""
    return page(f"{it['name']} を借りる", f"""{msg}
<form method="post" action="/items/{item_id}/borrow">
<label>返す日 <input name="due" type="date"></label>
<label>使う目的 <input name="purpose" placeholder="例: 会議で使う"></label>
<button>貸し出しを登録</button>
</form>
<p><a href="/">一覧に戻る</a></p>""", user)


@app.post("/items/{item_id}/borrow")
def borrow(request: Request, item_id: int, due: str = Form(""), purpose: str = Form("")):
    user = current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=303)
    it = next((x for x in ITEMS if x["id"] == item_id), None)
    if it is None or it["borrower"]:
        return RedirectResponse(f"/items/{item_id}/borrow?error=この備品は貸出中です", status_code=303)
    try:
        d = dt.date.fromisoformat(due)
    except ValueError:
        return RedirectResponse(f"/items/{item_id}/borrow?error=返す日を入力してください", status_code=303)
    if d < dt.date.today():
        return RedirectResponse(f"/items/{item_id}/borrow?error=返す日は今日以降にしてください", status_code=303)
    if not purpose.strip():
        return RedirectResponse(f"/items/{item_id}/borrow?error=使う目的を入力してください", status_code=303)
    it["borrower"], it["due"] = user, d.isoformat()
    return RedirectResponse(f"/?done={it['name']}", status_code=303)


@app.get("/api/news")
async def news():
    await asyncio.sleep(random.uniform(1.0, 2.0))  # わざと遅らせる（約1.5秒。毎回少し変わる。自動の待ちの練習）
    return {"text": "金曜日の 17 時から、備品の棚卸しをします"}


@app.get("/api/items")
def api_items():
    return ITEMS


@app.post("/api/items/{item_id}/borrow")
def api_borrow(item_id: int, payload: dict):
    it = next((x for x in ITEMS if x["id"] == item_id), None)
    if it is None:
        return JSONResponse({"error": "not found"}, status_code=404)
    it["borrower"], it["due"] = payload.get("borrower", "tanaka"), payload.get("due", dt.date.today().isoformat())
    return it


@app.post("/api/reset")
def api_reset():
    reset_items()
    return {"ok": True}
