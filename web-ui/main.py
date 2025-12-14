from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from routers import auth, listings, prediction, chatbot

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(prediction.router)
app.include_router(chatbot.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/listings")