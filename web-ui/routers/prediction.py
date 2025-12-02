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
        room_count: int = Form(...),
        net_area: int = Form(...)
):
    # TODO: Burası SOA/ML servisine istek atacak
    # Şimdilik rastgele bir mantıkla fiyat uyduruyoruz ki arayüz dolsun
    base_price = 1500000
    estimated_price = base_price + (room_count * 500000) + (net_area * 15000)

    return templates.TemplateResponse("prediction/form.html", {
        "request": request,
        "result": estimated_price,
        "input": {"location": location, "room_count": room_count, "net_area": net_area}
    })