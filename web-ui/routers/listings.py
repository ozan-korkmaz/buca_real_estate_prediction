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

# ... (Token fonksiyonları aynı kalacak) ...
def decode_token(token: str):
    try:
        if token.startswith("Bearer "): token = token[7:]
        parts = token.split('.')
        if len(parts) != 3: return None
        payload_bytes = base64.urlsafe_b64decode(parts[1] + '=' * (4 - len(parts[1]) % 4))
        return json.loads(payload_bytes.decode('utf-8'))
    except: return None

def standardize_phone_data(data: dict) -> dict:
    phone = data.get("phone")
    if not isinstance(phone, str) or not phone.strip(): data["phone"] = "Numara Yok"
    return data

# --- MAHALLE VERİSİ ---
def load_neighborhoods():
    return [
        {"_id": {"$oid": "692edc7ba7b9834d54d6aa5c"}, "name": "Adatepe Mahallesi", "slug": "adatepe"},
        {"_id": {"$oid": "692edd34a7b9834d54d6aa60"}, "name": "Tınaztepe Mahallesi", "slug": "tinaztepe"},
        {"_id": {"$oid": "692edd46a7b9834d54d6aa61"}, "name": "Efeler Mahallesi", "slug": "efeler"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0989"}, "name": "Yıldız Mahallesi", "slug": "yildiz"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0981"}, "name": "Şirinyer Mahallesi", "slug": "sirinyer"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0980"}, "name": "Buca Merkez", "slug": "merkez"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0986"}, "name": "Yenigün Mahallesi", "slug": "yenigun"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0987"}, "name": "Yeşilbağlar Mahallesi", "slug": "yesilbaglar"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0988"}, "name": "Yeşilçam Mahallesi", "slug": "yesilcam"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0999"}, "name": "Buca Koop Mahallesi", "slug": "buca-koop"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0998"}, "name": "Kozağaç Mahallesi", "slug": "kozagac"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0997"}, "name": "Kuruçeşme Mahallesi", "slug": "kurucesme"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0996"}, "name": "Menderes Mahallesi", "slug": "menderes"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0995"}, "name": "Yaylacık Mahallesi", "slug": "yaylacik"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0994"}, "name": "Yiğitler Mahallesi", "slug": "yigitler"},
    ]

# ... (Index sayfası aynı) ...
@router.get("/")
async def index_page(request: Request):
    listings = []
    error = None
    user_role = request.cookies.get("user_role")
    try:
        response = requests.get(API_URL)
        if response.status_code == 200: listings = response.json().get("data", [])
        else: error = "İlanlar getirilemedi"
    except Exception as e: error = f"API hatası: {e}"
    return templates.TemplateResponse("listings/index.html", {"request": request, "listings": listings, "error": error, "user_role": user_role})


# --- 2. İLAN VERME SAYFASI (CREATE GET - OPTİMİZE EDİLDİ) ---
@router.get("/create")
async def create_listing_page(request: Request):
    token = request.cookies.get("access_token")
    user_role = request.cookies.get("user_role")

    if not token: return RedirectResponse(url="/auth/login", status_code=303)
    if user_role != 'agent': return RedirectResponse(url="/listings", status_code=303)

    # Query parametrelerini (URL'den gelen) alıp bir sözlüğe (mutable) çevirelim
    prefill_data = dict(request.query_params)
    neighborhoods = load_neighborhoods() 

    # --- AKILLI KONUM EŞLEŞTİRME ---
    # Eğer URL'den "location_slug" geldiyse (buca-koop), bunu ID'ye çevirip "location" alanına atayalım
    incoming_slug = prefill_data.get("location_slug")
    if incoming_slug:
        for n in neighborhoods:
            # Basit bir string eşleşmesi (slug veya isim içinde arama)
            if incoming_slug.lower() in n.get("slug", "").lower() or incoming_slug.lower() in n["name"].lower():
                prefill_data["location"] = n["_id"]["$oid"]
                break
    
    return templates.TemplateResponse("listings/create.html", {
        "request": request,
        "prefill": prefill_data,
        "neighborhoods": neighborhoods
    })


