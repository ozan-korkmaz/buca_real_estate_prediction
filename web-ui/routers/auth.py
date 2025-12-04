import requests
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")
API_URL = "http://localhost:5001/api"

# --- LOGIN (GİRİŞ) ---
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    payload = {"email": email, "password": password}

    try:
        response = requests.post(f"{API_URL}/login",json=payload)

        if response.status_code == 200:
            data = response.json()
            token = data.get("data", {}).get("access_token")

            redirect = RedirectResponse(url="/listings", status_code=303)
            redirect.set_cookie(key="access_token", value=f"Bearer {token}",httponly=True)
            return redirect
        else:
            error_msg = response.json().get("message","Giriş başarısız!")
            return templates.TemplateResponse("auth/login.html", {"request": request, "error": error_msg})
    except Exception as e:
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": f"Sunucu hatası: {e}"})


# --- REGISTER (KAYIT) ---
@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register_submit(
        request: Request,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(...),
        password: str = Form(...)
):
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }

    try:
        response = requests.post(f"{API_URL}/register",json=payload)
        if response.status_code == 200:
            return RedirectResponse(url="/auth/login",status_code=303)

        else:
            error_msg = response.json().get("message","Kayıt yapılamadı!")
            return templates.TemplateResponse("auth/register.html", {"request": request, "error": error_msg})
    except Exception as e:
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": f"Bağlantı hatası: {e}"})