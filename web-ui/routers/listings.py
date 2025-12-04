import requests
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime

router = APIRouter(prefix="/listings", tags=["listings"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5001/api/listings"
AGENTS_API_URL = "http://localhost:5001/api/agents"
COMMENTS_API_URL = "http://localhost:5001/api/comments" # <-- Tanımlandı
USERS_API_URL = "http://localhost:5001/api/users"       # <-- Tanımlandı


# --- 1. LİSTELEME (INDEX) ---
@router.get("/")
async def index_page(request: Request):
    listings = []
    error = None
    try:
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

    headers = {"Authorization": token}
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
    
    try:
        # 1. Listing verisini çek
        response = requests.get(f"{API_URL}/{id}")
        
        # Hata kontrolü: 404 ise HTTP hatası fırlat
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="İlan bulunamadı.")
        
        if response.status_code == 200:
            listing = response.json().get("data")
            
            listing["seller"] = {"name": "Satıcı Bilgisi Yok", "phone": "Yok"}
            listing["comments"] = [] 

            # 2. Agent verisini çekme
            if listing and "agency_id" in listing:
                agency_id_obj = listing["agency_id"]
                agency_id = agency_id_obj.get("$oid") if isinstance(agency_id_obj, dict) else agency_id_obj
                
                if agency_id:
                    try:
                        agent_response = requests.get(f"{AGENTS_API_URL}/{agency_id}")
                        if agent_response.status_code == 200:
                            listing["seller"] = agent_response.json().get("data")
                    except requests.exceptions.RequestException:
                         # SOA/Agent API bağlantısı kapalıysa
                         listing["seller"]["name"] = "Ajans/SOA Servisi Kapalı"
            
            # 3. Yorum verisini çekme
            listing_id_obj = listing["_id"] if "_id" in listing else listing.get("id")
            listing_id = listing_id_obj.get("$oid") if isinstance(listing_id_obj, dict) else listing_id_obj

            if listing_id:
                try:
                    comments_response = requests.get(f"{COMMENTS_API_URL}?listing_id={listing_id}") 
                    
                    if comments_response.status_code == 200:
                        raw_comments = comments_response.json().get("data", [])
                        processed_comments = []
                        
                        for comment in raw_comments:
                            user_name = "Anonim Kullanıcı"
                            user_id_obj = comment.get("user_id")
                            user_id = user_id_obj.get("$oid") if isinstance(user_id_obj, dict) else user_id_obj
                            
                            if user_id:
                                try:
                                    # DEBUG: Kullanıcı API çağrısını ve yanıtını loglayın
                                    print(f"DEBUG: Calling Users API: {USERS_API_URL}/{user_id}")
                                    user_response = requests.get(f"{USERS_API_URL}/{user_id}")
                                    print(f"DEBUG: User Response Status: {user_response.status_code}")
                                    print(f"DEBUG: User Response Data: {user_response.text}")
                                    
                                    if user_response.status_code == 200:
                                        user_data = user_response.json().get("data", {})
                                        user_name = user_data.get("name", "Bilinmeyen Kullanıcı") # <-- 'name' alanını çeker
                                        
                                        print(f"DEBUG: Retrieved User Name: {user_name}") # <-- Log ekleyelim


                                except requests.exceptions.RequestException:
                                    print(f"DEBUG: Users API Connection Error for ID: {user_id}")
                                    pass

                            comment_text = comment.get("content") or comment.get("text") or "Yorum Metni Yok"
                            
                            processed_comments.append({
                                "user": user_name, 
                                "date": comment.get("created_at", "Tarih Yok"), 
                                "content": comment_text, # API'den gelen 'content' veya 'text'i atıyoruz.
                                "rating": comment.get("rating", 0) 
                            })

                        listing["comments"] = processed_comments
                        
                    elif comments_response.status_code != 404:
                        print(f"Yorum API'si HTTP Hatası: {comments_response.status_code}")
                        
                except requests.exceptions.RequestException as e:
                    print(f"Yorum API bağlantı hatası: {e}")

        elif listing is None:
            raise Exception("Listing API'den veri alınamadı.")

    except HTTPException:
        return RedirectResponse(url="/listings?error=Ilan_Bulunamadi", status_code=303)
    except Exception as e:
        print(f"Genel Hata: {e}")
        return templates.TemplateResponse("listings/index.html", {"request": request, "error": f"API Bağlantı Hatası: {e}"})

    if not listing:
        return RedirectResponse(url="/listings", status_code=303)

    return templates.TemplateResponse("listings/detail.html", {
        "request": request,
        "listing": listing
    })