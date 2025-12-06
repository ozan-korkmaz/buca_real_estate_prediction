import requests
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/prediction", tags=["prediction"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5001/api/predict"

@router.get("/estimate")
async def estimate_page(request: Request):
    user_role = request.cookies.get("user_role")
    token = request.cookies.get("access_token")
    if not token: return RedirectResponse(url="/auth/login", status_code=303)
    if user_role != 'agent': return RedirectResponse(url="/listings?error=Yetkisiz_Erisim", status_code=303)
    return templates.TemplateResponse("prediction/form.html", {"request": request})

@router.post("/estimate")
async def estimate_price_result(
        request: Request,
        location: str = Form(...),
        room_count: int = Form(...),
        hall_count: int = Form(...),       # Yeni: Salon
        bathroom_count: int = Form(...),   # Yeni: Banyo
        net_area: float = Form(...),
        floor: int = Form(...),
        total_floors: int = Form(...),     # Yeni: Toplam Kat
        building_age: int = Form(...),
        heating_type: str = Form(...),     # Yeni: Isıtma
        furnishing: str = Form(...),       # Yeni: Eşya
        usage_status: str = Form(...)      # Yeni: Kullanım
):
    user_role = request.cookies.get("user_role")
    if user_role != 'agent': return RedirectResponse(url="/listings", status_code=303)

    # ML Servisinin beklediği genişletilmiş payload
    payload = {
        "room_count": room_count,
        "hall_count": hall_count,
        "net_area": net_area,
        "floor": floor,
        "total_floors": total_floors,
        "building_age": building_age,
        "bathroom_count": bathroom_count,
        "location": location,          # "buca-koop" vb.
        "heating_type": heating_type,  # "kombi" vb.
        "furnishing": furnishing,      # "furnished" / "unfurnished"
        "usage_status": usage_status   # "empty" / "owner"
    }

    estimated_price = None
    price_range = None

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json().get("data", {})
            estimated_price = data.get("predicted_price")
            price_range = data.get("price_range")
        else:
            print(f"API Hatası: {response.text}")
    except Exception as e:
        print(f"Tahmin Hatası: {e}")

    return templates.TemplateResponse("prediction/result.html", {
        "request": request,
        "price": estimated_price,
        "range": price_range,
        "details": payload
    })