import requests
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime

router = APIRouter(prefix="/listings", tags=["listings"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5000/api/listings"


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
async def listing_detail(request: Request, id: int):
    listing = None
    try:
        response = requests.get(f"{API_URL}/{id}")
        if response.status_code == 200:
            listing = response.json().get("data")
    except Exception:
        pass

    if not listing:
        return RedirectResponse(url="/listings")

    return templates.TemplateResponse("listings/detail.html", {
        "request": request,
        "listing": listing
    })