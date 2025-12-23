from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import httpx 
from .auth import get_current_user 


templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/profile", tags=["profile"])

API_BASE_URL = "http://localhost:5001/api"

@router.get("/")
async def profile_view(
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    token = request.cookies.get("access_token")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        response = await client.get("/users/me", headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yetkilendirme hatasi"
        )

    user_data = response.json()["data"]

    return templates.TemplateResponse(
        "profile/view.html",
        {
            "request": request,
            "current_user": user_data
        }
    )

@router.post("/edit")
async def profile_edit(
    request: Request,
    current_user: dict = Depends(get_current_user),
    name: str = Form(...),
    surname: str = Form(...),
):
    token = request.cookies.get("access_token")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        response = await client.patch(
            "/users/me",
            json={"name": name, "surname": surname},
            headers=headers
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Profil guncellenemedi")

    return RedirectResponse("/profile?msg=Profil_guncellendi", status_code=302)


@router.post("/change-password")
async def change_password(
    request: Request,
    current_user: dict = Depends(get_current_user),
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    user_id = current_user.get("id")
    msg = ""

    if new_password != confirm_password:
        msg = "Yeni şifreler eşleşmiyor."
    elif len(new_password) < 8:
        msg = "Şifre en az 8 karakter olmalıdır."
    else:
        try:
            async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
                response = await client.post(
                    f"/auth/change-password", # Veya API'nizin şifre değiştirme rotası
                    json={
                        "user_id": user_id,
                        "current_password": current_password,
                        "new_password": new_password,
                    }
                )
                response.raise_for_status() 
                msg = "Şifreniz başarıyla değiştirildi. Lütfen tekrar giriş yapın."
                # logout yap
                return RedirectResponse(url="/auth/logout", status_code=status.HTTP_302_FOUND)

        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json().get("detail", f"HTTP Hatası: {e.response.status_code}")
            except:
                error_detail = f"HTTP Hatası: {e.response.status_code}"
            
            msg = f"Şifre değiştirme hatası: {error_detail}"
        except Exception as e:
            msg = f"Bir hata oluştu: {str(e)}"

    # hata tekrar profil sayfasına yönlendir
    return templates.TemplateResponse(
        "profile/view.html",
        {
            "request": request,
            "current_user": current_user, 
            "msg": msg
        }
    )