import requests
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime
import json
import base64

router = APIRouter(prefix="/listings", tags=["listings"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5001/api/listings"
AGENTS_API_URL = "http://localhost:5001/api/agents"
COMMENTS_API_URL = "http://localhost:5001/api/comments"
USERS_API_URL = "http://localhost:5001/api/users"


# --- TOKEN ÇÖZÜMLEME FONKSİYONU ---
def decode_token(token: str):
    """Token'ı çözer ve payload'u döndürür. Hata durumunda None."""
    try:
        if token.startswith("Bearer "):
            token = token[7:]
            
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        payload_base64 = parts[1] 
        padding = len(payload_base64) % 4
        if padding > 0:
            payload_base64 += '=' * (4 - padding)
            
        payload_bytes = base64.urlsafe_b64decode(payload_base64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        return payload
    except Exception as e:
        print(f"ERROR: Token çözme hatası: {e}")
        return None

# --- MAHALLE VERİSİ ---
def load_neighborhoods():
    return [
        {"_id": {"$oid": "692edc7ba7b9834d54d6aa5c"}, "name": "Adatepe Mahallesi"},
        {"_id": {"$oid": "692edd34a7b9834d54d6aa60"}, "name": "Tınaztepe Mahallesi"},
        {"_id": {"$oid": "692edd46a7b9834d54d6aa61"}, "name": "Efeler Mahallesi"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0967"}, "name": "Adatepe Mahallesi (Tekrar)"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0989"}, "name": "Yıldız Mahallesi"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0981"}, "name": "Şirinyer Mahallesi"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0980"}, "name": "Buca Merkez"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0986"}, "name": "Yenigün Mahallesi"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0987"}, "name": "Yeşilbağlar Mahallesi"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0988"}, "name": "Yeşilçam Mahallesi"},
    ]


# --- 1. LİSTELEME (INDEX) - GÜNCELLENDİ ---
@router.get("/")
async def index_page(request: Request):
    listings = []
    error = None
    
    # Kullanıcı rolünü alıyoruz ki template'e gönderebilelim
    user_role = request.cookies.get("user_role")

    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            listings = response.json().get("data", [])
        else:
            error = "İlanlar getirilemedi"
    except Exception as e:
        error = f"API hatası: {e}"

    return templates.TemplateResponse("listings/index.html",{
        "request": request,
        "listings": listings,
        "error": error,
        "user_role": user_role  # <-- Rol bilgisini template'e gönderdik
    })


# --- 2. İLAN VERME SAYFASI (CREATE GET) ---
@router.get("/create")
async def create_listing_page(request: Request):
    token = request.cookies.get("access_token")
    user_role = request.cookies.get("user_role")

    # GÜVENLİK KONTROLLERİ
    if not token:
        return RedirectResponse(url="/auth/login?msg=Ilan_vermek_icin_giris_yapin", status_code=303)
    
    if user_role != 'agent':
        return RedirectResponse(url="/listings?error=Yetkisiz_Erisim_Sadece_Emlakcilar_Ilan_Verebilir", status_code=303)

    prefill_data = request.query_params
    neighborhoods = load_neighborhoods() 
    
    return templates.TemplateResponse("listings/create.html", {
        "request": request,
        "prefill": prefill_data,
        "neighborhoods": neighborhoods
    })


# --- 3. İLAN KAYDETME (CREATE POST) ---
@router.post("/create")
async def create_listing_submit(
        request: Request,
        title: str = Form(...),
        description: str = Form(...),
        price: int = Form(...),
        neighborhood_id: str = Form(..., alias="location"), 
        room_count: str = Form(...),
        net_area: int = Form(...),
        gross_area: int = Form(...),
        floor: str = Form(...),
        building_age: str = Form(...),
        heating_type: str = Form(...)
):
    token = request.cookies.get("access_token")
    user_role = request.cookies.get("user_role")

    # GÜVENLİK
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    if user_role != 'agent':
        return RedirectResponse(url="/listings?error=Yetkisiz_Islem", status_code=303)

    decoded_token = decode_token(token)
    if not decoded_token:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    user_id = decoded_token.get("sub") or decoded_token.get("id")
    if not user_id:
        return RedirectResponse(url="/auth/login?error=InvalidTokenID", status_code=303)

    neighborhoods_data = load_neighborhoods()
    if not neighborhood_id:
        error_message = "Mahalle seçimi zorunludur."
        prefill_data = {
            "title": title, "description": description, "price": price, 
            "location": neighborhood_id, "room_count": room_count, "net_area": net_area,
            "gross_area": gross_area, "floor": floor, "building_age": building_age,
            "heating_type": heating_type
        }
        return templates.TemplateResponse("listings/create.html", {
            "request": request, 
            "prefill": prefill_data, 
            "error": error_message,
            "neighborhoods": neighborhoods_data
        })
    
    neighborhood_name = "Bilinmeyen Mahalle" 
    for n in neighborhoods_data:
        if n.get('_id', {}).get('$oid') == neighborhood_id:
            neighborhood_name = n.get('name', 'Bilinmeyen Mahalle')
            break
            
    current_time_utc_iso = datetime.utcnow().isoformat() + "Z"
    headers = {"Authorization": token}
    payload = {
        "agency_id": user_id, 
        "title": title,
        "description": description,
        "price": price,
        "neighborhood_id": neighborhood_id, 
        "property_specs": {
            "room_count": room_count,
            "net_m2": net_area,
            "gross_m2": gross_area,
            "floor": floor,
            "heating": heating_type,
            "building_age": building_age 
        },
        "location_details": {
            "street_name": neighborhood_name, 
            "coordinates": {"lat": 0, "lon": 0}
        },
        "created_at": current_time_utc_iso
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return RedirectResponse(url="/listings", status_code=303)
        else:
            error_response_text = response.text
            prefill_data = {
                "title": title, "description": description, "price": price, 
                "location": neighborhood_id, "room_count": room_count, "net_area": net_area,
                "gross_area": gross_area, "floor": floor, "building_age": building_age,
                "heating_type": heating_type
            }
            try:
                error_detail = response.json().get('message', error_response_text)
            except json.JSONDecodeError:
                error_detail = error_response_text
            error_message = f"İlan eklenemedi: {error_detail}"
            
            return templates.TemplateResponse("listings/create.html", {
                "request": request, 
                "prefill": prefill_data, 
                "error": error_message,
                "neighborhoods": neighborhoods_data 
            })
    except Exception as e:
        return templates.TemplateResponse("listings/create.html", {"request": request, "error": "Sunucuya bağlantı hatası"})
    

def standardize_phone_data(data: dict) -> dict:
    phone_number = data.get("phone")
    if not isinstance(phone_number, str) or not phone_number.strip():
        data["phone"] = "Numara Yok (API Sorunu)"
    return data

# --- 4. İLAN DETAY (DETAIL) ---
@router.get("/{id}")
async def listing_detail(request: Request, id: str):
    
    # GÜVENLİK
    token = request.cookies.get("access_token")
    if not token:
         return RedirectResponse(url="/auth/login?msg=Detaylari_gormek_icin_giris_yapmalisiniz", status_code=303)

    listing = None
    current_user_id = None
    user_role = request.cookies.get("user_role")

    if token:
        decoded = decode_token(token)
        if decoded:
             current_user_id = decoded.get("sub") or decoded.get("id")

    try:
        response = requests.get(f"{API_URL}/{id}")
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="İlan bulunamadı.")
        
        if response.status_code == 200:
            listing = response.json().get("data")
            listing["seller"] = {"name": "Satıcı Bilgisi Yok", "phone": "Numara Yok"}
            listing["seller_type"] = "unknown"
            listing["comments"] = [] 

            seller_found = False
            user_ref = listing.get("user")
            if user_ref:
                user_ref_id = user_ref.get("$oid") if isinstance(user_ref, dict) else user_ref
                if user_ref_id:
                    try:
                        user_response = requests.get(f"{USERS_API_URL}/{user_ref_id}")
                        if user_response.status_code == 200:
                            user_data = user_response.json().get("data", {})
                            user_data = standardize_phone_data(user_data)
                            listing["seller"] = user_data 
                            listing["seller_type"] = "user"
                            seller_found = True
                    except requests.exceptions.RequestException:
                        pass

            if not seller_found and "agency_id" in listing:
                agency_id_obj = listing["agency_id"]
                agency_ref_id = agency_id_obj.get("$oid") if isinstance(agency_id_obj, dict) else agency_id_obj
                
                if agency_ref_id:
                    try:
                        agent_response = requests.get(f"{AGENTS_API_URL}/{agency_ref_id}")
                        if agent_response.status_code == 200:
                            agent_data = agent_response.json().get("data", {})
                            agent_data = standardize_phone_data(agent_data)
                            listing["seller"] = agent_data 
                            listing["seller_type"] = "agency"
                            listing["agency_id_str"] = agency_ref_id 
                            seller_found = True
                        else:
                            try:
                                user_response = requests.get(f"{USERS_API_URL}/{agency_ref_id}")
                                if user_response.status_code == 200:
                                    user_data = user_response.json().get("data", {})
                                    user_data = standardize_phone_data(user_data)
                                    listing["seller"] = user_data
                                    listing["seller_type"] = "user"
                                    seller_found = True
                            except requests.exceptions.RequestException:
                                pass
                    except requests.exceptions.RequestException:
                        pass
            
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
                                    user_response = requests.get(f"{USERS_API_URL}/{user_id}")
                                    if user_response.status_code == 200:
                                        user_data = user_response.json().get("data", {})
                                        user_name = user_data.get("name", "Bilinmeyen Kullanıcı")
                                except requests.exceptions.RequestException:
                                    pass
                            comment_text = comment.get("content") or comment.get("text") or "Yorum Metni Yok"
                            processed_comments.append({
                                "user": user_name, 
                                "date": comment.get("created_at", "Tarih Yok"), 
                                "content": comment_text,
                                "rating": comment.get("rating", 0) 
                            })
                        listing["comments"] = processed_comments
                except requests.exceptions.RequestException:
                    pass

        elif listing is None:
            raise Exception("Listing API'den veri alınamadı.")

    except HTTPException:
        return RedirectResponse(url="/listings?error=Ilan_Bulunamadi", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("listings/index.html", {"request": request, "error": f"API Bağlantı Hatası: {e}"})

    if not listing:
        return RedirectResponse(url="/listings", status_code=303)

    return templates.TemplateResponse("listings/detail.html", {
        "request": request,
        "listing": listing,
        "user_role": user_role,
        "current_user_id": current_user_id
    })