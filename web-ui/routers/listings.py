from fastapi import APIRouter,Request
from starlette.templating import Jinja2Templates

router = APIRouter(prefix="/listings")
templates = Jinja2Templates(directory="templates")

#Mock ilan verileri normalde Soa DB'den getirecek
fake_listings = [
    {"id": 1, "title": "Buca'da Satılık 3+1 Daire", "price": 3500000, "location": "Buca/Şirinyer"},
    {"id": 2, "title": "Dokuz Eylül Yanı 1+1", "price": 1200000, "location": "Buca/Tınaztepe"},
    {"id": 3, "title": "Hasanağa Bahçesi Manzaralı", "price": 4100000, "location": "Buca/Merkez"},
]

@router.get("/")
async def list_listings(request: Request):
    return templates.TemplateResponse("listings/index.html", {
        "request": request,
        "listings": fake_listings,
        "title": "İlanlar"
    })