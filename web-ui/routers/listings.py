from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime

router = APIRouter(prefix="/listings", tags=["listings"])
templates = Jinja2Templates(directory="templates")

# --- MOCK VERİTABANI ---
# Gerçek API geldiğinde burası silinecek.
MOCK_LISTINGS = [
    {
        "id": 101,
        "title": "Buca Şirinyer'de Metroya Yakın 3+1",
        "description": "Evimiz güney cephedir, karanlık odası yoktur. Metroya 5 dk yürüme mesafesinde. Aile apartmanı.",
        "price": 3500000,
        "location": "Şirinyer",
        "room_count": "3+1",
        "net_area": 120,
        "gross_area": 135,
        "floor": "3",
        "building_age": "5-10",
        "heating_type": "Doğalgaz (Kombi)",
        "created_at": "2025-10-05",
        "seller": {"name": "Ahmet Yılmaz", "phone": "05551234567"},
        "comments": [
            {"user": "Mehmet K.", "content": "Fiyatı piyasaya göre biraz yüksek ama konumu harika.", "rating": 4,
             "date": "2025-10-07"},
            {"user": "Ayşe D.", "content": "Evi gezdim, fotoğraflardaki gibi temiz.", "rating": 5, "date": "2025-10-08"}
        ]
    },
    {
        "id": 102,
        "title": "Tınaztepe Kampüs Yanı Öğrenci Evi",
        "description": "Üniversiteye yürüme mesafesinde, eşyalı, yatırımlık daire.",
        "price": 1850000,
        "location": "Tınaztepe",
        "room_count": "1+1",
        "net_area": 55,
        "gross_area": 65,
        "floor": "1",
        "building_age": "0-5",
        "heating_type": "Klima",
        "created_at": "2025-10-06",
        "seller": {"name": "Emlak Ofisi", "phone": "05321112233"},
        "comments": []
    }
]


# --- 1. LİSTELEME (INDEX) ---
@router.get("/")
async def index_page(request: Request):
    # Sözleşmeye göre API bize bir liste dönecek
    return templates.TemplateResponse("listings/index.html", {
        "request": request,
        "listings": MOCK_LISTINGS
    })


# --- 2. İLAN VERME SAYFASI (CREATE GET) ---
@router.get("/create")
async def create_listing_page(request: Request):
    # URL'deki parametreleri (price, location vb.) alıyoruz
    prefill_data = request.query_params

    return templates.TemplateResponse("listings/create.html", {
        "request": request,
        "prefill": prefill_data  # Bu veriyi şablona gönderiyoruz
    })


# --- 3. İLAN KAYDETME (CREATE POST) ---
@router.post("/create")
async def create_listing_submit(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        price: int = Form(...),
        location: str = Form(...),
        room_count: str = Form(...),
        net_area: int = Form(...),
        gross_area: int = Form(...),
        floor: str = Form(...),
        building_age: str = Form(...),
        heating_type: str = Form(...)
):
    # Yeni ilanı oluştur (Sanki API'ye JSON atıyormuşuz gibi)
    new_listing = {
        "id": len(MOCK_LISTINGS) + 101,
        "title": title,
        "description": description,
        "price": price,
        "location": location,
        "room_count": room_count,
        "net_area": net_area,
        "gross_area": gross_area,
        "floor": floor,
        "building_age": building_age,
        "heating_type": heating_type,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "seller": {"name": "Ozan Korkmaz", "phone": "05001234567"},  # Auth gelince user'dan alınacak
        "comments": []
    }

    MOCK_LISTINGS.append(new_listing)
    print(f"Yeni İlan Eklendi: {title}")

    return RedirectResponse(url="/listings", status_code=303)


# --- 4. İLAN DETAY (DETAIL) ---
@router.get("/{id}")
async def listing_detail(request: Request, id: int):
    # Mock veritabanında ID'ye göre arama yapıyoruz
    listing = next((item for item in MOCK_LISTINGS if item["id"] == id), None)

    if not listing:
        return RedirectResponse(url="/listings")

    return templates.TemplateResponse("listings/detail.html", {
        "request": request,
        "listing": listing
    })