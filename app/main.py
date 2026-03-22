from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
import uuid

from app.services.hero_recognizer import recognize_hero
from app.services.ocr_service import process_screenshot
from app.services.general_ocr_service import recognize_general_text
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
        "similarity": results[0]["similarity"] if results else 0,
    }


@app.post("/game-result-recognize")
async def recognize_game_result(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"game_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    results = process_screenshot(file_path)

    return {
        "success": True,
        "win": results.get("win"),
        "ally_team": results.get("ally_team", []),
        "enemy_team": results.get("enemy_team", []),
        "detected_champions": results.get("detected_champions", []),
    }


@app.post("/pick-phase-recognize")
async def recognize_pick_phase(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"pick_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    from app.services.pick_phase_service import recognize_pick_phase_heroes

    results = recognize_pick_phase_heroes(file_path)

    return {
        "success": True,
        "available_heroes": results.get("available_heroes", []),
        "blue_side": results.get("blue_side", []),
    }


@app.post("/ocr-recognize")
async def recognize_text_from_image(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename or "")[1]
    filename = f"ocr_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    results = recognize_general_text(file_path)

    return results
