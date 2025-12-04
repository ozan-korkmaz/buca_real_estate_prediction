import requests
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime

router = APIRouter(prefix="/listings", tags=["listings"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5001/api/listings"
AGENTS_API_URL = "http://localhost:5001/api/agents"


# --- 1. LİSTELEME (INDEX) ---
@router.get("/")
async def index_page(request: Request):
    listings = []
    error = None
    try:
        #GET isteği
        response = requests.get(API_URL)
        if response.status_code == 200:
            listings = response.json().get("data", [])
        else:
            error = "İlanlar getirilemedi"
    except Exception as e:
        error = f"API hatası: {e}"
    return templates.TemplateResponse("listings/index.html",{
        "request":request,
        "listings": listings,
        "error": error
    })


# --- 2. İLAN VERME SAYFASI (CREATE GET) ---
@router.get("/create")
async def create_listing_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login")

    prefill_data = request.query_params
    return templates.TemplateResponse("listings/create.html", {
        "request": request,
        "prefill": prefill_data
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
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)

    headers = {"Authorization": token}  # Cookie zaten "Bearer <token>" formatında kaydedilmişti
    payload = {
        "title": title,
        "description": description,
        "price": price,
        "location": location,
        "building_age": building_age,
        "property_specs": {
            "room_count": room_count,
            "net_m2": net_area,
            "gross_m2": gross_area,
            "floor": floor,
            "heating": heating_type
        },
        # Location details zorunlu ise dummy veri veya formdan ek veri eklenebilir
        "location_details": {
            "street_name": location,
            "coordinates": {"lat": 0, "lon": 0}
        }
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return RedirectResponse(url="/listings", status_code=303)
        else:
            print("Hata:", response.text)
            return templates.TemplateResponse("listings/create.html", {"request": request, "error": "İlan eklenemedi"})
    except Exception as e:
        print("Exception:", e)
        return templates.TemplateResponse("listings/create.html", {"request": request, "error": "Sunucu hatası"})

# --- 4. İLAN DETAY (DETAIL) ---
@router.get("/{id}")
async def listing_detail(request: Request, id: str):
    listing = None
    
    # Not: API call fails if SOA is down or Agent data is not set up correctly.
    try:
        # 1. Listing verisini çek
        response = requests.get(f"{API_URL}/{id}")
        if response.status_code == 200:
            listing = response.json().get("data")
            
            # 2. Agent ID varsa, Agent (Satıcı) verisini çek ve ekle
            if listing and "agency_id" in listing:
                agency_id_obj = listing["agency_id"]
                # MongoDB ObjectId yapısından string ID'yi al
                agency_id = agency_id_obj.get("$oid") if isinstance(agency_id_obj, dict) else agency_id_obj
                
                # listing["seller"]'ı varsayılan olarak tanımla
                listing["seller"] = {"name": "Ajans/Satıcı Bilgisi Eksik", "phone": "Yok"} 

                if agency_id:
                    try:
                        agent_response = requests.get(f"{AGENTS_API_URL}/{agency_id}")
                        if agent_response.status_code == 200:
                            agent_data = agent_response.json().get("data")
                            # Agent verisini, frontend'in beklediği 'seller' alanına ekle
                            listing["seller"] = agent_data
                        elif agent_response.status_code == 404:
                            listing["seller"] = {"name": "Ajans/Satıcı Bulunamadı (404)", "phone": "Yok"}
                        else:
                            # Diğer HTTP hataları
                            listing["seller"] = {"name": f"Ajans/Satıcı API Hatası ({agent_response.status_code})", "phone": "Yok"}
                    except requests.exceptions.RequestException as e:
                        # Network veya bağlantı hatası (SOA kapalı)
                        print(f"Agent API bağlantı hatası (SOA kapalı?): {e}")
                        listing["seller"] = {"name": "Ajans/SOA Servisi Kapalı", "phone": "Yok"}

        elif response.status_code == 404:
            # İlan bulunamadı hatası (opsiyonel olarak bir hata şablonu oluşturulabilir)
            raise HTTPException(status_code=404, detail="İlan bulunamadı.")

    except HTTPException:
        # 404 hatasını yakala ve yönlendir
        return templates.TemplateResponse("error.html", {"request": request, "error": "İlan Bulunamadı"}, status_code=404)
    except Exception as e:
        # Genel hata (API bağlantısı kesik vb.)
        print(f"Genel Hata: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "error": f"API bağlantı hatası: {e}"}, status_code=500)

    if not listing:
        return RedirectResponse(url="/listings", status_code=303)

    return templates.TemplateResponse("listings/detail.html", {
        "request": request,
        "listing": listing
    })