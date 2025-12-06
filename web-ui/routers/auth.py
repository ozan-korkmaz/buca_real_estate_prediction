import requests
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5001/api"


# ---------- LOGIN SAYFASI ----------
@router.get("/login")
async def login_page(request: Request):
    msg = request.query_params.get("msg")
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "msg": msg, "error": None}
    )


# ---------- LOGIN SUBMIT ----------
@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    account_type: str = Form(...)
):
    # Node'a gönderilecek payload
    payload = {
        "email": email,
        "password": password,
        "account_type": account_type
    }

    try:
        resp = requests.post(f"{API_URL}/login", data=payload)
    except Exception as e:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": f"API bağlantı hatası: {e}", "msg": None}
        )

    if resp.status_code == 200:
        data = resp.json().get("data", {})
        token = data.get("access_token")
        role = data.get("role")
        user_name = data.get("user_name")

        # Giriş başarılı → listings'e yönlendir
        redirect = RedirectResponse(url="/listings", status_code=303)

        if token:
            redirect.set_cookie("access_token", f"Bearer {token}", httponly=True)
        if role:
            redirect.set_cookie("user_role", role)
        if user_name:
            redirect.set_cookie("user_name", user_name)

        return redirect

    # Hatalı giriş
    try:
        err_msg = resp.json().get("message", "Giriş başarısız.")
    except Exception:
        err_msg = f"Giriş başarısız: {resp.text}"

    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "error": err_msg, "msg": None}
    )


# ---------- REGISTER SAYFASI ----------
@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "error": None}
    )


# ---------- REGISTER SUBMIT ----------
@router.post("/register")
async def register_submit(request: Request):
    form = await request.form()

    payload = {
        "first_name": form.get("first_name"),
        "last_name": form.get("last_name"),
        "email": form.get("email"),
        "password": form.get("password"),
        "phone": form.get("phone"),
        "account_type": form.get("account_type"),
        "agency_name": form.get("agency_name"),
        "title": form.get("title"),
        "address": form.get("address"),
    }

    try:
        resp = requests.post(f"{API_URL}/register", data=payload)
    except Exception as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": f"API bağlantı hatası: {e}"}
        )

    if resp.status_code == 201:
        return RedirectResponse(
            url="/auth/login?msg=Kayit_Basarili_Lutfen_Giris_Yapin",
            status_code=303
        )

    try:
        err_msg = resp.json().get("message", "Kayıt işlemi başarısız.")
    except Exception:
        err_msg = f"Kayıt işlemi başarısız: {resp.text}"

    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request, "error": err_msg}
    )
