import requests
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/prediction", tags=["prediction"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5000/api/predict"

@router.get("/estimate")
async def estimate_page(request: Request):
    return templates.TemplateResponse("prediction/form.html", {"request": request})

@router.post("/estimate")
async def estimate_price_result(
        request: Request,
        location: str = Form(...),
        room_count: str = Form(...),
        net_area: int = Form(...),
        floor: int = Form(...),
        building_age: int = Form(...)
):
    # Basit bir parse işlemi (Örn: "3+1" -> 3)
    try:
        room_cnt_num = int(room_count.split("+")[0])
    except:
        room_cnt_num = 1

    payload = {
        "room_count": room_cnt_num,
        "net_area": net_area,
        "floor": floor,
        "building_age": building_age,
        "location_score": 5
    }

    estimated_price = None
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json().get("data", {})
            estimated_price = data.get("predicted_price")
    except Exception as e:
        print(f"Tahmin Hatası: {e}")

    return templates.TemplateResponse("prediction/result.html", {
        "request": request,
        "price": estimated_price,
        "details": payload
    })