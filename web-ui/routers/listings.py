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


# --- VARSAYIMSAL TOKEN ÇÖZÜMLEME FONKSİYONU ---
def decode_token(token: str):
    """Token'ı çözer ve payload'u döndürür. Hata durumunda None."""
    try:
        if token.startswith("Bearer "):
            token = token[7:]
            
        print(f"DEBUG: Token çözümleme başlatılıyor. Token: {token[:20]}...")
        
        parts = token.split('.')
        if len(parts) != 3:
            print("ERROR: Token yapısı geçersiz (header.payload.signature formatında değil).")
            return None
        
        payload_base64 = parts[1] 
        padding = len(payload_base64) % 4
        if padding > 0:
            payload_base64 += '=' * (4 - padding)
            
        import base64
        payload_bytes = base64.urlsafe_b64decode(payload_base64)
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        print(f"DEBUG: Token başarıyla çözüldü. Payload anahtarları: {list(payload.keys())}")
        return payload
    except Exception as e:
        print(f"ERROR: Token çözme sırasında beklenmeyen hata: {e}")
        return None

# --- MAHALLE VERİSİNİ OKUYAN YARDIMCI FONKSİYON ---
def load_neighborhoods():
    """Mahalle verilerini temsili JSON içeriğinden yükler."""
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
        print("DEBUG: /create sayfasına erişim, token bulunamadı. Giriş sayfasına yönlendiriliyor.")
        return RedirectResponse(url="/auth/login")

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
    if not token:
        print("DEBUG: İlan oluşturma denemesi, token bulunamadı. Giriş sayfasına yönlendiriliyor.")
        return RedirectResponse(url="/auth/login", status_code=303)

    decoded_token = decode_token(token)
    if not decoded_token:
        print("ERROR: Token çözülemedi veya geçersiz. Giriş sayfasına yönlendiriliyor.")
        return RedirectResponse(url="/auth/login", status_code=303)
    
    user_id = decoded_token.get("id") 
    
    if not user_id:
        print("ERROR: Token içinde User ID ('id') alanı bulunamadı.")
        return RedirectResponse(url="/auth/login?error=InvalidTokenID", status_code=303)

    # --- SUNUCU TARAFI DOĞRULAMASI (Önceki adımdan korundu) ---
    neighborhoods_data = load_neighborhoods()
    if not neighborhood_id:
        error_message = "Mahalle seçimi zorunludur. Lütfen bir mahalle seçin."
        
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
    # -----------------------------------------------------------
    
    # --- MAHALLE ADINI ID'DEN BULMA İŞLEMİ ---
    neighborhood_name = "Bilinmeyen Mahalle" 
    
    for n in neighborhoods_data:
        # MongoDB $oid formatına göre ID'yi kontrol ediyoruz.
        if n.get('_id', {}).get('$oid') == neighborhood_id:
            neighborhood_name = n.get('name', 'Bilinmeyen Mahalle')
            break
            
    print(f"DEBUG: Seçilen Mahalle ID: {neighborhood_id}, Adı: {neighborhood_name}")
    # ------------------------------------------

    current_time_utc_iso = datetime.utcnow().isoformat() + "Z"
    
    headers = {"Authorization": token}
    payload = {
        "agency_id": user_id, 
        "title": title,
        "description": description,
        "price": price,
        "neighborhood_id": neighborhood_id, # Mahalle ID'si API'ye hala gitmeli
        "property_specs": {
            "room_count": room_count,
            "net_m2": net_area,
            "gross_m2": gross_area,
            "floor": floor,
            "heating": heating_type,
            "building_age": building_age 
        },
        "location_details": {
            "street_name": neighborhood_name, # <-- DÜZELTME: Mahalle adı buraya eklendi!
            "coordinates": {"lat": 0, "lon": 0}
        },
        "created_at": current_time_utc_iso
    }
    
    print(f"DEBUG: Final API Payload (partial): agency_id={payload['agency_id']}, street_name={payload['location_details']['street_name']}")

    # ... (kalan API isteği ve hata kontrolü aynı kalır)
    # ...
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 201:
            print("DEBUG: İlan başarıyla oluşturuldu (201).")
            return RedirectResponse(url="/listings", status_code=303)
        else:
            # Hata durumunda da mahalleleri tekrar yüklemeliyiz
            error_response_text = response.text
            print(f"ERROR: API İlan oluşturma hatası. Status: {response.status_code}, Yanıt: {error_response_text}")
            
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
                
            error_message = f"İlan eklenemedi. API Hatası: {response.status_code}. Detay: {error_detail}"
            
            # neighborhoods_data zaten yukarıda tanımlı
            
            return templates.TemplateResponse("listings/create.html", {
                "request": request, 
                "prefill": prefill_data, 
                "error": error_message,
                "neighborhoods": neighborhoods_data # <-- Burada neighborhoods_data kullanılıyor
            })
    except Exception as e:
        print(f"ERROR: İstek gönderme sırasında Exception: {e}")
        return templates.TemplateResponse("listings/create.html", {"request": request, "error": "Sunucuya bağlantı hatası"})
    

# --- YARDIMCI FONKSİYON: DÖNEN VERİDE TELEFON KONTROLÜ VE STANDARTLAŞTIRMA ---
def standardize_phone_data(data: dict) -> dict:
    phone_number = data.get("phone")
    # Numara yoksa, None ise veya boş bir string ise standart bir hata mesajı ata
    if not isinstance(phone_number, str) or not phone_number.strip():
        data["phone"] = "Numara Yok (API Sorunu)"
    return data

