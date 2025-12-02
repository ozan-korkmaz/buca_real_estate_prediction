from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/listings", tags=["listings"])
templates = Jinja2Templates(directory="templates")


# --- LISTELEME (INDEX) ---
@router.get("/")
async def index_page(request: Request):
    # TODO: Backendci burayı veritabanından çekecek (SELECT * FROM listings)
    # Biz şimdilik 'Mock Data' (Sahte Veri) ile önizleme yapıyoruz
    mock_listings = [
        {"id": 1, "title": "Buca Merkezde Lüks Daire", "price": "3.500.000", "location": "Buca Merkez", "rooms": "3+1",
         "area": 120, "floor": 3},
        {"id": 2, "title": "Şirinyer Metro Yakını", "price": "2.850.000", "location": "Şirinyer", "rooms": "2+1",
         "area": 95, "floor": 1},
        {"id": 3, "title": "Tınaztepe Öğrenciye Uygun", "price": "1.950.000", "location": "Tınaztepe", "rooms": "1+1",
         "area": 60, "floor": 5},
    ]
    return templates.TemplateResponse("listings/index.html", {"request": request, "listings": mock_listings})


# --- İLAN VERME (CREATE) ---
@router.get("/create")
async def create_listing_page(request: Request):
    return templates.TemplateResponse("listings/create.html", {"request": request})


@router.post("/create")
async def create_listing_submit(
        request: Request,
        title: str = Form(...),
        price: int = Form(...),
        location: str = Form(...),
        room_count: str = Form(...),
        net_area: int = Form(...),
        description: str = Form(...)
):
    # TODO: Backendci buraya İlan Kaydetme (INSERT) kodunu yazacak
    print(f"Yeni İlan -> Başlık: {title}, Fiyat: {price}")

    # İlan eklenince listeye geri dön
    return RedirectResponse(url="/listings", status_code=303)