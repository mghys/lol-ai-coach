from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
import uuid

from app.services.hero_recognizer import recognize_hero
from config import UPLOAD_DIR

app = FastAPI(title="英雄识别")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/hero-recognize")
async def recognize_hero_image(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"hero_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    results = recognize_hero(file_path)
    
    return {
        "success": True,
        "hero": results[0]["hero"] if results else None,
        "similarity": results[0]["similarity"] if results else 0
    }
