import requests
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from datetime import datetime
import json
import base64
import urllib.parse

router = APIRouter(prefix="/listings", tags=["listings"])
templates = Jinja2Templates(directory="templates")

# API URL Ayarları
API_URL = "http://localhost:5001/api/listings"
AGENTS_API_URL = "http://localhost:5001/api/agents"
COMMENTS_API_URL = "http://localhost:5001/api/comments"
USERS_API_URL = "http://localhost:5001/api/users"

# --- YARDIMCI FONKSİYONLAR ---
def decode_token(token: str):
    """Token'ı çözer ve payload'u döndürür."""
    try:
        if not token: return None
        if token.startswith("Bearer "):
            token = token[7:]
        parts = token.split('.')
        if len(parts) != 3: return None
        
        payload_base64 = parts[1] 
        padding = len(payload_base64) % 4
        if padding > 0: payload_base64 += '=' * (4 - padding)
            
        payload_bytes = base64.urlsafe_b64decode(payload_base64)
        return json.loads(payload_bytes.decode('utf-8'))
    except Exception as e:
        print(f"Token decode error: {e}")
        return None

def get_clean_id(obj_or_str):
    if not obj_or_str: return None
    if isinstance(obj_or_str, dict): return obj_or_str.get("$oid")
    return str(obj_or_str)

def get_auth_header(token: str):
    """Backend'in beklediği Bearer formatında header oluşturur."""
    if not token:
        return {}
    if token.startswith("Bearer "):
        return {"Authorization": token}
    return {"Authorization": f"Bearer {token}"}

def standardize_seller_data(data: dict, type: str) -> dict:
    standardized = {}
    if type == "agency":
        name = data.get("agency_name") or data.get("full_name") or data.get("name")
        standardized["name"] = name if name else "İsimsiz Emlak Ofisi"
    else:
        name = data.get("name") or data.get("full_name")
        standardized["name"] = name if name else "İsimsiz Kullanıcı"

    phone = data.get("phone") or data.get("phone_number") or data.get("mobile")
    standardized["phone"] = phone if (isinstance(phone, str) and phone.strip()) else "Numara Yok"
    return standardized

