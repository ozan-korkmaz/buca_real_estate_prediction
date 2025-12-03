from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/prediction", tags=["prediction"])
templates = Jinja2Templates(directory="templates")


@router.get("/estimate")
async def estimate_page(request: Request):
    return templates.TemplateResponse("prediction/form.html", {"request": request})


@router.post("/estimate")
async def estimate_price_result(
        request: Request,
        location: str = Form(...),
        room_count: str = Form(...),
        net_area: int = Form(...),
        gross_area: int = Form(...),
        floor: str = Form(...),
        building_age: str = Form(...),
        heating_type: str = Form(...)
):
    # --- MOCK ML MODELİ ---
    # Gerçek model gelene kadar basit bir matematik yapalım
    base_price = 1500000

    # Oda sayısı katsayısı
    room_multipliers = {"1+1": 1.0, "2+1": 1.2, "3+1": 1.4, "4+1": 1.6}
    room_mult = room_multipliers.get(room_count, 1.0)

    # Konum katsayısı
    loc_multipliers = {"Buca Merkez": 1.0, "Şirinyer": 1.3, "Tınaztepe": 0.9, "Yıldız": 1.1, "Hasanağa": 1.05}
    loc_mult = loc_multipliers.get(location, 1.0)

    # Hesaplama
    estimated_price = (base_price * room_mult * loc_mult) + (net_area * 15000)

    # Verileri geri döndür (İlan Ver butonuna basınca taşımak için)
    input_data = {
        "location": location,
        "room_count": room_count,
        "net_area": net_area,
        "gross_area": gross_area,
        "floor": floor,
        "building_age": building_age,
        "heating_type": heating_type
    }

    return templates.TemplateResponse("prediction/form.html", {
        "request": request,
        "result": int(estimated_price),
        "input": input_data
    })