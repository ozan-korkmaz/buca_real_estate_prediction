import requests
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json
import base64

router = APIRouter(prefix="/prediction", tags=["prediction"])
templates = Jinja2Templates(directory="templates")

API_URL = "http://localhost:5001/api/predict"

# --- YARDIMCI FONKSİYONLAR ---
def decode_token(token: str):
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
    except: return None

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

# --- SAYFA GÖSTERİMİ (GET) ---
@router.get("/estimate")
async def estimate_page(request: Request):
    token = request.cookies.get("access_token")
    decoded = decode_token(token)
    
    # Sadece agent girebilir onun kontrolü
    if not token or not decoded:
        return RedirectResponse(url="/auth/login", status_code=303)
    
    if decoded.get("role") != 'agent':
        return RedirectResponse(url="/listings?error=Yetkisiz_Erisim", status_code=303)
    
    return templates.TemplateResponse("prediction/form.html", {
        "request": request,
        "prefill": dict(request.query_params), 
        "neighborhoods": load_neighborhoods()  
    })

# --- TAHMİN SONUCU (POST) ---
@router.post("/estimate")
async def estimate_price_result(
        request: Request,
        location: str = Form(...),
        room_count: int = Form(...),
        hall_count: int = Form(1),
        bathroom_count: int = Form(1),
        net_area: float = Form(...),
        floor: int = Form(...),
        total_floors: int = Form(5),
        building_age: int = Form(...),
        heating_type: str = Form("Kombi"),
        furnishing: str = Form("unfurnished"),
        usage_status: str = Form("empty")
):
    token = request.cookies.get("access_token")
    decoded = decode_token(token)
    if not decoded or decoded.get("role") != 'agent':
         return RedirectResponse(url="/listings", status_code=303)

    # ML Servisine Gidecek Payload
    payload = {
        "room_count": room_count,
        "hall_count": hall_count,
        "net_area": net_area,
        "floor": floor,
        "total_floors": total_floors,
        "building_age": building_age,
        "bathroom_count": bathroom_count,
        "location": location,          
        "heating_type": heating_type,  
        "furnishing": furnishing,      
        "usage_status": usage_status   
    }

    estimated_price = None
    price_range = None
    error = None

    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json().get("data", {})
            estimated_price = data.get("predicted_price")
            price_range = data.get("price_range")
        else:
            error = f"API Hatası: {response.text}"
            print(error)
    except Exception as e:
        error = f"Sunucu Hatası: {e}"
        print(error)

    # Sonuç sayfasına detayları gönder
    return templates.TemplateResponse("prediction/result.html", {
        "request": request,
        "price": estimated_price,
        "range": price_range,
        "details": payload,
        "error": error
    })