from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers.auth import router as auth_router
from routers.listings import router as listings_router

app = FastAPI()

app.mount("/static",StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(listings_router)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("listings/index.html", {"request": request, "title":"Ana Sayfa"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)