def load_neighborhoods():
    return [
        {"_id": {"$oid": "692edc7ba7b9834d54d6aa5c"}, "name": "Adatepe Mahallesi", "slug": "adatepe"},
        {"_id": {"$oid": "692edd34a7b9834d54d6aa60"}, "name": "Tınaztepe Mahallesi", "slug": "tinaztepe"},
        {"_id": {"$oid": "692edd46a7b9834d54d6aa61"}, "name": "Efeler Mahallesi", "slug": "efeler"},
        {"_id": {"$oid": "69301f30f9a575e1e6fb0967"}, "name": "Adatepe Mahallesi (Tekrar)"},
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

# --- 1. LİSTELEME (INDEX) ---
@router.get("/")
async def index_page(request: Request):
    listings = []
    error = None
    
    token = request.cookies.get("access_token")
    decoded = decode_token(token)
    user_role = decoded.get("role") if decoded else "guest"

    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            all_listings = response.json().get("data", [])
            
            # --- AGENT FİLTRELEME ---
            if user_role == 'agent' and decoded:
                my_agency_name = decoded.get("agency_name")
                my_user_id = decoded.get("sub") or decoded.get("id")
                
                filtered_listings = []
                for l in all_listings:
                    l_agency = l.get("agency_name")
                    l_owner_id = get_clean_id(l.get("agency_id"))
                    if not l_owner_id: l_owner_id = get_clean_id(l.get("user"))
                    
                    is_agency_match = (my_agency_name and l_agency and my_agency_name == l_agency)
                    is_owner_match = (my_user_id and l_owner_id and str(my_user_id) == str(l_owner_id))
                    
                    if is_agency_match or is_owner_match:
                        filtered_listings.append(l)
                listings = filtered_listings
            else:
                listings = all_listings
        else:
            error = "İlanlar getirilemedi"
    except Exception as e:
        error = f"API hatası: {e}"

    return templates.TemplateResponse("listings/index.html",{
        "request": request, "listings": listings, "error": error, "user_role": user_role
    })

# --- 2. İLAN OLUŞTURMA SAYFASI (CREATE GET) ---
@router.get("/create")
async def create_listing_page(request: Request):
    token = request.cookies.get("access_token")
    decoded = decode_token(token)
    
    if not token or not decoded: return RedirectResponse(url="/auth/login", status_code=303)
    
    user_role = decoded.get("role")
    if user_role != 'agent': 
        return RedirectResponse(url="/listings", status_code=303)

    return templates.TemplateResponse("listings/create.html", {
        "request": request,
        "prefill": dict(request.query_params),
        "neighborhoods": load_neighborhoods()
    })

# --- 3. İLAN KAYDETME (CREATE POST) [DÜZELTİLDİ: Bearer Token Eklendi] ---
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
        total_floors: str = Form(None), 
        hall_count: str = Form(None),
        usage_status: str = Form(None),
        bathroom_count: str = Form(None),
        furnishing: str = Form(None)
):
    token = request.cookies.get("access_token")
    decoded = decode_token(token)

    if not token or not decoded or decoded.get("role") != 'agent':
        return RedirectResponse(url="/auth/login", status_code=303)

    user_id = decoded.get("sub") or decoded.get("id")
    agency_name = decoded.get("agency_name")

    neighborhoods_data = load_neighborhoods()
    neighborhood_name = "Bilinmeyen Mahalle" 
    for n in neighborhoods_data:
        if n.get('_id', {}).get('$oid') == neighborhood_id:
            neighborhood_name = n.get('name')
            break
            
    final_description = description
    extras = []
    if total_floors: extras.append(f"Toplam Kat: {total_floors}")
    if hall_count: extras.append(f"Salon Sayısı: {hall_count}")
    if usage_status: 
        status_map = {"empty": "Boş", "owner": "Mülk Sahibi", "tenanted": "Kiracılı"}
        extras.append(f"Kullanım: {status_map.get(usage_status, usage_status)}")
    if furnishing: 
        furn_map = {"furnished": "Eşyalı", "unfurnished": "Eşyasız"}
        extras.append(f"Eşya: {furn_map.get(furnishing, furnishing)}")
    if bathroom_count: extras.append(f"Banyo: {bathroom_count}")
    
    if extras:
        final_description += "\n\n--- Diğer Özellikler ---\n" + "\n".join(extras)

    # --- DÜZELTME BURADA: Auth Header ---
    headers = get_auth_header(token)
    
    payload = {
        "agency_id": user_id, 
        "agency_name": agency_name,
        "title": title,
        "description": final_description,
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
             print(f"Kayıt Hatası: {response.text}")
             form_data = {
                 "title": title, "description": description, "price": price, "location": neighborhood_id,
                 "room_count": room_count, "net_area": net_area, "gross_area": gross_area,
                 "floor": floor, "building_age": building_age, "heating_type": heating_type,
                 "total_floors": total_floors, "hall_count": hall_count, 
                 "bathroom_count": bathroom_count, "furnishing": furnishing, "usage_status": usage_status
             }
             return templates.TemplateResponse("listings/create.html", {
                "request": request, 
                "prefill": form_data, 
                "error": f"Kayıt Başarısız: {response.text}", 
                "neighborhoods": neighborhoods_data
            })
    except Exception as e:
        print(f"Sunucu Hatası: {e}")
        return templates.TemplateResponse("listings/create.html", {
            "request": request, 
            "prefill": {},
            "error": f"Sunucu Hatası: {str(e)}",
            "neighborhoods": neighborhoods_data
        })

# --- 4. İLAN DETAY ---
@router.get("/{id}")
async def listing_detail(request: Request, id: str):
    token = request.cookies.get("access_token")
    decoded = decode_token(token)
    user_role = decoded.get("role") if decoded else "guest"
    
    listing = None
    try:
        response = requests.get(f"{API_URL}/{id}")
        if response.status_code == 200:
            listing = response.json().get("data")
            listing["id"] = get_clean_id(listing.get("_id")) or id

            listing["seller"] = {"name": "Satıcı Bilgisi Yok", "phone": "Numara Yok"}
            listing["seller_type"] = "unknown"
            
            agency_id_str = get_clean_id(listing.get("agency_id"))
            user_id_str = get_clean_id(listing.get("user"))

            if agency_id_str:
                try:
                    ar = requests.get(f"{AGENTS_API_URL}/{agency_id_str}")
                    if ar.status_code == 200:
                        listing["seller"] = standardize_seller_data(ar.json().get("data", {}), "agency")
                        listing["seller_type"] = "agency"
                except: pass
            
            if listing["seller_type"] == "unknown" and user_id_str:
                try:
                    ur = requests.get(f"{USERS_API_URL}/{user_id_str}")
                    if ur.status_code == 200:
                        listing["seller"] = standardize_seller_data(ur.json().get("data", {}), "user")
                        listing["seller_type"] = "user"
                except: pass

            listing["comments"] = [] 
            try:
                c_resp = requests.get(f"{COMMENTS_API_URL}?listing_id={listing['id']}")
                if c_resp.status_code == 200:
                    raw_comments = c_resp.json().get("data", [])
                    processed = []
                    for c in raw_comments:
                        u_data = c.get("user_id")
                        u_name = u_data.get("name", "Misafir") if isinstance(u_data, dict) else "Misafir"
                        processed.append({
                            "user": u_name,
                            "content": c.get("text", ""),
                            "rating": int(c.get("rating", 0)),
                            "date": c.get("created_at", "")[:10]
                        })
                    listing["comments"] = processed
            except: pass
    except: pass

    if not listing: return RedirectResponse(url="/listings", status_code=303)

    current_agency = decoded.get("agency_name") if decoded else None
    is_owner_agency = (user_role == 'agent' and current_agency and listing.get("agency_name") == current_agency)

    return templates.TemplateResponse("listings/detail.html", {
        "request": request, "listing": listing, "user_role": user_role, "is_owner_agency": is_owner_agency
    })

# --- 5. YORUM YAPMA ---
@router.post("/{id}/comment")
async def add_comment(request: Request, id: str, rating: int = Form(...), content: str = Form(...)):
    token = request.cookies.get("access_token")
    decoded = decode_token(token)
    if not decoded or decoded.get("role") != 'user':
        return RedirectResponse(url=f"/listings/{id}", status_code=303)

    # --- DÜZELTME BURADA: Auth Header ---
    headers = get_auth_header(token)
    
    payload = {"listing_id": id, "user_id": decoded.get("sub") or decoded.get("id"), "content": content, "rating": rating}
    try: requests.post(COMMENTS_API_URL, json=payload, headers=headers)
    except: pass
    return RedirectResponse(url=f"/listings/{id}", status_code=303)

# --- 6. İLAN DÜZENLEME SAYFASI (EDIT GET) ---
@router.get("/{id}/edit")
async def edit_listing_page(request: Request, id: str):
    token = request.cookies.get("access_token")
    decoded = decode_token(token)

    # 1. Giriş Kontrolü
    if not token or not decoded or decoded.get("role") != 'agent':
        return RedirectResponse(url=f"/listings/{id}", status_code=303)

    listing_data = {}
    error = None
    neighborhoods = load_neighborhoods()

    try:
        # İlan verisini çek
        response = requests.get(f"{API_URL}/{id}")
        if response.status_code == 200:
            data = response.json().get("data", {})
            
            # SADECE İLAN SAHİBİ DÜZENLEYEBİLİR
            current_agency = decoded.get("agency_name")
            listing_agency = data.get("agency_name")
            
            if current_agency != listing_agency:
                return RedirectResponse(url=f"/listings/{id}?error=Yetkisiz_Islem", status_code=303)

            # Veriyi form yapısına uydur (Mapping)
            # Description içindeki "--- Diğer Özellikler ---" kısmını temizleyebiliriz
            clean_desc = data.get("description", "").split("\n\n--- Diğer Özellikler ---")[0]

            listing_data = {
                "id": get_clean_id(data.get("_id")) or id,
                "title": data.get("title"),
                "description": clean_desc,
                "price": data.get("price"),
                "location": get_clean_id(data.get("neighborhood_id")), # Select box için ID lazım
                "room_count": data.get("property_specs", {}).get("room_count"),
                "net_area": data.get("property_specs", {}).get("net_m2"),
                "gross_area": data.get("property_specs", {}).get("gross_m2"),
                "floor": data.get("property_specs", {}).get("floor"),
                "building_age": data.get("property_specs", {}).get("building_age"),
                "heating_type": data.get("property_specs", {}).get("heating"),
                # Diğer alanlar opsiyonel, description içinde parse edilebilir ama şimdilik boş bırakıyoruz
                "total_floors": "", 
                "hall_count": "", 
                "bathroom_count": "",
                "furnishing": "",
                "usage_status": ""
            }
        else:
            error = "İlan bulunamadı."
    except Exception as e:
        error = f"Hata: {e}"

    return templates.TemplateResponse("listings/edit.html", {
        "request": request,
        "listing": listing_data,
        "neighborhoods": neighborhoods,
        "error": error
    })

# --- 7. İLAN GÜNCELLEME İŞLEMİ (EDIT POST) ---
@router.post("/{id}/edit")
async def edit_listing_submit(
        request: Request,
        id: str,
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
    if not token: return RedirectResponse(url="/auth/login", status_code=303)

    # Mahalle Adı
    neighborhoods_data = load_neighborhoods()
    neighborhood_name = "Bilinmeyen Mahalle"
    for n in neighborhoods_data:
        if n.get('_id', {}).get('$oid') == neighborhood_id:
            neighborhood_name = n.get('name')
            break

    # Headers (Bearer Token)
    headers = get_auth_header(token)

    payload = {
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
            "street_name": neighborhood_name
            # Koordinatları ellemiyoruz
        }
    }

    try:
        # PUT İsteği
        response = requests.put(f"{API_URL}/{id}", json=payload, headers=headers)
        
        if response.status_code == 200:
            return RedirectResponse(url=f"/listings/{id}", status_code=303)
        else:
            # Hata durumunda edit sayfasına geri dön
            print(f"Güncelleme Hatası: {response.text}")
            return templates.TemplateResponse("listings/edit.html", {
                "request": request,
                "listing": {**payload, "id": id, "location": neighborhood_id}, # Form verilerini koru
                "neighborhoods": neighborhoods_data,
                "error": f"Güncelleme Başarısız: {response.text}"
            })
    except Exception as e:
        print(f"Sunucu Hatası: {e}")
        return RedirectResponse(url=f"/listings/{id}?error=Sunucu_Hatasi", status_code=303)

# --- 8. İLAN SİLME İŞLEMİ (DELETE POST) ---
@router.post("/{id}/delete")
async def delete_listing(request: Request, id: str):
    token = request.cookies.get("access_token")
    if not token: return RedirectResponse(url="/auth/login", status_code=303)

    headers = get_auth_header(token)
    
    try:
        response = requests.delete(f"{API_URL}/{id}", headers=headers)
        if response.status_code == 200:
            return RedirectResponse(url="/listings?success=Silindi", status_code=303)
        else:
            print(f"Silme Hatası: {response.text}")
            return RedirectResponse(url=f"/listings/{id}?error=Silme_Basarisiz", status_code=303)
    except Exception as e:
        print(f"Silme Exception: {e}")
        return RedirectResponse(url=f"/listings/{id}?error=Sunucu_Hatasi", status_code=303)