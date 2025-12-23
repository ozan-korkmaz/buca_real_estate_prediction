import requests
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import Request, HTTPException, status
import jwt
import os
import urllib.parse  

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET bulunamadi")

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5001/api"

# --- LOGIN SAYFASI (GET) ---
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

# --- LOGIN İŞLEMİ (POST) ---
@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    account_type: str = Form(...)
):
    payload = {
        "email": email,
        "password": password,
        "account_type": account_type
    }

    try:
        response = requests.post(f"{API_URL}/login", json=payload)
        
        if response.status_code == 200:
            data = response.json().get("data", {})
            token = data.get("access_token")
            role = data.get("role")
            
            raw_name = data.get("user_name") or "Kullanıcı"
            
            safe_user_name = urllib.parse.quote(raw_name)

            redirect = RedirectResponse(url="/listings", status_code=303)
            
            redirect.set_cookie("access_token", token, httponly=True)
            redirect.set_cookie("user_role", role)
            redirect.set_cookie("user_name", safe_user_name) # 3. Güvenli ismi yaz
            
            return redirect
        else:
            error_msg = response.json().get("message", "Giriş başarısız")
            return templates.TemplateResponse("auth/login.html", {
                "request": request,
                "error": error_msg
            })

    except Exception as e:
        return templates.TemplateResponse("auth/login.html", {
            "request": request,
            "error": f"Sunucu hatası: {e}"
        })

# --- REGISTER SAYFASI (GET) ---
@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

# --- REGISTER İŞLEMİ (POST) ---
@router.post("/register")
async def register_submit(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    phone: str = Form(...),
    account_type: str = Form(...),

    agency_name: str = Form(None),
    title: str = Form(None),
    address: str = Form(None)
):
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password,
        "phone": phone,
        "account_type": account_type,
        "agency_name": agency_name,
        "title": title,
        "address": address
    }

    try:
        response = requests.post(f"{API_URL}/register", json=payload)
        if response.status_code == 201:
            return RedirectResponse(url="/auth/login?success=Kayit_Basarili", status_code=303)
        else:
            error_msg = response.json().get("message", "Kayıt başarısız")
            return templates.TemplateResponse("auth/register.html", {
                "request": request, 
                "error": error_msg
            })
    except Exception as e:
        return templates.TemplateResponse("auth/register.html", {
            "request": request, 
            "error": f"Hata: {e}"
        })

# --- ÇIKIŞ YAP (LOGOUT) ---
@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie("access_token")
    response.delete_cookie("user_role")
    response.delete_cookie("user_name")
    return response


def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")

    print("JWT_SECRET:", JWT_SECRET)
    print("TOKEN:", token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token bulunamadi"
        )

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token suresi dolmus"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gecersiz token"
        )