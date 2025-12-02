from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import auth, listings, prediction

app = FastAPI()

# Statik dosyaları (CSS, Resimler) tanıtıyoruz
app.mount("/static", StaticFiles(directory="static"), name="static")

# Router'ları (Modülleri) ana uygulamaya bağlıyoruz
app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(prediction.router)

@app.get("/")
async def root():
    # Siteye giren kişiyi direkt İlanlara atıyoruz (İstersen Login'e atabilirsin)
    return RedirectResponse(url="/listings")