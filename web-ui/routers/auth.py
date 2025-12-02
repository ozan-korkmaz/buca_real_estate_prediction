from fastapi import APIRouter,Request,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/auth")
templates = Jinja2Templates(directory="templates")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html",{"request": request})

@router.post("/login")
async def login_action(request: Request, username: str = Form(...), password: str = Form(...)):
    #Normalde SOA'ya istek atılacak şimdilik dummy logic ile login
    if username == "admin" and password == "1234":
        return RedirectResponse(url="/listings", status_code=303)
    else:
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Kullanıcı adı veya şifre hatalı!"})
