from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")


# --- LOGIN (GİRİŞ) ---
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login_submit(request: Request, email: str = Form(...), password: str = Form(...)):
    # TODO: Backendci arkadaş buraya veritabanı kontrolü yazacak
    print(f"Giriş Denemesi -> Email: {email}, Şifre: {password}")

    # Başarılıysa ilanlara yönlendir
    return RedirectResponse(url="/listings", status_code=303)


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
    # TODO: Backendci arkadaş buraya 'INSERT INTO users...' yazacak
    print(f"Yeni Kayıt -> {first_name} {last_name}, {email}")

    # Kayıt bitince giriş sayfasına at
    return RedirectResponse(url="/auth/login", status_code=303)