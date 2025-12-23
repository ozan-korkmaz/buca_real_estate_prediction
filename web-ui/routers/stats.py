import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests
import json

API_BASE_URL = os.getenv("SOA_API_URL", "http://localhost:5001/api")

router = APIRouter(tags=["Stats"])
templates = Jinja2Templates(directory="templates")

def format_currency(value):
    try:
        return f"{int(value):,}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"
    except (TypeError, ValueError):
        return "N/A"

@router.get("/stats/street", response_class=HTMLResponse)
async def street_stats_page(request: Request):
    endpoint = f"{API_BASE_URL}/listings/stats/street"
    street_data = []
    error_message = None

    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status() 
        
        data = response.json()
        
        street_data = [
            {
                "street": stat["street"] if stat["street"] != 'Diğer/Belirtilmemiş' else format_currency("Diğer/Belirtilmemiş"),
                "averagePrice": format_currency(stat["averagePrice"]),
                "count": stat["count"]
            }
            for stat in data
        ]
        
    except requests.exceptions.RequestException as e:
        error_message = f"API'ye ulaşılamadı veya geçersiz yanıt: {endpoint}. Hata: {e}"
        print(f"API isteği başarısız: {error_message}")
        
    except Exception as e:
        error_message = f"Veri işlenirken beklenmedik hata oluştu: {type(e).__name__}: {str(e)}"
        print(f"DEBUG HATA (WebUI İşleme): {error_message}")
        
    return templates.TemplateResponse(
        "stats/street_stats.html",
        {
            "request": request,
            "street_data": street_data,
            "error": error_message,
            "title": "Mahalle/Sokak Fiyat Analizleri"
        }
    )