# --- 3. İLAN KAYDETME (CREATE POST - OPTİMİZE EDİLDİ) ---
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
        heating_type: str = Form(...),
        # Yeni Alanlar (Zorunlu değil, opsiyonel alalım)
        bathroom_count: str = Form(None),
        furnishing: str = Form(None)
):
    token = request.cookies.get("access_token")
    user_role = request.cookies.get("user_role")

    if not token or user_role != 'agent':
        return RedirectResponse(url="/auth/login", status_code=303)

    decoded_token = decode_token(token)
    user_id = decoded_token.get("sub") or decoded_token.get("id") if decoded_token else None
    
    neighborhoods_data = load_neighborhoods()
    neighborhood_name = "Bilinmeyen Mahalle" 
    for n in neighborhoods_data:
        if n.get('_id', {}).get('$oid') == neighborhood_id:
            neighborhood_name = n.get('name', 'Bilinmeyen Mahalle')
            break
    
    # --- VERİ ZENGİNLEŞTİRME ---
    # Veritabanı şemasını değiştirmeden ek verileri Description'a gömüyoruz.
    final_description = description
    extras = []
    if bathroom_count: extras.append(f"Banyo Sayısı: {bathroom_count}")
    if furnishing: 
        tr_furnishing = "Eşyalı" if furnishing == "furnished" else "Eşyasız"
        extras.append(f"Eşya Durumu: {tr_furnishing}")
    
    if extras:
        final_description += "\n\n--- Ek Özellikler ---\n" + "\n".join(extras)

    headers = {"Authorization": token}
    payload = {
        "agency_id": user_id, 
        "title": title,
        "description": final_description, # Güncellenmiş açıklama
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
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 201:
            return RedirectResponse(url="/listings", status_code=303)
        else:
             # Hata durumunda verileri koruyarak formu geri dön
             # prefill sözlüğünü form verileriyle dolduruyoruz
             form_data = {
                 "title": title, "description": description, "price": price, "location": neighborhood_id,
                 "room_count": room_count, "net_area": net_area, "gross_area": gross_area,
                 "floor": floor, "building_age": building_age, "heating_type": heating_type,
                 "bathroom_count": bathroom_count, "furnishing": furnishing
             }
             return templates.TemplateResponse("listings/create.html", {
                "request": request, "prefill": form_data, "error": f"Hata: {response.text}", "neighborhoods": neighborhoods_data
            })
    except Exception:
        return templates.TemplateResponse("listings/create.html", {"request": request, "error": "Sunucu hatası"})

# ... (Geri kalan comment, detail kısımları aynı kalacak) ...
@router.post("/{id}/comment")
async def add_comment(request: Request, id: str, rating: int = Form(...), content: str = Form(...)):
    # ... (Önceki kodun aynısı) ...
    token = request.cookies.get("access_token")
    user_role = request.cookies.get("user_role")
    if not token or user_role != 'user':
        return RedirectResponse(url=f"/listings/{id}", status_code=303)
    decoded = decode_token(token)
    user_id = decoded.get("sub") or decoded.get("id")
    headers = {"Authorization": token}
    payload = {"listing_id": id, "user_id": user_id, "content": content, "rating": rating, "created_at": datetime.utcnow().isoformat() + "Z"}
    try:
        requests.post(COMMENTS_API_URL, json=payload, headers=headers)
    except: pass
    return RedirectResponse(url=f"/listings/{id}", status_code=303)

@router.get("/{id}")
async def listing_detail(request: Request, id: str):
    # ... (Önceki kodun aynısı, sadece format_date filtresi main.py'dan gelecek) ...
    token = request.cookies.get("access_token")
    if not token: return RedirectResponse(url="/auth/login", status_code=303)
    listing = None
    current_user_id = None
    user_role = request.cookies.get("user_role")
    if token:
        decoded = decode_token(token)
        if decoded: current_user_id = decoded.get("sub") or decoded.get("id")
    try:
        response = requests.get(f"{API_URL}/{id}")
        if response.status_code == 200:
            listing = response.json().get("data")
            listing["seller"] = {"name": "Satıcı Bilgisi Yok", "phone": "Numara Yok"}
            listing["seller_type"] = "unknown"
            listing["comments"] = []
            
            # (Basitlik için seller fetch kodunu koru)
            user_ref = listing.get("user")
            agency_ref = listing.get("agency_id")
            if agency_ref:
                try:
                    ar = requests.get(f"{AGENTS_API_URL}/{agency_ref}")
                    if ar.status_code==200: listing["seller"]=standardize_phone_data(ar.json()["data"]); listing["seller_type"]="agency"; listing["agency_id_str"]=agency_ref
                except: pass
            
            if "id" not in listing and "_id" in listing: listing["id"] = listing["_id"]["$oid"] if isinstance(listing["_id"], dict) else listing["_id"]

            try:
                c_resp = requests.get(f"{COMMENTS_API_URL}?listing_id={listing['id']}")
                if c_resp.status_code == 200: listing["comments"] = c_resp.json().get("data", [])
            except: pass
    except: pass
    if not listing: return RedirectResponse(url="/listings", status_code=303)
    return templates.TemplateResponse("listings/detail.html", {"request": request, "listing": listing, "user_role": user_role, "current_user_id": current_user_id})