# --- 4. İLAN DETAY (DETAIL) ---
@router.get("/{id}")
async def listing_detail(request: Request, id: str):
    listing = None
    
    try:
        # 1. Listing verisini çek
        response = requests.get(f"{API_URL}/{id}")
        
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="İlan bulunamadı.")
        
        if response.status_code == 200:
            listing = response.json().get("data")
            
            # Başlangıç/Varsayılan değerleri ayarla
            listing["seller"] = {"name": "Satıcı Bilgisi Yok", "phone": "Numara Yok"}
            listing["seller_type"] = "unknown"
            listing["comments"] = [] 

            # --- 2. Agent/User verisini çekme (Öncelikli Kontrol Mantığı) ---
            seller_found = False
            
            # 2a. User ID Kontrolü (İlan doğrudan kullanıcıya aitse öncelik ver)
            user_ref = listing.get("user")
            
            if user_ref:
                user_ref_id = user_ref.get("$oid") if isinstance(user_ref, dict) else user_ref
                
                if user_ref_id:
                    try:
                        print(f"DEBUG: Öncelikli User ID ile bilgi çekiliyor: {user_ref_id}")
                        user_response = requests.get(f"{USERS_API_URL}/{user_ref_id}")
                        if user_response.status_code == 200:
                            user_data = user_response.json().get("data", {})
                            
                            # **YENİ DEBUG:** Ham veride phone alanının tipini ve değerini kontrol et
                            phone_value = user_data.get('phone')
                            print(f"DEBUG: Ham User Data Phone Type: {type(phone_value)}, Value: {phone_value}")
                            
                            user_data = standardize_phone_data(user_data) # Telefonu standartlaştır
                            
                            listing["seller"] = user_data 
                            listing["seller_type"] = "user"
                            seller_found = True
                            print(f"DEBUG: User bulundu. İletişim: {user_data.get('phone')}")
                            
                        else:
                            print(f"DEBUG: User API status {user_response.status_code}. User ID çözümlenemedi.")
                    except requests.exceptions.RequestException as e:
                        print(f"ERROR: User API bağlantı hatası (öncelikli kontrol): {e}")

            # 2b. Agency ID Kontrolü (Eğer User bilgisi bulunamadıysa)
            if not seller_found and "agency_id" in listing:
                agency_id_obj = listing["agency_id"]
                agency_ref_id = agency_id_obj.get("$oid") if isinstance(agency_id_obj, dict) else agency_id_obj
                
                if agency_ref_id:
                    try:
                        print(f"DEBUG: Agency ID ile bilgi çekiliyor: {agency_ref_id}")
                        agent_response = requests.get(f"{AGENTS_API_URL}/{agency_ref_id}")
                        if agent_response.status_code == 200:
                            agent_data = agent_response.json().get("data", {})
                            agent_data = standardize_phone_data(agent_data) # Telefonu standartlaştır
                            
                            listing["seller"] = agent_data 
                            listing["seller_type"] = "agency"
                            seller_found = True
                            print(f"DEBUG: Agency bulundu. İletişim: {agent_data.get('phone')}")

                        else:
                            print(f"DEBUG: Agency API status {agent_response.status_code}. Agent ID çözümlenemedi. User ID olarak deneniyor.")
                            # Agent bulunamazsa, aynı ID'nin bir User olma ihtimaline karşı tekrar dene
                            try:
                                user_response = requests.get(f"{USERS_API_URL}/{agency_ref_id}")
                                if user_response.status_code == 200:
                                    user_data = user_response.json().get("data", {})
                                    user_data = standardize_phone_data(user_data) # Telefonu standartlaştır
                                    
                                    listing["seller"] = user_data
                                    listing["seller_type"] = "user"
                                    seller_found = True
                                    print(f"DEBUG: Agent ID'si User olarak çözüldü. İletişim: {user_data.get('phone')}")
                                else:
                                    print(f"DEBUG: ID hem Agent hem de User olarak çözümlenemedi.")
                            except requests.exceptions.RequestException:
                                pass
                    except requests.exceptions.RequestException as e:
                        print(f"ERROR: Agency API bağlantı hatası: {e}. User API'ye düşülüyor.")
                        # Bağlantı hatası durumunda User API'yi yedek olarak dene
                        try:
                            user_response = requests.get(f"{USERS_API_URL}/{agency_ref_id}")
                            if user_response.status_code == 200:
                                user_data = user_response.json().get("data", {})
                                user_data = standardize_phone_data(user_data) # Telefonu standartlaştır
                                
                                listing["seller"] = user_data
                                listing["seller_type"] = "user"
                                seller_found = True
                            else:
                                print(f"DEBUG: Agency ID (API hatası sonrası) User olarak da çözümlenemedi.")
                        except requests.exceptions.RequestException:
                            pass
            
            # 3. Yorum verisini çekme (Kalan kısım aynı)
            listing_id_obj = listing["_id"] if "_id" in listing else listing.get("id")
            listing_id = listing_id_obj.get("$oid") if isinstance(listing_id_obj, dict) else listing_id_obj

            if listing_id:
                try:
                    print(f"DEBUG: Yorumlar çekiliyor. Listing ID: {listing_id}")
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
                        print(f"DEBUG: Toplam {len(processed_comments)} yorum çekildi.")
                        
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